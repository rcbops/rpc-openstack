import os
import hashlib
import re
import uuid
import yaml
from six.moves.urllib.parse import urlparse, urlunparse
import six.moves.urllib.request as urlrequest
from markdown import Markdown
from markdown.inlinepatterns import ImagePattern, ImageReferencePattern, \
    IMAGE_LINK_RE, IMAGE_REFERENCE_RE
try:
    from openstack_dashboard import api
except:
    api = None


class _RebasedImageLinkPattern(ImagePattern):
    """This class adds a base URL to any relative image links seen by the
    markdown parser."""
    def __init__(self, base_url, *args, **kwargs):
        self.base_url = base_url
        super(_RebasedImageLinkPattern, self).__init__(*args, **kwargs)

    def sanitize_url(self, url):
        url_parts = urlparse(url)
        if url_parts.scheme == '':
            url = os.path.join(self.base_url, url)
        return super(_RebasedImageLinkPattern, self).sanitize_url(url)


class _RebasedImageRefPattern(ImageReferencePattern):
    """This class adds a base URL to any relative image references seen by the
    markdown parser."""
    def __init__(self, base_url, *args, **kwargs):
        self.base_url = base_url
        super(_RebasedImageRefPattern, self).__init__(*args, **kwargs)

    def sanitize_url(self, url):
        url_parts = urlparse(url)
        if url_parts.scheme == '':
            url = os.path.join(self.base_url, url)
        return super(_RebasedImageRefPattern, self).sanitize_url(url)


