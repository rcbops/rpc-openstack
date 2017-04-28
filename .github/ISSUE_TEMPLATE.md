> **THIS IS A PUBLIC FACING ISSUE.**
>
> Do not include private or confidential information in this issue.

## Is this a feature or a bug?

- [ ] Feature _(request for enhancement, new functionality)_
- [ ] Bug _(something is broken)_

## Which version of rpc-openstack does this issue relate to?
- [ ] master
- [ ] newton-14.0
- [ ] mitaka-13.1
- [ ] liberty-12.2

Run `git log --pretty=oneline | head -n 1` and provide the output below between
the backtick lines:

```

```

## What happened?

> Example: I can't snapshot a cinder volume on an AIO RPC-O deployment.

## What were you doing when it happened?

> Example: I have an existing cinder volume and I get this error when I try
> to snapshot it using openstackclient:
>
>      $ openstack --os-cloud=mycloud volume snapshot list
>      publicURL endpoint for volumev2 service in RegionOne region not found

## What did you expect to happen instead of what actually happened?

> Example: I expected a cinder volume snapshot to be successfully created.

## Do you think the documentation team wants to know about this?

- [ ] Yes, and I submitted an issue to [Docs issues](https://github.com/rackerlabs/docs-rpc/issues "Docs issues")
- [ ] Yes, and I contributed a documentation patch to [docs-rpc](https://github.com/rackerlabs/docs-rpc "docs-rpc")
- [ ] No documentation required for this change

## Does your change require a release note?

- [ ] Yes, it's a pretty big deal like I am and I've made a reno note!
- [ ] Nope, this change has no major impact.
