---
title: "Concepts"
description: Details the concepts of Meltano Cloud
layout: doc
sidebar_position: 3
---

:::info

<p><strong>Meltano Cloud is currently in Beta.</strong></p>
<p>While in Beta, functionality is not guaranteed and subject to change. <br /> If you're interested in using Meltano Cloud please join our <a href="https://meltano.com/cloud/">waitlist</a>.</p>
:::

## Meltano Cloud Users

Your Meltano Cloud user account is associated with a GitHub account for single-sign-on. If you do not have a GitHub account, you can create a free account at [github.com](https://github.com).

:::info

  <p>During the Private and Public Beta phases, we will be collecting feedback from users regarding the login and account creation experience overall. Post-GA, we plan to offer SAML on Cloud. If you have a use case to support alternate forms of login besides GitHub auth and SAML (e.g. GitLab, or user/password auth), please let your account manager know or log an issue in our <a href="https://github.com/meltano/meltano/issues">issue tracker</a>.</p>
:::

## Meltano Cloud Organizations

Your Meltano Cloud Organization is the top-level entity associated with your payment info. Each organization will be issued a unique billing account number.

:::info

  <p>Meltano Cloud Organizations should not be confused with GitHub Organizations (or "GitHub Orgs"). Each Meltano Cloud Organization can include projects from multiple GitHub Orgs.</p>
  <br />
  <p>Meltano Cloud users grant access to specific public and private repositories using the standard GitHub App authorization flow.</p>
:::

### Internal Organization ID

Meltano Cloud uses an internal alpha-numeric string (randomly generated) to uniquely identify your cloud organization's identify. This ID may occassionally be shared during Cloud debugging and you may find references to it in the internal workings of Meltano Cloud CLI.

:::caution

  <p>The "Internal Organization ID" should not be considered a permanent identifier, and may change at any time without notice.</p>
:::

## Meltano Cloud Projects

A "Cloud Project" is any Meltano project you have registered on Meltano Cloud. The project definition consists of a git repo and a relative project directory within the git repo.

### Internal Project ID

Meltano Cloud uses an internal alpha-numeric string (randomly generated) to uniquely identify your project's deployment. This ID may occassionally be shared during Cloud debugging and you may find references to it in the internal workings of Meltano Cloud CLI.

:::caution

  <p>The "Internal Project ID" should not be confused with the Project ID that is defined within <code>meltano.yml</code>.</p>
:::

:::info

  <p>The "Internal Project ID" should not be considered a permanent identifier, and may change at any time without notice.</p>
:::

## Meltano Cloud Deployments

Within each Cloud Project, you can deploy zero or more named [Meltano Environments](/concepts/environments) to Meltano Cloud. These are called Cloud Deployments.

Each Cloud Deployment must specify an environment name to deploy and a git branch to use when tracking project updates.

:::info

  <p>All operations that perform compute require a deployed environment - including: ad-hoc job execution, EL pipelines, scheduled tasks, etc.</p>
:::

## Meltano Cloud Schedules

Schedules within Meltano Cloud map directly to schedules defined in `meltano.yml`. However, in Meltano Cloud, each schedule starts off disabled by default, and each schedule is enabled or disabled on a per-Deployment basis.

For example: The Acme Data Project has a schedule named `daily-transforms` and two environments named `prod` and `staging` respectively. Upon onboarding to Meltano Cloud, the Acme team can choose to enable `daily-transforms` on the `prod` environment only. Alternatively, the Acme team can choose to enable the schedule for both environments or neither environment. Whenever changing the status on a schedule, the action to enable or disable the schedule is in the context of one specific [Deployed Environment](#meltano-cloud-deployments) and one specified schedule name.

Meltano Cloud will use the cron expression specified by the `interval` key in for the schedules defined in `meltano.yml`, but will not run precisely on the minute specified by the cron expression. Instead, each schedule will be randomly assigned a constant offset of ±7 minutes from the exact minute the cron expression would have had it run at. This offset is consistent between runs of the same schedule within the same deployment, but may differ for different schedules within the same deployment, or for the same schedule between different deployments.

As an example, if your schedule is configured to run every 15 minutes with a cron expression of `*/15 * * * *`, and it receives a random offset of +3 minutes, then instead of running at the 0th, 15th, 30th, and 45th minute of each hour, it will run at the 3rd, 18th, 33rd, and 48th minute of each hour.

## Meltano Cloud Pipelines

A Meltano Cloud pipeline is an execution of a schedule.
Pipelines use different amount of credits depending on how frequently they are run.

For more details on credits and pricing see the [Pricing FAQ](https://meltano.com/pricing/).

## Meltano Cloud Notifications

A Meltano cloud notification is a response to meltano cloud event.

### Supported notification types
- `webhook`
- `email`

### Supported notification filters
- `events`
  - `all`
- `status`
  - `succeeded`
  - `failed`
  - `cancelled`
