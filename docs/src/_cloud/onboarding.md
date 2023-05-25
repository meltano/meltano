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

### Prereq #1: Provide access to your repo

Click the following link to install the [Meltano Cloud GitHub App](https://github.com/apps/meltano-cloud) to your organization.
When asked "Where do you want to install this app?" you _must_ select your GitHub organization, not your personal account.
When asked which repositories to provide the app access to, select your GitHub project repo.

### Prereq #2: Creating a test or sandbox environment

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

### Prereq #3: Create schedules if needed

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

### Step 1: Submit Project Onboarding Information

Once you've completed the above, you are ready to onboard your project to Meltano Cloud.

To onboard your project, Meltano will need the following project information:

1. Company name: `___________`
   - E.g. "ABC Company Inc."
1. Primary contact name and email: `___________`
1. GitHub repo information:
   1. Repo URL: `___________`
   2. Initial Meltano Environment Name: `___________` (e.g. 'prod' or 'staging')
   3. Git branch name to use for the above environment: `___________` (e.g. `main`)
1. List of GitHub User IDs, separated by commas: `___________`
1. List of Meltano schedule names and intervals: `___________`
   - This can be copy-pasted from `meltano.yml`.
   - During Beta, you'll need to reach out to Meltano support in order to create additional schedules.

### Step 2: Install (or update) the Cloud CLI

To install from scratch using [pipx](https://pypa.github.io/pipx/installation/#install-pipx):

```console
pipx install 'git+https://github.com/meltano/meltano.git@cloud#subdirectory=src/cloud-cli'
```

To upgrade to the latest version:

```console
pipx reinstall meltano-cloud-cli
```

The above commands will install a `meltano-cloud` CLI command into your workstation.

### Step 3: User creation and authorization

First, create your user account by logging in via: `meltano-cloud login`.

The login command will open a browser window which you can use to create your account. In the Beta, your identification and authorization will be driven by your GitHub login identity. No Meltano-specific passwords or usernames are needed, and Meltano Cloud does not have access to your personal GitHub credentials.

After you create your account, within one business day, your account will be authorized according to the onboarding information you'll see be able to access your project within the CLI.

<div class="notification is-info">
  <p>As of now, installing the Meltano Cloud <a href="#prereq-1-provide-access-to-your-repo">GitHub App</a> to your organization is a separate process from granting Meltano Cloud access to use your GitHub profile for login purposes. Both the GitHub App installation for your organization <em>and</em> the OAuth grant flow for your profile must be performed in order to have full access to Meltano Cloud functionality.</p>
</div>

### Step 4: Test basic functionality

After login, and after your project is onboarded, you can explore the interface with a few different commands:

```console
meltano-cloud history
```

```console
meltano-cloud schedule list
```

### Step 5: Initialize secrets

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

### Step 6: Run and debug your workloads

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
