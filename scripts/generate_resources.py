#! /usr/bin/env python
from argparse import ArgumentParser
from datetime import datetime, timedelta
from ipaddress import IPv4Network
from itertools import chain, izip, repeat, islice
from json import dumps
import os
from time import sleep

from openstack import exceptions
import os_client_config
from cinderclient import client as cinder_client
from novaclient import client as nova_client


def get_conf():
    parser = ArgumentParser()
    parser.add_argument("--servers", type=int, default=1)
    parser.add_argument("--volumes", type=int, default=0)
    parser.add_argument("--networks", type=int, default=1)
    parser.add_argument("--infinite-quotas", action="store_true")
    parser.add_argument("--output-file")
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
        "output_file": args.output_file,
        "infinite_quotas": args.infinite_quotas,
        "resources": {},
    }

    conf["resources"]["servers"] = {
        "count": args.servers,
        "flavor": "tempest1",
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
    conf["resources"]["security_group"] = {
        "name": "secgrp1",
    }
    return conf


def verify_active(building, timeout=600):
    conn = os_client_config.make_sdk()
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
            server = conn.compute.get_server(server)
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
    conn = os_client_config.make_sdk()
    net = IPv4Network(u'10.0.0.0/8')
    snets = net.subnets(prefixlen_diff=16)
    ext_gateway_net = conn.network.find_network(
        conf["external_gateway_network"],
        ignore_missing=False
    )
    for number, cidr in enumerate(snets):
        network = conn.network.create_network(
            name="test_network_{}".format(number),
        )
        subnet = conn.network.create_subnet(
            network_id=network.id,
            ip_version=4,
            cidr=str(cidr),
            name="test_subnet_{}".format(number),
        )
        router = conn.network.create_router(
            name="test_router_{}".format(number),
            external_gateway_info={
                "network_id": ext_gateway_net.id,
            }
        )
        conn.network.add_interface_to_router(
            router,
            subnet_id=subnet.id,
        )
        yield {"uuid": network.id}


def create_floating_ips(network, count):
    conn = os_client_config.make_sdk()
    ext_gateway_net = conn.network.find_network(network, ignore_missing=False)
    ips = []
    for _ in range(count):
        fip = conn.network.create_ip(floating_network_id=ext_gateway_net.id)
        ips.append(fip.floating_ip_address)
    return ips


def generate_resources(conf):
    conn = os_client_config.make_sdk()
    image = conn.image.find_image(
        conf["servers"]["image"], ignore_missing=False
    )
    flavor = conn.compute.find_flavor(
        conf["servers"]["flavor"],
        ignore_missing=False
    )
    sec_group = conn.network.find_security_group(
        conf["security_group"]["name"],
        ignore_missing=False
    )
    server_names = (
        "test_server_{}".format(id_)
        for id_ in xrange(conf["servers"]["count"])
    )

    networks = make_networks(conf["networks"])
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
        conn.compute.create_server(
            name=name,
            image_id=image.id,
            flavor_id=flavor.id,
            block_device_mapping_v2=[
                {
                    "source_type": "image",
                    "destination_type": "local",
                    "delete_on_termination": True,
                    "uuid": image.id,
                    "boot_index": 0,
                },
            ] + [
                {
                    "source_type": "blank",
                    "destination_type": "volume",
                    "volume_size": conf["volumes"]["size"],
                    "delete_on_termination": True,
                },
            ] * v_count,
            networks=list(islice(networks, 0, n_count)),
            security_groups=[{"name": sec_group.name}],
        )
        for name, v_count, n_count in counts
    ]

    floating_ips = create_floating_ips(
        conf["networks"]["external_gateway_network"],
        len(building)
    )
    active = verify_active(building)
    for server, floating_ip in zip(active, floating_ips):
        conn.compute.add_floating_ip_to_server(server, floating_ip)
    return floating_ips


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
    conn = os_client_config.make_sdk()
    project_id = conn.session.get_project_id()

    nova = nova_client.Client("2", session=conn.session)
    try:
        cinder = cinder_client.Client("2", session=conn.session)
        cinder.quotas.update(
            project_id,
            gigabytes=-1,
            snapshots=-1,
            volumes=-1,
        )
    except exceptions.SDKException:
        cinder = cinder_client.Client("1", session=conn.session)
        cinder.quotas.update(
            project_id,
            gigabytes=-1,
            snapshots=-1,
            volumes=-1,
        )

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
    conn.network.update_quota(
        project_id,
        floatingip=-1,
        network=-1,
        port=-1,
        router=-1,
        security_group=-1,
        security_group_rule=-1,
        subnet=-1,
    )


def ensure_sec_group(name):
    conn = os_client_config.make_sdk()

    try:
        sg = conn.network.find_security_group(name, ignore_missing=False)
    except exceptions.ResourceNotFound:
        sg = conn.network.create_security_group(name=name)

    try:
        conn.network.create_security_group_rule(
            security_group_id=sg.id,
            direction='ingress',
            remote_ip_prefix='0.0.0.0/0',
            protocol='icmp',
            port_range_max=None,
            port_range_min=None,
            ethertype='IPv4'
        )
    except exceptions.HttpException as e:
        if e.http_status != 409:
            raise e
    return sg


def main():
    conf = get_conf()

    if conf["infinite_quotas"]:
        set_quotas()

    ensure_sec_group(
        conf["resources"]["security_group"]["name"]
    )
    resources = generate_resources(conf["resources"])
    data = dumps(resources, sort_keys=True, indent=4)
    if conf["output_file"]:
        with open(conf["output_file"], "wb") as f:
            f.write(data)
    else:
        print data


if __name__ == "__main__":
    main()
