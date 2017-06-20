#! /usr/bin/env python
from argparse import ArgumentParser
from datetime import datetime, timedelta
from ipaddress import IPv4Network
from itertools import chain, izip, repeat, islice
from json import dumps
import os
from time import sleep

from keystoneauth1.identity import v3
from keystoneauth1 import session as session_
from cinderclient import client as cinder_client
from glanceclient import client as glance_client
from neutronclient.v2_0 import client as neutron_client
from novaclient import client as nova_client

CLIENT_VERSION = "2"


def get_conf():
    parser = ArgumentParser()
    parser.add_argument("--servers", type=int, default=1)
    parser.add_argument("--volumes", type=int, default=0)
    parser.add_argument("--networks", type=int, default=1)
    parser.add_argument("--infinite-quotas", action="store_true")
    args = parser.parse_args()
    if args.servers > args.networks:
        raise ValueError(
            "Each server must have at least one network and so the number of "
            "networks must be greater than or equal to the number of servers."
        )
    if args.servers < 1:
        raise ValueError(
            "The minimum number of servers that can be created is 1."
        )

    conf = {
        "auth": {},
        "infinite_quotas": args.infinite_quotas,
        "resources": {},
    }
    conf["auth"]["endpoint_type"] = os.environ["OS_ENDPOINT_TYPE"]
    conf["auth"]["username"] = os.environ["OS_USERNAME"]
    conf["auth"]["password"] = os.environ["OS_PASSWORD"]
    conf["auth"]["project_name"] = os.environ["OS_PROJECT_NAME"]
    conf["auth"]["auth_url"] = os.environ["OS_AUTH_URL"]
    conf["auth"]["user_domain_id"] = os.environ["OS_USER_DOMAIN_NAME"]
    conf["auth"]["project_domain_id"] = os.environ["OS_PROJECT_DOMAIN_NAME"]

    conf["resources"]["servers"] = {
        "count": args.servers,
        "flavor": "m1.tiny",
        "image": "cirros",
    }
    conf["resources"]["volumes"] = {
        "count": args.volumes,
        "size": 1,
    }
    conf["resources"]["networks"] = {
        "count": args.networks,
        "external_gateway_network": "public",
    }
    return conf


def _get_session(conf):
    auth = v3.Password(
        auth_url=conf["auth_url"],
        username=conf["username"],
        password=conf["password"],
        project_name=conf["project_name"],
        user_domain_id=conf["user_domain_id"],
        project_domain_id=conf["project_domain_id"],
    )

    return session_.Session(auth=auth, verify=True)


def session_caching_wrapper():
    cached = {}

    def get_session():
        if not cached.get("session"):
            conf = get_conf()
            cached["session"] = _get_session(conf["auth"])
        return cached["session"]
    return get_session


get_session = session_caching_wrapper()


def get_flavor_id_from_name(name):
    nova = nova_client.Client(CLIENT_VERSION, session=get_session())
    flavors = [
        flavor for flavor in nova.flavors.list() if flavor.name == name
    ]
    if len(flavors) > 1:
        raise Exception("Flavor name, '{}', is not unique.".format(name))
    try:
        return flavors[0].id
    except IndexError:
        raise Exception("No flavor with name '{}' exists.".format(name))


def get_network_id_from_name(name):
    neutron = neutron_client.Client(session=get_session())
    networks_ = neutron.list_networks(name=name)
    networks = networks_["networks"]
    if len(networks) > 1:
        raise Exception("Network name, '{}', is not unique.".format(name))
    try:
        return networks[0]["id"]
    except IndexError:
        raise Exception("No network with name '{}' exists.".format(name))


def get_image_id_from_name(name):
    glance = glance_client.Client(CLIENT_VERSION, session=get_session())
    images = list(glance.images.list(name=name))
    if len(images) > 1:
        raise Exception("Image name, '{}', is not unique.".format(name))
    try:
        return images[0].id
    except IndexError:
        raise Exception("No image with name '{}' exists.".format(name))


