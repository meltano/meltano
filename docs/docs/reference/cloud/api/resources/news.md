---
title: News
description: Meltano Cloud news resource reference documentation
sidebar_position: 14
---

News is a collection of [notifications](notifications) resulting from all configured [subscriptions](subscriptions). News is used to form a feed of [datasets](datasets#dataset) specific to the authenticated user profile, in the context of a [workspace](workspaces).

---

## Requests

### View the news for a workspace

:::info
**GET** `/api/workspaces/{workspace-id}/news?before={before}&since={since}`
:::

Returns the news for the workspace `{workspace-id}`.

Unlike [View all notifications](notifications#view-all-notifications), this returns all notifications triggered by subscriptions configured for both the workspace and authenticated user profile.

#### Query Parameters

Parameter | Required | Format | Default Value | Description
--------- | -------- | ------ | ------------- | -----------
`before` | No | ISO 8601 timestamp | The instant at which the request was made | The instant to return any notifications created before
`since` | No | ISO 8601 timestamp | `2021-02-11T11:12` | The instant to return any notifications created since
`q` | No | Tag [filter](/reference/cloud/api/links#filter) | | The tag(s) to search notifications by

#### Response
`200 OK`

[Notification](notifications#notification) collection with HAL links.

---

##### See Also

- [View all tags in the news for a workspace](tags#view-all-tags-in-the-news-for-a-workspace)
