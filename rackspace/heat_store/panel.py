import horizon

from rackspace import dashboard


class HeatStorePanel(horizon.Panel):
    name = 'Heat Templates'
    slug = 'heat_store'


dashboard.RackspaceDashboard.register(HeatStorePanel)
