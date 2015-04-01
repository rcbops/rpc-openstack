#!/usr/bin/env python
import maas_common


def get_value(path):
    with open(path) as f:
        value = f.read()
    return value.strip()


def get_metrics():
    metrics = {
        'nf_conntrack_count': {
            'path': '/proc/sys/net/netfilter/nf_conntrack_count'},
        'nf_conntrack_max': {
            'path': '/proc/sys/net/netfilter/nf_conntrack_max'}}

    for data in metrics.viewvalues():
        data['value'] = get_value(data['path'])

    return metrics


def main():
    metrics = get_metrics()
    maas_common.status_ok()
    for name, data in metrics.viewitems():
        maas_common.metric(name, 'uint32', data['value'])


if __name__ == '__main__':
    with maas_common.print_output():
        main()
