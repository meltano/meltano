---
title: "Known Limitations"
description: Details Beta limitations for  Meltano Cloud
layout: doc
hidden: false
weight: 10
---

<div class="notification is-info">
  <p><strong>Meltano Cloud is currently in Beta.</strong></p>
  <p>While in Beta, functionality is not guaranteed and subject to change. <br /> If you're interested in using Meltano Cloud please join our <a href="https://meltano.com/cloud/">waitlist</a>.</p>
</div>

## Limitations during Beta

### Manually-submitted schedules lists

During Beta, Meltano Cloud will only run schedules which you have explicitly declared and requested.

In the future, Meltano Cloud will automatically run any schedules you have configured to run within the named environment.

See related issue: [#6853](https://github.com/meltano/meltano/issues/6853).

### Manual Deployment Of All Changes

Meltano cloud will have support for automatic deployments in GA but currently users need to manually request a re-deployment of a project when new commits are added to the git repository.

```bash
meltano-cloud deployment update --name prod
```

See the [deployments CLI reference](/cloud/cloud-cli#deployment).

### Support-Requested Addition of Projects

Meltano cloud will have support for users to self-manage addition of projects in the near future but currently a project addition needs to be requested through Meltano Cloud Support.

See related issue: [#7412](https://github.com/meltano/meltano/issues/7412)

## Other Unsupported Features in Meltano Cloud

The following features are not currently scoped for inclusion for the Meltano Cloud GA.

1. Hosted Airflow as orchestrator
   - At launch, Meltano will not support hosted Airflow orchestration. Instead, Meltano Cloud provides its own built-in managed scheduler and orchestrator.
   - Workaround:
     - We are evaluating options for users to invoke workloads from external services and from the command line. These could provide a method of remote execution from a self-managed Airflow server, for instance.
1. Hosting of BYO web services and other stateful service backends
   - At launch, Meltano will not allow incoming traffic to any running container. This is for security reasons.
   - Workarounds:
     - We may in the future offer BYO-services when defined as Meltano plugins. Due to the additional security provisions required, this additional functionality may only be available for premium service tiers.
1. Manipulating state artifacts
   - Although incremental replication is supported in Meltano Cloud, [direct state manipulation](https://docs.meltano.com/reference/command-line-interface#state) is not yet supported.
   - See the [Backfills and State](/cloud/usage#backfills-and-state) section of the usage Cloud docs for more details.
   - In the future, users will be able to, for example, seed initial state by setting Meltano Cloud as a [state backend](https://docs.meltano.com/concepts/state_backends).

Based upon user feedback, we will continue to reevaluate the list of supported and non-supported features for Meltano Cloud. If you have an urgenct need for any of the above features, please let us know!
