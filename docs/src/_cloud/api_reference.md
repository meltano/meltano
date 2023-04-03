---
title: "API Reference"
description: Details the Private API of Meltano Cloud
layout: doc
hidden: true
---

<div class="notification is-info">
  <p><strong>Meltano Cloud is currently in Beta.</strong></p>
  <p>While in Beta, functionality is not guaranteed and subject to change. <br> If you're interested in using Meltano Cloud please join our <a href="https://meltano.com/cloud/">waitlist</a>.</p>
</div>

API usage and examples for features of Meltano Cloud.

The API functionalities documented here may be adjusted during the Meltano Cloud alpha, and will definitely be adjusted prior to the Meltano Cloud GA release.

## On-demand Job Runners

On-demand job runners allow users to rerun or run at any point a scheduled job.

During the onboarding process, you will receive the following information that you will need to invoke your scheduled jobs on-demand:
- An API key
- A Meltano Runner Secret
- Your Organization's Tenant Resource Key (Tenant ID)
- Your Project's ID (if you have multiple projects, you will receive one for each)

Information that you provide to us during [onboarding](/onboarding/#step-1-submit-project-onboarding-information):
- The name of the [Meltano Environment](/concepts/environments)
- The schedule name

You will need to pass them in as headers (`x-api-key` and `meltano-runner-secret`) when invoking the API as part of the authentication process.

### CURL Example

Set environment variables locally:
- `API_KEY`
- `MELTANO_RUNNER_SECRET`
- `TENANT_RESOURCE_KEY`
- `PROJECT_ID`
- `ENVIRONMENT_NAME`
- `SCHEDULE_NAME`

```
curl -X POST "https://cloud-runners.meltano.com/v1/${TENANT_RESOURCE_KEY}/${PROJECT_ID}/${ENVIRONMENT_NAME}/${SCHEDULE_NAME}" -H "x-api-key": ${API_KEY}" -H "meltano-runner-secret: ${MELTANO_RUNNER_SECRET}"
```
