---
title: "Onboarding"
description: Details the onboarding process of Meltano Cloud
layout: doc
weight: 2
---

<div class="notification is-info">
  <p><strong>Meltano Cloud is currently in Beta.</strong></p>
  <p>While in Beta, functionality is not guaranteed and subject to change. <br> If you're interesting in using Meltano Cloud please join our <a href="https://meltano.com/cloud/">waitlist</a>.</p>
</div>

## Prereqs

### Prereq #1: Provide access to your repo

Click the following link to install the [Meltano Cloud GitHub App](https://github.com/apps/meltano-cloud) to your organization.
When asked "Where do you want to install this app?" you _must_ select your GitHub organization, not your personal account.
When asked which repositories to provide the app access to, select your GitHub project repo.

### Prereq #2: Creating a test or sandbox environment

For onboarding and debugging purposes, we recommend that teams create a [Meltano Environment](/concepts/environments) named `'sandbox'`, which can be used by Meltano Cloud to test that all jobs are working as expected.

For more information, please see our guide: [Creating a Sandbox Environment for Meltano Cloud](/cloud/sandbox_environments)

### Prereq #3: Create schedules if needed

If your project does not yet have schedules defined - for instance, if you are running workloads via an external orchestrator - you'll want to create new schedules for use by Meltano Cloud.

Schedules should be specified in UTC if providing a cron expression.

## Onboarding Steps

### Step 1: Submit Project Onboarding Information

Once you've completed the above, you are ready to onboard your project to Meltano Cloud.

To onboard your project, Meltano will need the following project information:

1. Company name
   - E.g. "ABC Company Inc."
1. Primary contact name and email
1. Preferred Organization ID ("org ID") on Meltano Cloud
   - Organization ID :
     - must be globally unique
     - must be 20 characters or less
     - can contain a combination of lowercase letters, numbers, and dashes (no other special characters).
   - E.g. `abc-company`, `abc-company-usa`, `abc-data-team`, `abc-finance-team`, etc.
1. For each project:
   1. GitHub repo information:
      1. Repo URL
      2. Git branch name and [Meltano Environment](/concepts/environments) to use for onboard and testing purposes. (We recommend `'staging'` for Environment name and `'staging'|'develop'` for branch name.)
      3. Optionally, a branch name to pair with your `'prod'` environment. (We recommend `'prod'` for Environment name and `'main'` for branch name.)
1. Per authorized user:
   1. User's Full Name
   2. User's Email Address
   3. User's GitHub ID (used for identity, authentication, and permissioning)
   4. User's Role: `owner`, `developer`, or `stakeholder`
      - See [users and roles](/platform/#roles-and-permissions) for more information.

### Step 2: Install (or update) the Cloud CLI

To install from scratch:

```console
pipx install 'git+https://github.com/meltano/meltano.git@cloud#subdirectory=src/cloud-cli'
```

To update to the latest version:

```console
pipx uninstall meltano-cloud-cli && pipx install 'git+https://github.com/meltano/meltano.git@cloud#subdirectory=src/cloud-cli'
```

### Step 3: User creation and authorization

First, create your user account by logging in via: `meltano-cloud login`.

The login command will open a browser window which you can use to create your account. In the Beta, your identification and authorization will be driven by your GitHub login identity. No Meltano-specific passwords or usernames are needed, and Meltano Cloud does not have access to your personal GitHub credentials.

After you create your account, within one business day, your account will be authorized according to the onboarding information you'll see be able to access your project within the CLI.

### Step 4: Test basic functionality

After login, you can see that operations

```console
meltano-cloud schedule list
```

_COMING SOON!_

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

_COMING SOON!_

## Additional Resources

- [Known Issues and Feature Limitations](/known_issues)
- [Security Whitepaper (Latest)](/security)
- [Roles and Permissions](/platform/#roles-and-permissions)
