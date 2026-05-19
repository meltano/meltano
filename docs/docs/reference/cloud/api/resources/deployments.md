---
title: Deployments
description: Matatika Deployments resource reference documentation
---

import Snippet from '@site/src/components/Snippet';
import TabItem from '@theme/TabItem';
import Tabs from '@theme/Tabs';

Deployments let the user schedule a [job](jobs) to deploy the contents of their [workspace](workspaces) repository to their workspace in the Matatika cloud.

This can be done manually or via a GitHub Webhook which you can see how to set up in our Quick Start Guide: [Workspace Deploy Hook]({{site.baseurl}}/how-to-guides/manage-workspaces/managing-config-from-github)

---

## Requests

### Deploy your workspace repository

:::info
**POST** `/api/workspaces/{workspaces-id}/deployments`
:::

Deploys the workspace `{workspace-id}`.

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<Snippet path="deployment/deploy-workspace/curl-request.md" />

</TabItem>
<TabItem value="python" label="Python (requests)">

<Snippet path="deployment/deploy-workspace/python-requests.md" />

</TabItem>
</Tabs>

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

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<Snippet path="deployment/github-webhook-deploy/curl-request.md" />

</TabItem>
<TabItem value="python" label="Python (requests)">

<Snippet path="deployment/github-webhook-deploy/python-requests.md" />

</TabItem>
</Tabs>

#### Response
`202 Accepted`

[Job](jobs) with HAL links.
<Snippet path="deployment/github-webhook-deploy/response-body.md" />

---