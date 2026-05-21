---
title: Subscriptions
description: Meltano Cloud subscriptions resource reference documentation
sidebar_position: 20
---

import Examples from '@site/src/components/Examples';
import Snippet from '@site/src/components/Snippet';

Subscriptions are a declaration of interest in a particular resource, allowing a user to receive [notifications](notifications) when certain events occur. The events that trigger [notifications](notifications) are controlled by the [type of subscription](#subscription-type).

---

## Objects

### Subscription

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`id` | `string` | Version 4 UUID | The subscription ID
`created` | `string` | ISO 8601 timestamp | The instant the subscription was created at
`lastModified` | `string` | ISO 8601 timestamp | The instant the subscription was last modified at
`type` | `string` | [Subscription Type](#subscription-type) | The type of subscription

<Snippet path="subscriptions/view-a-subscription/response-body.md" />

## Formats

### Subscription Type

`string`

Value | Description
----- | -----------
`ALL` | Triggers [notifications](notifications) for all resource events
`ALERTS` | Triggers [notifications](notifications) for resource alert events only
`NONE` | Does not trigger any [notifications](notifications)

---

## Requests

### View all subscriptions

:::info
**GET** `/api/subscriptions`
:::

Returns all subscriptions for the authenticated user profile.

<Examples path="subscriptions/view-all-subscriptions" />

#### Response
`200 OK`

[Subscription](#subscription) collection with HAL links.
<Snippet path="subscriptions/view-all-subscriptions/response-body.md" />

---

### View all member subscriptions to a workspace

:::info
**GET** `/api/workspaces/{workspace-id}/members/subscriptions`
:::

Returns all member subscriptions to the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist

<Examples path="subscriptions/view-all-member-subscriptions-to-a-workspace" />

#### Response
`200 OK`

[Subscription](#subscription) collection with HAL links.
<Snippet path="subscriptions/view-all-member-subscriptions-to-a-workspace/response-body.md" />

---

### View a subscription

:::info
**GET** `/api/subscriptions/{subscription-id}`
:::

Returns the subscription `{subscription-id}`.

#### Prerequisites
- Subscription `{subscription-id}` must exist

<Examples path="subscriptions/view-a-subscription" />

#### Response
`200 OK`

[Subscription](#subscription) with HAL links.
<Snippet path="subscriptions/view-a-subscription/response-body.md" />

---

### Subscribe to a workspace

:::info
**POST** `/api/workspaces/{workspace-id}/subscriptions`
:::

Subscribes the authenticated user profile to the workspace `{workspace-id}`.

By default, the subscription is configured for all workspace events (see [Subscription Type](#subscription-type) for more information).

#### Prerequisites
- Workspace `{workspace-id}` must exist

#### Query Parameters

Parameter | Required | Format | Default Value | Description
--------- | -------- | ------ | ------------- | -----------
`allMembers` | No | Boolean | `false` | Whether or not to subscribe the workspace to workspace events, in order to enable workspace-wide notifications for all [members](members) by default (applicable for the workspace owner only)


<Examples path="subscriptions/subscribe-to-a-workspace" />

#### Response
`200 OK`

[Subscription](#subscription) with HAL links.
<Snippet path="subscriptions/subscribe-to-a-workspace/response-body.md" />

---

### Subscribe to a channel

:::info
**POST** `/api/channels/{channel-id}/subscriptions`
:::

Subscribes the authenticated user profile to the channel `{channel-id}`.

By default, the subscription is configured for all channel events (see [Subscription Type](#subscription-type) for more information).

#### Prerequisites
- Channel `{channel-id}` must exist

#### Query Parameters

Parameter | Required | Format | Default Value | Description
--------- | -------- | ------ | ------------- | -----------
`allMembers` | No | Boolean | `false` | Whether or not to subscribe the workspace to channel events, enabling notifications for all [members](members) by default (applicable for the workspace owner only)


<Examples path="subscriptions/subscribe-to-a-channel" />

#### Response
`200 OK`

[Subscription](#subscription) with HAL links.
<Snippet path="subscriptions/subscribe-to-a-channel/response-body.md" />

---

### Subscribe to a dataset

:::info
**POST** `/api/datasets/{dataset-id}/subscriptions`
:::

Subscribes the authenticated user profile to the dataset `{dataset-id}`.

By default, the subscription is configured for all dataset events (see [Subscription Type](#subscription-type) for more information).

#### Prerequisites
- Dataset `{dataset-id}` must exist

#### Query Parameters

Parameter | Required | Format | Default Value | Description
--------- | -------- | ------ | ------------- | -----------
`allMembers` | No | Boolean | `false` | Whether or not to subscribe the workspace to dataset events, enabling notifications for all [members](members) by default (applicable for the workspace owner only)


<Examples path="subscriptions/subscribe-to-a-dataset" />

#### Response
`200 OK`

[Subscription](#subscription) with HAL links.
<Snippet path="subscriptions/subscribe-to-a-dataset/response-body.md" />

---

### Subscribe to a pipeline

:::info
**POST** `/api/pipelines/{pipeline-id}/subscriptions`
:::

Subscribes the authenticated user profile to the pipeline `{pipeline-id}`.

By default, the subscription is configured for all pipeline events (see [Subscription Type](#subscription-type) for more information).

#### Prerequisites
- Pipeline `{pipeline-id}` must exist

#### Query Parameters

Parameter | Required | Format | Default Value | Description
--------- | -------- | ------ | ------------- | -----------
`allMembers` | No | Boolean | `false` | Whether or not to subscribe the workspace to pipeline events, enabling notifications for all [members](members) by default (applicable for the workspace owner only)


<Examples path="subscriptions/subscribe-to-a-pipeline" />

#### Response
`200 OK`

[Subscription](#subscription) with HAL links.
<Snippet path="subscriptions/subscribe-to-a-pipeline/response-body.md" />

---

### Update a subscription

:::info
**PUT** `/api/subscriptions/{subscription-id}`
:::

Updates the subscription `{subscription-id}`.

#### Prerequisites
- Subscription `{subscription-id}` must exist

#### Body

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`type` | `string` | [Subscription Type](#subscription-type) | The type of subscription

<Snippet path="subscriptions/update-a-subscription/request-body.md" />


<Examples path="subscriptions/update-a-subscription" />

#### Response
`200 OK`

[Subscription](#subscription) with HAL links.
<Snippet path="subscriptions/update-a-subscription/response-body.md" />

---

### Remove a subscription

:::info
**DELETE** `/api/subscriptions/{subscription-id}`
:::

Removes the subscription `{subscription-id}`.

#### Prerequisites
- Subscription `{subscription-id}` must exist

<Examples path="subscriptions/remove-a-subscription" />

#### Response
`204 No Content`

No response body provided.

---
