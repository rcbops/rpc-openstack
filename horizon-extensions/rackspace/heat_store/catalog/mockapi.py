class _Namespace(object):
    def __init__(self, adict):
        self.__dict__.update(adict)


class api:
    class glance:
        @staticmethod
        def image_list_detailed(request):
            images = [
                {'name': 'ubuntu', 'id': '1111-1111-1111'},
                {'name': 'fedora', 'id': '2222-2222-2222'},
                {'name': 'centos', 'id': '3333-3333-3333'},
            ]
            return ([_Namespace(i) for i in images], False, False)

    class nova:
        @staticmethod
        def flavor_list(request):
            flavors = [
                {'name': 'm1.tiny', 'id': '111-111'},
                {'name': 'm1.small', 'id': '222-222'},
                {'name': 'm1.large', 'id': '333-333'},
            ]
            return [_Namespace(f) for f in flavors]

        @staticmethod
        def keypair_list(request):
            keypairs = [
                {'name': 'first_keypair', 'id': '1111-1111'},
                {'name': 'second_keypair', 'id': '2222-2222'},
                {'name': 'third_keypair', 'id': '3333-3333'},
            ]
            return [_Namespace(k) for k in keypairs]

    class neutron:
        @staticmethod
        def network_list(request, **args):
            networks = [
                {'name': 'first_network', 'id': '11'},
                {'name': 'second_network', 'id': '22'},
                {'name': 'third_network', 'id': '33'},
            ]
            return [_Namespace(n) for n in networks]