def verify_active(building, timeout=600):
    nova = nova_client.Client(CLIENT_VERSION, session=get_session())
    active = []
    delay = 10
    timeout_ = datetime.utcnow() + timedelta(seconds=timeout)
    while building:
        if datetime.utcnow() < timeout_:
            sleep(delay)
        else:
            raise Exception(
                "{} servers failed to build within {} seconds.".format(
                    len(building),
                    timeout,
                )
            )

        still_building = []
        for server in building:
            server = nova.servers.get(server.id)
            if server.status == "ACTIVE":
                active.append(server)
            elif server.status == "BUILD":
                still_building.append(server)
            else:
                raise Exception(
                    "The resource {} is in an invalid state.".format(
                        server.id
                    )
                )
        building = still_building
    return active


def make_networks(conf):
    neutron = neutron_client.Client(session=get_session())
    net = IPv4Network(u'10.0.0.0/8')
    snets = net.subnets(prefixlen_diff=16)
    ext_gateway_net = get_network_id_from_name(
        conf["external_gateway_network"]
    )
    for number, cidr in enumerate(snets):
        network = neutron.create_network(
            {
                "network": {
                    "name": "test_network_{}".format(number),
                },
            }
        )
        subnet = neutron.create_subnet(
            {
                "subnet": {
                    "network_id": network["network"]["id"],
                    "ip_version": 4,
                    "cidr": cidr,
                    "name": "test_subnet_{}".format(number),
                },
            }
        )
        router = neutron.create_router(
            {
                "router": {
                    "name": "test_router_{}".format(number),
                    "external_gateway_info": {
                        "network_id": ext_gateway_net,
                    }
                },
            }
        )
        neutron.add_interface_router(
            router["router"]["id"],
            {
                "subnet_id": subnet["subnet"]["id"],
            }
        )
        yield {"net-id": network["network"]["id"]}


def generate_resources(conf):
    image_id = get_image_id_from_name(conf["servers"]["image"])
    flavor_id = get_flavor_id_from_name("m1.tiny")
    server_names = (
        "test_server_{}".format(id_)
        for id_ in xrange(conf["servers"]["count"])
    )

    networks = make_networks(conf["networks"])
    nova = nova_client.Client(CLIENT_VERSION, session=get_session())
    counts = izip(
        server_names,
        get_child_counts(
            conf["servers"]["count"],
            conf["volumes"]["count"]
        ),
        get_child_counts(
            conf["servers"]["count"],
            conf["networks"]["count"]
        ),
    )
    building = [
        nova.servers.create(
            name=name,
            image=image_id,
            flavor=flavor_id,
            block_device_mapping_v2=[
                {
                    "source_type": "blank",
                    "destination_type": "volume",
                    "volume_size": conf["volumes"]["size"],
                    "delete_on_termination": True,
                }
            ] * v_count,
            nics=list(islice(networks, 0, n_count)),
        )
        for name, v_count, n_count in counts
    ]
    active = verify_active(building)
    resources = [
        {
            "id": server.id,
            "name": server.name,
        }
        for server in active
    ]
    return resources


def get_child_counts(parent_count, child_count):
    try:
        base_count = child_count // parent_count
    except ZeroDivisionError:
        counts = iter(())
    else:
        remainder = child_count % parent_count
        counts = chain(
            repeat(base_count + 1, remainder),
            repeat(base_count, parent_count - remainder),
        )

    return counts


def set_quotas():
    nova = nova_client.Client(CLIENT_VERSION, session=get_session())
    cinder = cinder_client.Client(CLIENT_VERSION, session=get_session())
    neutron = neutron_client.Client(session=get_session())

    project_id = get_session().get_project_id()
    nova.quotas.update(
        project_id,
        cores=-1,
        fixed_ips=-1,
        floating_ips=-1,
        injected_file_content_bytes=-1,
        injected_file_path_bytes=-1,
        injected_files=-1,
        instances=-1,
        key_pairs=-1,
        metadata_items=-1,
        ram=-1,
        security_group_rules=-1,
        security_groups=-1,
        server_groups=-1,
        server_group_members=-1,
    )
    cinder.quotas.update(
        project_id,
        gigabytes=-1,
        snapshots=-1,
        volumes=-1,
    )
    neutron.update_quota(
        project_id,
        {
            "quota": {
                "floatingip": -1,
                "network": -1,
                "port": -1,
                "router": -1,
                "security_group": -1,
                "security_group_rule": -1,
                "subnet": -1,
            }
        }
    )


def main():
    conf = get_conf()

    if conf["infinite_quotas"]:
        set_quotas()

    resources = generate_resources(conf["resources"])
    print dumps(resources, sort_keys=True, indent=4)


if __name__ == "__main__":
    main()
