import os
import hashlib
import re
import uuid
import threading
import time
import yaml
from six.moves.urllib.parse import urlparse, urlunparse
import six.moves.urllib.request as urlrequest
from markdown import Markdown
from markdown.inlinepatterns import ImagePattern, ImageReferencePattern, \
    IMAGE_LINK_RE, IMAGE_REFERENCE_RE
try:
    from openstack_dashboard import api
except:
    from mockapi import api  # used for unit tests
#from mockapi import api


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
        self.id = hashlib.md5(solution_yaml.encode('utf-8')).hexdigest()
        self.title = info['name']
        self.release = str(info['release'])
        if 'logo' in info:
            self.logo = self._make_absolute_path(info.get('logo'),
                                                 self.basedir)[0]
        # in all the following fields, newlines are suppressed because they
        # are not rendered properly in Javascript strings by Django
        self.short_description = \
            markdown.convert(info['short_desc']).replace('\n', '')
        self.long_description = \
            markdown.convert(info['long_desc']).replace('\n', '')
        self.architecture = \
            markdown.convert(info['architecture']).replace('\n', '')
        self.design_specs = info.get('design_specs', [])
        self.heat_template = info['heat_template']
        self.env_file = info.get('env_file')  # environments are optional

    def get_parameter_types(self, request):
        """Return the parameter list for this solution."""
        parameter_types = []

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
                    if 'flavor' in name:
                        flavors = api.nova.flavor_list(request)
                        param_type = 'comma_delimited_list'
                        param_constraints = [
                            {'allowed_values': [flavor.name
                                                for flavor in flavors]}
                        ]
                        if flavors and not param_default:
                            param_default = flavors[0].name
                    elif 'image' in name:
                        images, more, prev = \
                            api.glance.image_list_detailed(request)
                        param_type = 'comma_delimited_list'
                        param_constraints = [
                            {'allowed_values': [image.name
                                                for image in images]}
                        ]
                        if images and not param_default:
                            param_default = images[0].name
                    elif 'keyname' in name:
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
                    elif 'network' in name:
                        networks = api.neutron.network_list(
                            request, **{'router:external': False})
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
                    'label': param['label'] if 'label' in param else name,
                    'description': param.get('description'),
                    'default': param_default
                }
                if param_mapping:
                    p['_mapping'] = param_mapping
                parameter_types.append(p)
        return parameter_types

    def map_parameter(self, parameter_types, name, value):
        """Map the value provided by the user to the value needed by Heat."""
        param = next((p for p in parameter_types if p['name'] == name), None)
        if param is None or '_mapping' not in param:
            return value
        return param['_mapping'].get(value, value)

    def launch(self, request, params={}):
        """Launch the solution's heat template."""
        if not api or not api.heat:
            raise RuntimeError('Heat API is not available.')

        parameter_types = self.get_parameter_types(request)
        mapped_params = dict(
            (name, self.map_parameter(parameter_types, name, value))
            for (name, value) in params.items())

        fields = {
            'stack_name': (re.sub('[\W\d]+', '_', self.title.strip()) +
                           '_' + str(uuid.uuid4())),
            'timeout_mins': 60,
            'disable_rollback': True,
            'parameters': mapped_params,
            'template_url': self._make_absolute_path(self.heat_template,
                                                     self.basedir)[0],
            'environment': self._get_environment_data()  # can't use URL here
        }
        api.heat.stack_create(request, **fields)
        return True

    def _make_absolute_path(self, file_or_url, basedir=''):
        """Return an absolute file or URL.

        :param file_or_url: The filename or remote URL. If already absolute, it
                            is returned untouched.
        :param basedir: The path or URL to prepend when `file_or_url` is
                        relative.
        :returns a tuple with the absolute path or URL and the urlparse
                 components that define it.
        """
        url_parts = urlparse(file_or_url)
        if url_parts.scheme == '' and not os.path.isabs(url_parts.path):
            file_or_url = os.path.join(basedir, file_or_url)
            url_parts = urlparse(file_or_url)
        return file_or_url, url_parts

    def _open(self, file_or_url, basedir=''):
        """Open a local or remote file.

        :param file_or_url: The filename or remote URL to open.
        :param basedir: The path or URL to prepend when `file_or_url` is
                        relative.
        :returns a tuple with the file handle and the urlparsed filename.
        """
        file_or_url, url_parts = self._make_absolute_path(file_or_url, basedir)
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
        f, url_parts = self._open(self.env_file, self.basedir)
        return f.read().decode('utf-8')


class Catalog(object):
    """This class holds a collection of solutions, imported from yaml
    catalogs.

    :param args: one or more catalog filenames. Each filename must be a local
                 yaml file containing a list of solution URLs. Each solution
                 URL must point at the info.yaml file for the solution.
    """
    cache = {}

    def __init__(self, *args):
        self.solutions = []
        for catalog in args:
            if catalog in self.cache:
                if self.cache[catalog]['mtime'] != os.stat(catalog).st_mtime:
                    # catalog was updated
                    del self.cache[catalog]
                elif self.cache[catalog]['atime'] + 3600 < time.time():
                    # one hour without being used, discard cached copy
                    del self.cache[catalog]
            if catalog in self.cache:
                self.solutions += self.cache[catalog]['solutions']
                self.cache[catalog]['atime'] = time.time()
            else:
                solutions = yaml.load(open(catalog).read())
                basedir = os.path.abspath(os.path.dirname(catalog))
                if solutions and len(solutions) > 0:
                    self.cache[catalog] = {'mtime': os.stat(catalog).st_mtime,
                                           'atime': time.time(),
                                           'solutions': []}

                    def read_solution(url):
                        solution = Solution(url, basedir)
                        self.cache[catalog]['solutions'].append(solution)
                        self.solutions.append(solution)

                    threads = [threading.Thread(target=read_solution,
                                                args=[url])
                               for url in solutions]
                    for t in threads:
                        t.start()
                    for t in threads:
                        t.join()

    def __iter__(self):
        return iter(self.solutions)

    def find_by_id(self, template_id):
        for template in self:
            if template.id == template_id:
                return template
