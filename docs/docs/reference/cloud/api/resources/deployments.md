---
title: Deployments
description: Meltano Cloud deployments resource reference documentation
sidebar_position: 23
---

import Examples from '@site/src/components/Examples';
import Snippet from '@site/src/components/Snippet';

Deployments let the user schedule a [job](jobs) to deploy the contents of their [workspace](workspaces) repository to their workspace in Meltano Cloud.

This can be done manually or via a [GitHub repository webhook](https://docs.github.com/en/webhooks/using-webhooks/creating-webhooks#creating-a-repository-webhook):
- Payload URL: `https://app.meltano.com/api/workspaces/<workspace_id>/deployments/github-webhook`
- Content type: `application/json`
- Secret: "Deployment Secret" from workspace settings in Meltano Cloud

---

## Requests

### Deploy your workspace repository

:::info
**POST** `/api/workspaces/{workspaces-id}/deployments`
:::

Deploys the workspace `{workspace-id}`.

<Examples path="deployment/deploy-workspace" />

#### Response
`202 Accepted`

[Job](jobs) with HAL links.
<Snippet path="deployment/deploy-workspace/response-body.md" />

---

### GitHub webhook workspace deployment

:::info
**POST** `/api/workspaces/{workspaces-id}/deployments/github-webhook`
:::

Receives `POST` requests from GitHub and starts a workspace deploy job.

<Examples path="deployment/github-webhook-deploy" />

#### Response
`202 Accepted`

[Job](jobs) with HAL links.
<Snippet path="deployment/github-webhook-deploy/response-body.md" />

---
