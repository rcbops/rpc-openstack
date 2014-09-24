from horizon import tables

templates = object()


class MoreInfoLink(tables.LinkAction):
    name = 'more-info'
    verbose_name = 'Installation and More Information'
    # url = 'rackspace:heat_store:info'
    classes = ('ajax-modal',)
    ajax = True

    def __init__(self, attrs=None, **kwargs):
        kwargs['preempt'] = True
        super(MoreInfoLink, self).__init__(attrs, **kwargs)

    def get_link_url(self):
        return '#{0}'.format(self.table.data.title.lower())


class TemplateRow(tables.Row):
    ajax = True


class TemplateTable(tables.DataTable):
    name = tables.Column('template', sortable=False,)

    class Meta:
        name = 'template'
        template = 'rackspace/heat_store/_template_table.html'
        multi_select = False
        row_class = TemplateRow
        table_actions = (MoreInfoLink,)

    def get_rows(self):
        return [self._meta.row_class(self, self.data.short_description)]

    def get_object_id(self, datum):
        return self.data.title
