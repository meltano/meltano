---
title: Notifications
description: Meltano Cloud notifications resource reference documentation
sidebar_position: 21
---

import Examples from '@site/src/components/Examples';
import Snippet from '@site/src/components/Snippet';

Notifications are alerts triggered by certain events pertaining to a resource. To receive notifications for a specific resource, a user must have a [subscription](subscriptions) to the resource.

---

## Objects

### Notification

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`id` | `string` | Version 4 UUID | The notification ID
`created` | `string` | ISO 8601 timestamp | The instant the notification was created at
`lastModified` | `string` | ISO 8601 timestamp | The instant the notification was last modified at
`actor` | `object` | [`Member`](members#member) | The member whose action raised this notification
`type` | `string` | [Notification Type](#notification-type) | The type of notification
`resolved` | `bool` | | Whether or not the notification has been read

<Snippet path="notifications/view-a-notification/response-body.md" />

## Formats

### Notification Type

`string`

Value | Description
----- | -----------
`DATASET_ACTIVITY` | Any activity on the [dataset](datasets#dataset)
`DATASET_ANOMALY` | A detected anomaly in the [dataset](datasets#dataset) data
`DATASET_COMMENT` | A [comment](comments#comment) on the [dataset](datasets#dataset)
`DATASET_LIKE` | A [like](datasets#record-a-like-of-a-dataset) recorded on the [dataset](datasets#dataset)
`DATASET_MESSAGE` | A [message](datasets#dataset-message) about the [dataset](datasets#dataset)
`JOB_STARTED` | A [job](jobs#job) started for a [pipeline](pipelines#pipeline)
`JOB_ENDED` | A [job](jobs#job) ended for a [pipeline](pipelines#pipeline)

---

## Requests

### View all notifications

:::info
**GET** `/api/notifications?all={all}&before={before}&since={since}`
:::

Returns all notifications for the authenticated user profile.

#### Query Parameters

Parameter | Required | Format | Default Value | Description
--------- | -------- | ------ | ------------- | -----------
`all` | No | Boolean | `false` | Whether or not to return both resolved and unresolved notifications
`before` | No | ISO 8601 timestamp | The instant at which the request was made | The instant to return any notifications created before
`since` | No | ISO 8601 timestamp | `2021-02-11T11:12` | The instant to return any notifications created since


<Examples path="notifications/view-all-notifications" />

#### Response
`200 OK`

[Notification](#notification) collection with HAL links.
<Snippet path="notifications/view-all-notifications/response-body.md" />

---

### View all notifications for a workspace

:::info
**GET** `/api/workspaces/{workspaceId}/notifications?all={all}&before={before}&since={since}`
:::

Returns all notifications for the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist

#### Query Parameters

Parameter | Required | Format | Default Value | Description
--------- | -------- | ------ | ------------- | -----------
`all` | No | Boolean | | Whether or not to return both resolved and unresolved notifications
`before` | No | ISO 8601 timestamp | The instant at which the request was made | The instant to return any notifications created before
`since` | No | ISO 8601 timestamp | `2021-02-11T11:12` | The instant to return any notifications created since


<Examples path="notifications/view-all-notifications-for-a-workspace" />

#### Response
`200 OK`

[Notification](#notification) collection with HAL links.
<Snippet path="notifications/view-all-notifications-for-a-workspace/response-body.md" />

---

### View a notification

:::info
**GET** `/api/notifications/{notification-id}`
:::

Returns the notification `{notification-id}`.

#### Prerequisites
- Notification `{notification-id}` must exist

<Examples path="notifications/view-a-notification" />

#### Response
`200 OK`

[Notification](#notification) with HAL links.
<Snippet path="notifications/view-a-notification/response-body.md" />

---

### Refresh notifications

:::info
**PUT** `/api/notifications?since={since}&markAsResolved={markAsResolved}`
:::

Returns new notifications for the authenticated user profile, optionally marking existing notifications as resolved up to the moment the request was made or the supplied `since` parameter.

#### Query Parameters

Parameter | Required | Format | Default Value | Description
--------- | -------- | ------ | ------------- | -----------
`since` | No | ISO 8601 timestamp | The instant at which the request was made | The instant to fetch any new notifications from
`markAsResolved` | No | Boolean | `true` | Whether or not to mark notifications created up to `since` as resolved


<Examples path="notifications/refresh-notifications" />

#### Response
`200 OK`

[Notification](#notification) collection with HAL links.
<Snippet path="notifications/refresh-notifications/response-body.md" />

---

### Delete a notification

:::info
**DELETE** `/api/notifications/{notification-id}`
:::

Deletes the notification `{notification-id}`.

#### Prerequisites
- Notification `{notification-id}` must exist

<Examples path="notifications/delete-a-notification" />

#### Response
`204 No Content`

No response body provided.

---

##### See Also

- [Create or update a dataset message](datasets#create-or-update-a-dataset-message)
