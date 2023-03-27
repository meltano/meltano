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

Install the [Meltano Cloud GitHub App](https://github.com/apps/meltano-cloud) to your organization.
When asked "Where do you want to install this app?" you _must_ select your GitHub organization, not your personal account.
When asked which repositories to provide the app access to, select your GitHub project repo.

For the alpha, we ask that you grant the following GitHub users `Read` access to the project repo:

1. The Meltano Cloud service account:
   1. `@MeltanoCloud`
1. Meltano engineers (for onboarding and troubleshooting support):
   1. `@WillDaSilva`
   1. `@magreenbaum`
   1. `@kgpayne`

Note:

- Grants to Meltano engineers are for the purpose of troubleshooting and support during and after the onboarding process.
- Support for granting Meltano Cloud repo access using a private access token will also be available in the near future. (Let us know if this is your preferred method.)

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
   1. Git repo information:
      1. Name of hosting provider (e.g. GitHub, GitLab, etc.)
      1. Git repo URL
      1. Git branch name
      1. The name of the [Meltano Environment](/concepts/environments) to use for onboard and testing purposes.
         - _Recommended environment name is `'sandbox'`. See prereqs above for more information._
   1. For each schedule you would like to run in Meltano Cloud:
      1. Schedule name
1. Per authorized user:
   1. User's Full Name
   1. User's Email Address
   1. User's GitHub ID (used for identity, authentication, and permissioning)
   1. User's Role: `owner`, `maintaner`, or `reader`
      - See [users and roles](/platform/#roles-and-permissions) for more information.

### Step 2: Encrypt and submit the `.env` file

After receiving the above information, Meltano will register your project(s) and generate a new set of encryption and decryption keys specific to your organization. We will then provide you with your organization's public key along with instructions to encrypt your `.env` file and attach your encrypted file to your project.

The [kms-ext tool](https://github.com/meltano/kms-ext) is available to use for the encryption process.
See the [encrypting secrets docs](/encrypting_secrets) for more details and examples of how to do this.
Also be aware that there are some [reserved variables](/platform/#reserved-variables) only for use by Meltano Cloud.

Also see the [security whitepaper](/security) for more information on encryption algorithms.

### Step 3: Initial execution and debugging

Once the above steps are complete, Meltano will initialize your account and execute the provided schedules. If any errors occur during execution, we will notify you and provide access to the necessary logs for debugging.

## Additional Resources

- [Known Issues and Feature Limitations](/known_issues)
- [Security Whitepaper (Latest)](/security)
- [Roles and Permissions](/platform/#roles-and-permissions)
