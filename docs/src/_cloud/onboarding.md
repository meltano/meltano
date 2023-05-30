---
title: "Onboarding"
description: Details the onboarding process of Meltano Cloud
layout: doc
weight: 2
---

<div class="notification is-info">
  <p><strong>Meltano Cloud is currently in Beta.</strong></p>
  <p>While in Beta, functionality is not guaranteed and subject to change. <br> If you're interested in using Meltano Cloud please join our <a href="https://meltano.com/cloud/">waitlist</a>.</p>
</div>

## Prereqs

### Prereq #1: Sign up for the waitlist

While Meltano Cloud is in Beta, you must sign up via [the waitlist](https://meltano.com/cloud/) in order to gain access.

Waitlist members are added to Meltano Cloud on a rolling basis. You'll receive an email once you've been added.

### Prereq #2: Provide access to your repo

Click the following link to install the [Meltano Cloud GitHub App](https://github.com/apps/meltano-cloud) to your organization.
When asked "Where do you want to install this app?" you _must_ select your GitHub organization, not your personal account.
When asked which repositories to provide the app access to, select your GitHub project repo.

### Prereq #3: Creating a test or sandbox environment

For onboarding and debugging purposes, we recommend that teams create a [Meltano Environment](/concepts/environments) named `'sandbox'`, which can be used by Meltano Cloud to test that all jobs are working as expected.

For more information, please see our guide: [Creating a Sandbox Environment for Meltano Cloud](/cloud/sandbox_environments)

If you aren't yet declaring 'environments' in `meltano.yml`, you can get started quickly by copy-pasting this snippet into your `meltano.yml` file:

```yml
environments:
- dev
- staging
- prod
default_environment: dev
```

### Prereq #4: Create schedules if needed

If your project does not yet have schedules defined - for instance, if you are running workloads via an external orchestrator - you'll want to create new schedules for use by Meltano Cloud.

Schedules should be specified in UTC if providing a cron expression.

If you don't yet have an existing schedule, you can get started quickly by copy-pasting this snippet to the bottom of your `meltano.yml` file:

```yml
schedules:
- name: daily-refresh
  job: daily-refresh-job
  interval: @daily  # Can be @daily, @hourly, etc., or a cron-based interval
jobs:
- name: daily-refresh-job
  tasks:
  # Update this section to include any EL jobs or other
  # commands that you'd like to run:
  - tap-gitlab target-snowflake
  - dbt-snowflake:run
  - dbt-snowflake:test
```

## Onboarding Steps

### Step 1: Install (or update) the Cloud CLI

To install from scratch using [pipx](https://pypa.github.io/pipx/installation/#install-pipx):

```console
pipx install 'git+https://github.com/meltano/meltano.git@cloud#subdirectory=src/cloud-cli'
```

To upgrade to the latest version:

```console
pipx reinstall meltano-cloud-cli
```

The above commands will install a `meltano-cloud` CLI command into your workstation.

### Step 2: User creation and authorization

First, create your user account by logging in via: `meltano-cloud login`.

The login command will open a browser window which you can use to create your account. In the Beta, your identification and authorization will be driven by your GitHub login identity. No Meltano-specific passwords or usernames are needed, and Meltano Cloud does not have access to your personal GitHub credentials.

While Meltano Cloud is in Beta, it may take up to one business day for your user to be fully provisioned and added to your Meltano Cloud organization. You'll be notified via email once your newly created user has been added to your organization, at which time you can logout via `meltano-cloud logout` and then log back in to have full CLI access to your organization's Meltano Cloud resources.

<div class="notification is-info">
  <p>As of now, installing the Meltano Cloud <a href="#prereq-1-provide-access-to-your-repo">GitHub App</a> to your organization is a separate process from granting Meltano Cloud access to use your GitHub profile for login purposes. Both the GitHub App installation for your organization <em>and</em> the OAuth grant flow for your profile must be performed in order to have full access to Meltano Cloud functionality.</p>
</div>


### Step 3: Test basic functionality

After login, and after your user is added to your organization, you can explore the interface with a few different commands:

```console
meltano-cloud history
```

```console
meltano-cloud schedule list
```

### Step 4: Initialize secrets

Secrets are configured using the Cloud CLI.

```console
meltano-cloud config env set TAP_GITLAB_PASSWORD
> Secret value: ****
```

```console
meltano-cloud config env list
> TAP_GITLAB_FOOBAR
> TAP_GITLAB_PASSWORD
```

### Step 5: Run and debug your workloads

You can invoke a schedule on-demand with the `meltano-cloud run` command:

```console
meltano-cloud run --deployment=staging SCHEDULE_NAME
```

Within 1-2 minutes, the running workload will appear in `history`:

```console
meltano-cloud history
```

To view logs for any completed or still-running job, you can use:

```console
meltano-cloud logs print --execution-id=ASDF1234...
```

### Step 6: Enable schedules

Your Meltano Cloud project's schedules are disabled by default.
Use the `meltano-cloud schedule enable <SCHEDULE NAME>` command to enable schedules.
