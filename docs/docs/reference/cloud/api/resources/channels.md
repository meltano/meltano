---
title: Channels
description: Matatika Channels resource reference documentation
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Channels enable datasets to be categorised or grouped together. A single workspace can have multiple channels.

---

## Objects

### Channel

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`id` | `string` | Version 4 UUID | The channel ID
`creator` | `object` | [`Member`](members#member) | The channel creator
`workspace` | `object` | [`Workspace`](workspaces#workspace) | The channel workspace
`created` | `string` |  ISO 8601 timestamp | The channel created at timestamp
`lastModified` | `string` | ISO 8601 timestamp | The channel last modified timestamp
`name` | `string` | | The channel name
`description` | `string` | | The channel description
`picture` | `string` | URL | The channel picture metadata

<!-- {% include snippets/api/channels/view-a-channel/response-body.md %} -->

---

## Requests

### Initialise a channel

:::info
**POST** `/api/channels/{channel-id}`
:::

Initialise a channel.

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<!-- {% include snippets/api/channels/initialise-a-channel/curl-request.md %} -->

</TabItem>
<TabItem value="python" label="Python (requests)">

<!-- {% include snippets/api/channels/initialise-a-channel/python-requests.md %} -->

</TabItem>
</Tabs>

#### Response
`200 OK`

[Channel](#channel) with HAL links.
<!-- {% include snippets/api/channels/initialise-a-channel/response-body.md %} -->

---
### View a channel

:::info
**GET** `/api/channels/{channel-id}`
:::

Returns the channel `{channel-id}`.

#### Prerequisites
- Channel `{channel-id}` must exist

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<!-- {% include snippets/api/channels/view-a-channel/curl-request.md %} -->

</TabItem>
<TabItem value="python" label="Python (requests)">

<!-- {% include snippets/api/channels/view-a-channel/python-requests.md %} -->

</TabItem>
</Tabs>

#### Response
`200 OK`

[Channel](#channel) with HAL links.
<!-- {% include snippets/api/channels/view-a-channel/response-body.md %} -->

---
### View a channel in a workspace

:::info
**GET** `/api/workspaces/{workspace-id}/channels/{channel-id}`
:::

Returns a channel in the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist
- The user must be a member of the workspace `{workspace-id}`

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<!-- {% include snippets/api/channels/view-a-channel-in-a-workspace/curl-request.md %} -->

</TabItem>
<TabItem value="python" label="Python (requests)">

<!-- {% include snippets/api/channels/view-a-channel-in-a-workspace/python-requests.md %} -->

</TabItem>
</Tabs>

#### Response
`200 OK`

[Channel](#channel) with HAL links.
<!-- {% include snippets/api/channels/view-a-channel-in-a-workspace/response-body.md %} -->

---
### View all channels in a workspace

:::info
**GET** `/api/workspaces/{workspace-id}/channels/{channel-id}?type={type}&source={source}&containsDataset={datasetId}`
:::

Returns all channels in the workspace `{workspace-id}`.

#### Request
##### Query Parameters

Parameter | Required | Format | Default Value | Description
--------- | -------- | ------ | ------------- | -----------
`type` | No | string | None | Return channels by types: `list` or `source`
`source` | No | string | None | Return channels by source: `profile` or `workspace`
`containsDataset` | No | string | None | Adds a `containsDataset` boolean field to all channels returning if it contains the dataset

#### Prerequisites
- Workspace `{workspace-id}` must exist
- The user must be a member of the workspace `{workspace-id}`

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<!-- {% include snippets/api/channels/view-all-channels-in-a-workspace/curl-request.md %} -->

</TabItem>
<TabItem value="python" label="Python (requests)">

<!-- {% include snippets/api/channels/view-all-channels-in-a-workspace/python-requests.md %} -->

</TabItem>
</Tabs>

#### Response
`200 OK`

[Channel](#channel) collection with HAL links.
<!-- {% include snippets/api/channels/view-all-channels-in-a-workspace/response-body.md %} -->

---
### Create or Update a channel in a workspace

:::info
**PUT** `/api/workspaces/{workspace-id}/channels/{channel-id}`
:::

Creates or Updates a channel in the workspace `{workspace-id}`.

This endpoint takes a `{channel-id}` (UUID) and based on the supplied value and the channels that already exist in the workspace, will update or create a channel accordingly.

#### Prerequisites
- Workspace `{workspace-id}` must exist
- The user must be a admin in the workspace `{workspace-id}`

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<!-- {% include snippets/api/channels/create-a-channel-in-a-workspace-by-id/curl-request.md %} -->

</TabItem>
<TabItem value="python" label="Python (requests)">

<!-- {% include snippets/api/channels/create-a-channel-in-a-workspace-by-id/python-requests.md %} -->

</TabItem>
</Tabs>

#### Response
`200 OK / 201 Created`

[Channel](#channel) with HAL links.
<!-- {% include snippets/api/channels/create-a-channel-in-a-workspace-by-id/response-body.md %} -->

---
### Delete a channel

:::info
**DELETE** `/api/channels/{channel-id}`
:::

Delete a channel.

#### Prerequisites
- The user must be a admin of the workspace the channel is in.

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<!-- {% include snippets/api/channels/delete-a-channel/curl-request.md %} -->

</TabItem>
<TabItem value="python" label="Python (requests)">

<!-- {% include snippets/api/channels/delete-a-channel/python-requests.md %} -->

</TabItem>
</Tabs>

#### Response
`204 No Content`

No response body provided.

---
### View all channels in your workspace news

:::info
**GET** `/api/channels/{channel-id}`
:::

Returns all channels in your news for the workspace.

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<!-- {% include snippets/api/channels/channels-in-news/curl-request.md %} -->

</TabItem>
<TabItem value="python" label="Python (requests)">

<!-- {% include snippets/api/channels/channels-in-news/python-requests.md %} -->

</TabItem>
</Tabs>

#### Response
`200 OK`

[Channels](#channel) in your workspace news.
<!-- {% include snippets/api/channels/channels-in-news/response-body.md %} -->

---
### Add a dataset to a list channel

:::info
**PUT** `/api/channels/{channel-id}/datasets/{dataset-id}`
:::

Adds a dataset to a channel with type list.

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<!-- {% include snippets/api/channels/add-dataset-to-list-channel/curl-request.md %} -->

</TabItem>
<TabItem value="python" label="Python (requests)">

<!-- {% include snippets/api/channels/add-dataset-to-list-channel/python-requests.md %} -->

</TabItem>
</Tabs>

#### Response
`201 Created`

No response body provided.

---
### Remove a dataset from a list channel

:::info
**DELETE** `/api/channels/{channel-id}/datasets/{dataset-id}`
:::

Removes a dataset from a channel with type list.

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<!-- {% include snippets/api/channels/remove-dataset-from-list-channel/curl-request.md %} -->

</TabItem>
<TabItem value="python" label="Python (requests)">

<!-- {% include snippets/api/channels/remove-dataset-from-list-channel/python-requests.md %} -->

</TabItem>
</Tabs>

#### Response
`204 No Content`

No response body provided.

---
### Add workspace scope to a channel

:::info
**PUT** `/api/channels/{channel-id}/scope/workspace`
:::

Add workspace scope to a channel.

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<!-- {% include snippets/api/channels/add-workspace-scope-to-a-channel/curl-request.md %} -->

</TabItem>
<TabItem value="python" label="Python (requests)">

<!-- {% include snippets/api/channels/add-workspace-scope-to-a-channel/python-requests.md %} -->

</TabItem>
</Tabs>

#### Response
`200 OK`

[Channel](#channel) with HAL links.
<!-- {% include snippets/api/channels/add-workspace-scope-to-a-channel/response-body.md %} -->

---
### Withdraw workspace scope from a channel

:::info
**PUT** `/api/channels/{channel-id}/scope/profile`
:::

Withdraw workspace scope from a channel.

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<!-- {% include snippets/api/channels/withdraw-workspace-scope-from-a-channel/curl-request.md %} -->

</TabItem>
<TabItem value="python" label="Python (requests)">

<!-- {% include snippets/api/channels/withdraw-workspace-scope-from-a-channel/python-requests.md %} -->

</TabItem>
</Tabs>

#### Response
`200 OK`

[Channel](#channel) with HAL links.
<!-- {% include snippets/api/channels/withdraw-workspace-scope-from-a-channel/response-body.md %} -->

---

##### See Also

- [Subscribe to a channel](subscriptions#subscribe-to-a-channel)
