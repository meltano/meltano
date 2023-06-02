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
When asked "Where do you want to install this app?" you _must_ select either your GitHub organization or personal account depending on which contains the repository you wish to provide access.
When asked which repositories to provide the app access to, select your GitHub project repo.

If you do not yet have a Meltano project in GitHub, you can follow the steps in our [Getting Started](/getting-started) guide.

### Prereq #3: Define your schedules

Meltano Cloud uses the [schedules](https://docs.meltano.com/concepts/project#schedules) defined in your meltano.yml project file to run workloads.

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

### Step 2: Login to Meltano Cloud

Login to Meltano Cloud by running the `meltano-cloud login` [command](/cloud/cloud-cli#login) in your local terminal.
You'll have to sign in with the same GitHub user you provided when you signed up via the waitlist.

The login command will open a browser window which you can use to access your account. In the Beta, your identification and authorization will be driven by your GitHub login identity. No Meltano-specific passwords or usernames are needed, and Meltano Cloud does not have access to your personal GitHub credentials.

While Meltano Cloud is in Beta, it may take up to one business day for your user to be fully provisioned and added to your Meltano Cloud organization. You'll be notified via email once your newly created user has been added to your organization, at which time you can logout via `meltano-cloud logout` and then log back in to have full CLI access to your organization's Meltano Cloud resources.

<div class="notification is-info">
  <p>Installing the Meltano Cloud <a href="#prereq-2-provide-access-to-your-repo">GitHub App</a> to your organization is a separate process from granting Meltano Cloud access to use your GitHub profile for login purposes. Both the GitHub App installation for your organization <em>and</em> the OAuth grant flow for your profile must be performed in order to have full access to Meltano Cloud functionality.</p>
</div>


### Step 3: Set default project and validate access and functionality

After logging in you can explore the interface with a few different commands.
The full list of CLI commands is in the [Cloud Docs](https://docs.meltano.com/cloud/cloud-cli).

To see Meltano Cloud projects for your organizations, run:
```console
meltano-cloud project list
```
```console
Running this command will verify that your project is connected and you're properly authenticated with Meltano Cloud.
```

You should select a project to use as default for all commands.
You can do this by running:
```console
meltano-cloud project use <project name>
```

### Step 4: Create deployments

In order for pipelines to run, they must have a [deployment](/cloud/concepts#meltano-cloud-deployments) to run in.

To deploy a named [Meltano Environment](/concepts/environments) to Meltano Cloud, run the following [command](https://docs.meltano.com/cloud/cloud-cli#deployment):

```console
meltano-cloud deployment create --name <deployment name> --environment-name <Meltano Environment name> --git-rev <the git revision to use for this deployment>
```

For example, if you wanted to deploy the `prod` Meltano Environment as defined in your `meltano.yml` in the `main` branch of your git repo and you wanted the Meltano Cloud deployment to be named `production`,  you would run:

```console
meltano-cloud deployment create --name production --environment-name prod --git-rev main
```

To confirm that your deployment was created, you can view all of your Meltano Cloud deployments by running:
```console
meltano-cloud deployments list
```

### Step 5: Initialize secrets

Secrets allow you to pass environment variables to your workloads without needing to expose them within your `meltano.yml`.
Setting a secret in Meltano Cloud is equivalent to using a `.env` file to store environment variables at runtime.
Secrets are shared across all deployments in your project and can be referenced in your `meltano.yml` file just as you would reference environment variables locally.

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

### Step 6: Run your workloads

You can invoke a schedule on-demand with the `meltano-cloud run` [command](/cloud/cloud-cli#run):

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

### Step 7: Enable schedules

Your Meltano Cloud project's schedules are disabled by default.
Use the `meltano-cloud schedule enable <SCHEDULE NAME>` [command](/cloud/cloud-cli#schedule) to enable schedules.
