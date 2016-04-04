DASHBOARD = 'rackspace'

ADD_INSTALLED_APPS = [
    'rackspace',
]

ADD_ANGULAR_MODULES = ['horizon.dashboard.rackspace']

# Have Horizon find all the static files here when adding links to
# the base page template.
AUTO_DISCOVER_STATIC_FILES = True

# If set to True, this dashboard will not be added to the settings.
DISABLED = False