class Solution(object):
    """This class holds a solution (heat template plus metadata for it).

    :param info_yaml: URL or filename to the solution's info.yaml file.
    :raises IOError: File not found.
            URLError: Remote file not found.
    """
    def __init__(self, info_yaml, basedir=''):
        """Import the solution's info.yaml file."""
        f, url_parts = self._open(info_yaml, basedir)
        solution_yaml = f.read().decode('utf-8')
        self.basedir = urlunparse((url_parts.scheme, url_parts.netloc,
                                   os.path.dirname(url_parts.path),
                                   None, None, None))

        # create a markdown converter and modify it to rebase image links
        markdown = Markdown()
        markdown.inlinePatterns['image_link'] = _RebasedImageLinkPattern(
            self.basedir, IMAGE_LINK_RE, markdown)
        markdown.inlinePatterns['image_reference'] = _RebasedImageRefPattern(
            self.basedir, IMAGE_REFERENCE_RE, markdown)

        # import the solution's metadata
        info = yaml.load(solution_yaml)
        self.id = hashlib.md5(solution_yaml).hexdigest()
        self.title = info['title']
        self.logo = info['logo']
        self.short_description = info['short_description']
        self.template_version = info['template_version']
        self.highlights = info.get('highlights', [])
        self.links = info.get('links', [])
        self.heat_template = info['heat_template']
        self.env_file = info.get('env_file')  # environments are optional
        desc_url = info['long_description']

        # read the markdown description
        f, url_parts = self._open(desc_url, self.basedir)
        self.long_description = markdown.convert(f.read().decode('utf-8'))

        # initialize parameters
        self.parameter_types = []

    def get_parameter_types(self, request):
        """Return the parameter list for this solution."""
        if self.parameter_types:
            return self.parameter_types

        # import heat template to obtain its parameters
        f, url_parts = self._open(self.heat_template, self.basedir)
        template = yaml.load(f.read().decode('utf-8'))
        params_in_order = []
        if template.get('parameter_groups'):
            for pgroup in template.get('parameter_groups'):
                for param in pgroup.get('parameters', []):
                    params_in_order.append(param)
        params = template.get('parameters')
        if not params_in_order:
            params_in_order = params.keys()
        if params_in_order:
            for name in params_in_order:
                param = params[name]

                # there are a few commonly used string parameters such as
                # flavors, images, keynames, etc. that we want to present as
                # dropdowns, so we change them to a more appropriate type here
                param_type = param['type']
                param_constraints = param.get('constraints', [])
                param_default = param.get('default')
                param_mapping = None
                if param_type == 'string' and param_constraints == []:
                    if name.endswith('flavor'):
                        flavors = api.nova.flavor_list(request)
                        param_type = 'comma_delimited_list'
                        param_constraints = [
                            {'allowed_values': [flavor.name
                                                for flavor in flavors]}
                        ]
                        if flavors and not param_default:
                            param_default = flavors[0].name
                    elif name.endswith('image'):
                        images, more, prev = \
                            api.glance.image_list_detailed(request)
                        param_type = 'comma_delimited_list'
                        param_constraints = [
                            {'allowed_values': [image.name
                                                for image in images]}
                        ]
                        if images and not param_default:
                            param_default = images[0].name
                    elif name.endswith('keyname'):
                        keypairs = api.nova.keypair_list(request)
                        param_type = 'comma_delimited_list'
                        param_constraints = [
                            {'allowed_values': [keypair.name
                                                for keypair in keypairs]}
                        ]
                        if keypairs and not param_default:
                            param_default = keypairs[0].name
                    elif name == 'floating-network-id':
                        networks = api.neutron.network_list(
                            request, **{'router:external': True})
                        param_type = 'comma_delimited_list'
                        param_constraints = [
                            {'allowed_values': [network.name
                                                for network in networks]}
                        ]
                        if networks and not param_default:
                            param_default = networks[0].name
                        param_mapping = {}
                        for network in networks:
                            param_mapping[network.name] = network.id

                p = {
                    'name': name,
                    'type': param_type,
                    'constraints': param_constraints,
                    'label': param['label'],
                    'description': param.get('description'),
                    'default': param_default
                }
                if param_mapping:
                    p['_mapping'] = param_mapping
                self.parameter_types.append(p)
        return self.parameter_types

    def map_parameter(self, param, value):
        """Map the value provided by the user to the value needed by Heat."""
        if '_mapping' not in param:
            return value
        return param['_mapping'].get(value, value)

    def launch(self, request, params={}):
        """Launch the solution's heat template."""
        if not api or not api.heat:
            raise RuntimeError('Heat API is not available.')

        fields = {
            'stack_name': (re.sub('[\W\d]+', '_', self.title.strip()) +
                           '_' + str(uuid.uuid4())),
            'timeout_mins': 60,
            'disable_rollback': False,
            'parameters': params,
            'template_url': self.heat_template,
            'environment': self._get_environment_data()  # can't use URL here
        }
        api.heat.stack_create(request, **fields)

    def _open(self, file_or_url, basedir=''):
        """Open a local or remote file.

        :param file_or_url: The filename or remote URL to open.
        :param basedir: The path or URL to prepend when `file_or_url` is
                        relative.
        :returns a tuple with the file handle and the urlparsed filename.
        """
        url_parts = urlparse(file_or_url)
        if url_parts.scheme == '' and not os.path.isabs(url_parts.path):
            file_or_url = os.path.join(basedir, file_or_url)
            url_parts = urlparse(file_or_url)
        if url_parts.scheme == '':
            f = open(file_or_url)
        else:
            f = urlrequest.urlopen(file_or_url)
        return f, url_parts

    def _get_environment_data(self):
        """Return the contents of the heat environment file (if provided).

        This is necessary because the heat API does not accept a URL for
        this parameter.
        """
        if not self.env_file:
            return None
        f = urlrequest.urlopen(self.env_file)
        return f.read().decode('utf-8')


class Catalog(object):
    """This class holds a collection of solutions, imported from yaml
    catalogs.

    :param args: one or more catalog filenames. Each filename must be a local
                 yaml file containing a list of solution URLs. Each solution
                 URL must point at the info.yaml file for the solution.
    """
    def __init__(self, *args):
        self.solutions = []
        for catalog in args:
            solutions = yaml.load(open(catalog).read())
            basedir = os.path.abspath(os.path.dirname(catalog))
            if solutions and len(solutions) > 0:
                for solution_url in solutions:
                    self.solutions.append(Solution(solution_url, basedir))

    def __iter__(self):
        return iter(self.solutions)

    def find_by_id(self, template_id):
        for template in self:
            if template.id == template_id:
                return template
