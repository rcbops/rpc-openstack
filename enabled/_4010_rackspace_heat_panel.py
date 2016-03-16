# The slug of the panel to be added to HORIZON_CONFIG. Required.
PANEL = 'heat_store'
# The slug of the dashboard the PANEL associated with. Required.
PANEL_GROUP = 'rackspace_private_cloud'
# The slug of the panel group the PANEL is associated with.
PANEL_DASHBOARD = 'rackspace'

# Python panel class of the PANEL to be added.
ADD_PANEL = 'rackspace.heat_store.panel.HeatStorePanel'

ADD_ANGULAR_MODULES = ['horizon.dashboard.rackspace']

DISABLED=False
