---
title: Datasets
description: Meltano Cloud datasets resource reference documentation
sidebar_position: 8
---

import Examples from '@site/src/components/Examples';
import Snippet from '@site/src/components/Snippet';

Datasets are modules of data that can be published to workspaces. Datasets are visualised in Meltano Cloud following the [Chart.js](https://www.chartjs.org/) specifications.

---

## Objects

### Dataset

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`id` | `string` | Version 4 UUID | The dataset ID
`published` | `string` | ISO 8601 timestamp | The instant the dataset was published
`alias` | `string` | | The dataset alias
`workspaceId` | `string` | Version 4 UUID | The workspace ID of the published dataset
`source` | `string` | | The channel ID where the dataset was initially published to
`title` | `string` | | The dataset title
`description` | `string` | | The dataset description (may contain markdown)
`questions` | `string` | | The dataset questions
`rawData` | `string` | JSON | The dataset raw data
`visualisation` | `string` | JSON | The dataset visualisation metadata. [More Info](/reference/cloud/dataml/datasetml/visualisation)
`metadata` | `string` | JSON | The dataset metadata. [More Info](/reference/cloud/dataml/datasetml/metadata)
`query` | `string` | SQL statement | The dataset query. [More Info](/reference/cloud/dataml/datasetml/query)
`likeCount` | `number` | Unsigned integer | The number of likes the dataset has received
`likedByProfiles` | `object[]` | Array of [`Member`](members#member)s | The members that have liked the dataset
`commentCount` | `number` | Unsigned integer | The number of comments the dataset has received
`viewCount` | `number` | Unsigned integer | The number of views the dataset has received
`created` | `string` | ISO 8601 timestamp | The instant the dataset was create
`score` | `number` | Decimal | The dataset score used to determine its position in the workspace [Feed](feed)

<Snippet path="datasets/view-a-dataset/response-body.md" />

### Dataset Message

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`id` | `string` | Version 4 UUID | The dataset message ID (shared with the resulting [notification](notifications))
`recipientId` | `string` | | The recipient profile ID
`message` | `string` | | The dataset message content
`datasetId` | `string` | Version 4 UUID | The message subject dataset ID

<Snippet path="datasets/create-or-update-a-dataset-message/response-body.md" />

---

## Requests

### View all datasets in a workspace

:::info
**GET** `/api/workspaces/{workspace-id}/datasets`
:::

Returns all datasets in the workspace `{workspace-id}`.

#### Prerequisites

- The user must be a member of the workspace `{workspace-id}`

<Examples path="datasets/view-all-datasets-in-a-workspace" />

#### Response
`200 OK`

[Dataset](#dataset) collection with HAL links.
<Snippet path="datasets/view-all-datasets-in-a-workspace/response-body.md" />

---

### View all liked datasets in a workspace

:::info
**GET** `/api/workspaces/{workspace-id}/liked`
:::

Returns all datasets in the workspace `{workspace-id}` liked by the authenticated profile.

#### Prerequisites

- The user must be a member of the workspace `{workspace-id}`

<Examples path="datasets/view-datasets-in-a-workspace-liked-by-profile" />

#### Response
`200 OK`

[Dataset](#dataset) collection with HAL links.
<Snippet path="datasets/view-datasets-in-a-workspace-liked-by-profile/response-body.md" />

---

### View datasets by channel

:::info
**GET** `/api/channels/{channel-id}/datasets`
:::

Returns datasets by the channel `{channel-id}`.

#### Prerequisites

- Channel `{channel-id}` must exist

<Examples path="datasets/view-datasets-by-channel" />

#### Response
`200 OK`

[Dataset](#dataset) collection with HAL links.
<Snippet path="datasets/view-datasets-by-channel/response-body.md" />

---

### View a dataset

:::info
**GET** `/api/datasets/{dataset-id}`
:::

Returns the dataset `{dataset-id}`.

#### Prerequisites
- Dataset `{dataset-id}` must exist

<Examples path="datasets/view-a-dataset" />

#### Response
`200 OK`

[Dataset](#dataset) with HAL links.
<Snippet path="datasets/view-a-dataset/response-body.md" />

---

### View a dataset in a workspace

:::info
**GET** `/api/workspaces/{workspace-id}/datasets/{dataset-id-or-alias}`
:::

Returns the dataset `{dataset-id-or-alias}` in the workspace `{workspace-id}`.

#### Prerequisites

- The user must be a member of the workspace `{workspace-id}`
- Dataset `{dataset-id-or-alias}` must exist within the workspace `{workspace-id}`

<Examples path="datasets/view-a-dataset-in-a-workspace" />

#### Response
`200 OK`

[Dataset](#dataset) with HAL links.
<Snippet path="datasets/view-a-dataset-in-a-workspace/response-body.md" />

---

### View the data of a dataset

:::info
**GET** `/api/datasets/{dataset-id}/data`
:::

Returns the data of the dataset `{dataset-id}`.

#### Prerequisites
- Dataset `{dataset-id}` must exist

#### Headers
##### `Accept`

Media Type(s) | Description
------------- | -----------
`application/json` `*/*` | Sets the response content type format to JSON
`text/csv` | Sets the response content type format to CSV

Defaults to `application/json` (given `Accept */*` or no `Accept` header).


<Examples path="datasets/view-the-data-of-a-dataset" />

#### Response
- `200`: The dataset data (defaults to JSON format).

<Snippet path="datasets/view-the-data-of-a-dataset/response-body.md" />

- `204`: No response body provided.

---

### Publish a dataset to a workspace

:::info
**POST** `/api/workspaces/{workspace-id}/datasets`
:::

Publishes a dataset to the workspace `{workspace-id}`.

#### Prerequisites

- The user must be a member of the workspace `{workspace-id}`

<Examples path="datasets/publish-a-dataset-to-a-workspace">

Making the request with an existing `id` or `alias` will result in the respective dataset being overwritten.

[Dataset](#dataset) resource.
<Snippet path="datasets/publish-a-dataset-to-a-workspace/request-body.md" />

</Examples>
#### Response
`200 OK / 201 Created`

[Dataset](#dataset) with HAL links.
<Snippet path="datasets/publish-a-dataset-to-a-workspace/response-body.md" />

---

### Edit a dataset

:::info
**PATCH** `/api/datasets/{dataset-id}`
:::

Edits the dataset `{dataset-id}`.

#### Prerequisites
- Dataset `{dataset-id}` must exist

#### Body

This request can update one or more of the [dataset](#dataset) fields at once. With a single request, it is possible to - *for example* - edit the dataset `title` only, or both `title` and `description` (shown below).

<Snippet path="datasets/edit-a-dataset/request-body.md" />


<Examples path="datasets/edit-a-dataset" />

#### Response
`200 OK`

[Dataset](#dataset) with HAL links.
<Snippet path="datasets/edit-a-dataset/response-body.md" />

---

### Record a view of a dataset

:::info
**PUT** `/api/datasets/{dataset-id}/view`
:::

"Adds a view to the dataset `{dataset-id}`.

#### Prerequisites

- Dataset `{dataset-id}` must exist

<Examples path="datasets/record-a-view-of-a-dataset" />

#### Response
`200 OK`

No response body provided.

---

### Record a like of a dataset

:::info
**PUT** `/api/datasets/{dataset-id}/like`
:::

Records a like of the dataset `{dataset-id}` from the authenticated user profile.

#### Prerequisites

- Dataset `{dataset-id}` must exist

<Examples path="datasets/record-a-like-of-a-dataset" />

#### Response
`200 OK`

No response body provided.

---

### Remove a like from a dataset

:::info
**DELETE** `/api/datasets/{dataset-id}/like`
:::

Removes a like of the dataset `{dataset-id}` from the authenticated user profile.

#### Prerequisites

- Dataset `{dataset-id}` must exist

<Examples path="datasets/remove-a-like-from-a-dataset" />

#### Response
`204 No Content`

No response body provided.

---

### Initialise a new dataset message

:::info
**POST** `/api/datasets/{dataset-id}/messages`
:::

Initialises a new dataset message for the dataset `{dataset-id}`

#### Prerequisites
- Dataset `{dataset-id}` must exist


<Examples path="datasets/initialise-a-new-dataset-message" />

#### Response
`200 OK`

[Dataset Message](#dataset-message) with HAL links.
<Snippet path="datasets/initialise-a-new-dataset-message/response-body.md" />

---

### Create or update a dataset message

:::info
**PUT** `/api/datasets/{dataset-id}/messages/{message-id}`
:::

Creates or updates the dataset message `{message-id}` for the dataset `{dataset-id}`. This appears as [`DATASET_MESSAGE`](notifications#notification-type) [notification](notifications) for the recipient.

#### Prerequisites
- Dataset `{dataset-id}` must exist

#### Body
[Dataset Message](#dataset-message) resource.
<Snippet path="datasets/create-or-update-a-dataset-message/request-body.md" />


<Examples path="datasets/create-or-update-a-dataset-message" />

#### Response
`200 OK / 201 Created`

[Dataset Message](#dataset-message) with HAL links.
<Snippet path="datasets/create-or-update-a-dataset-message/response-body.md" />

---

### Delete a dataset

:::info
**DELETE** `/api/datasets/{dataset-id}`
:::

Deletes the dataset `{dataset-id}`.

#### Prerequisites

- Dataset `{dataset-id}` must exist

<Examples path="datasets/delete-a-dataset" />

#### Response
`204 No Content`

No response body provided.

Further Reading:

- [Meltano Cloud dataset YAML file](/reference/cloud/dataml/datasetml/)
- [Example Charts](/reference/cloud/dataml/datasetml/basic-examples)

---

##### See Also

- [View all comments on a dataset](comments#view-all-comments-on-a-dataset)
- [Search for datasets in a workspace by free text](search#search-for-datasets-in-a-workspace-by-free-text)
- [Search for datasets in a workspace by channel name](search#search-for-datasets-in-a-workspace-by-channel-name)
- [Search for datasets in a workspace by tag name](search#search-for-datasets-in-a-workspace-by-tag-name)
- [Subscribe to a dataset](subscriptions#subscribe-to-a-dataset)
