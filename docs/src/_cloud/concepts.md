---
title: "Concepts"
description: Details the concepts of Meltano Cloud
layout: doc
weight: 1
---

<div class="notification is-info">
  <p><strong>Meltano Cloud is currently in Beta.</strong></p>
  <p>While in Beta, functionality is not guaranteed and subject to change. <br> If you're interested in using Meltano Cloud please join our <a href="https://meltano.com/cloud/">waitlist</a>.</p>
</div>

## Meltano Cloud Users

Your Meltano Cloud user account is associated with a GitHub account for single-sign-on. If you do not have a GitHub account, you can create a free account at [github.com](https://github.com).

<div class="notification is-info">
  <p>During the Private and Public Beta phases, we will be collecting feedback from users regarding the login and account creation experience overall. Post-GA, we plan to offer SAML on Cloud. If you have a use case to support alternate forms of login besides GitHub auth and SAML (e.g. GitLab, or user/password auth), please let your account manager know or log an issue in our <a href="https://github.com/meltano/meltano/issues">issue tracker</a>.</p>
</div>

## Meltano Cloud Organizations

Your Meltano Cloud Organization is the top-level entity associated with your payment info. Each organization will be issued a unique billing account number.

<div class="notification is-info">
  <p>Meltano Cloud Organizations should not be confused with GitHub Organizations (or "GitHub Orgs"). Each Meltano Cloud Organization can include projects from multiple GitHub Orgs.</p>
  <br>
  <p>Meltano Cloud users grant access to specific public and private repositories using the standard GitHub App authorization flow.</p>
</div>

### Internal Organization ID

Meltano Cloud uses an internal alpha-numeric string (randomly generated) to uniquely identify your cloud organization's identify. This ID may occassionally be shared during Cloud debugging and you may find references to it in the internal workings of Meltano Cloud CLI.

<div class="notification is-warning">
  <p>The "Internal Organization ID" should not be considered a permanent identifier, and may change at any time without notice.</p>
</div>

## Meltano Cloud Projects

A "Cloud Project" is any Meltano project you have registered on Meltano Cloud. The project definition consists of a git repo and a relative project directory within the git repo.

### Internal Project ID

Meltano Cloud uses an internal alpha-numeric string (randomly generated) to uniquely identify your project's deployment. This ID may occassionally be shared during Cloud debugging and you may find references to it in the internal workings of Meltano Cloud CLI.

<div class="notification is-warning">
  <p>The "Internal Project ID" should not be confused with the Project ID that is defined within <code>meltano.yml</code>.</p>
</div>

<div class="notification is-info">
  <p>The "Internal Project ID" should not be considered a permanent identifier, and may change at any time without notice.</p>
</div>

## Meltano Cloud Deployments

Within each Cloud Project, you can deploy zero or more named [Meltano Environments](/concepts/environments) to Meltano Cloud. These are called Cloud Deployments.

Each Cloud Deployment must specify an environment name to deploy and a git branch to use when tracking project updates.

<div class="notification is-info">
  <p>All operations that perform compute require a deployed environment - including: ad-hoc job execution, EL pipelines, scheduled tasks, etc.</p>
</div>

## Meltano Cloud Schedules

Schedules within Meltano Cloud map directly to schedules defined in `meltano.yml`. However, in Meltano Cloud, each schedule starts off disabled by default, and each schedule is enabled or disabled on a per-Deployment basis.
For example: The Acme Data Project has a schedule named `daily-transforms` and two environments named `prod` and `staging` respectively. Upon onboarding to Meltano Cloud, the Acme team can choose to enable `daily-transforms` on the `prod` environment only. Alternatively, the Acme team can choose to enable the schedule for both environments or neither environment. Whenever changing the status on a schedule, the action to enable or disable the schedule is in the context of one specific [Deployed Environment](#meltano-cloud-deployments) and one specified schedule name.
