import horizon

from rackspace import dashboard


class HeatStorePanel(horizon.Panel):
    name = 'Solutions'
    slug = 'heat_store'


dashboard.RackspaceDashboard.register(HeatStorePanel)
