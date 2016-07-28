from horizon import tables


class TemplateTable(tables.DataTable):
    name = tables.Column('template', sortable=False,)

    class Meta:
        name = 'template'
        template = 'rackspace/heat_store/_template_table.html'
        multi_select = False

    def get_rows(self):
        return [self._meta.row_class(self, self.data.short_description)]

    def get_object_id(self, datum):
        return self.data.title
