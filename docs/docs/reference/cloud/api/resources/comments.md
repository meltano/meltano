---
title: Comments
description: Meltano Cloud comments resource reference documentation
sidebar_position: 10
---

import Examples from '@site/src/components/Examples';
import Snippet from '@site/src/components/Snippet';

Comments aid conversation and collaboration around workspace datasets. Comments can be made on datasets, or other comments to form threads.

---

## Objects

### Comment

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`id` | `string` | Version 4 UUID | The comment ID
`message` | `string` | | The comment message
`likeCount` | `number` | Unsigned integer | The number of likes the comment has received
`likedByProfiles` | `object[]` | Array of [`Member`](members#member)s | The workspace members that have liked the comment
`created` | `string` | ISO 8601 timestamp | Timestamp denoting when the comment was created
`lastModified` | `string` | ISO 8601 timestamp | Timestamp denoting when the comment was last modified
`from` | `object` | [`Member`](members#member) | The comment author
`commentCount` | `number` | Unsigned integer | The number of replies the comment has received
`datasetId` | `string` | Version 4 UUID | The ID of the dataset comment subject
`parentId` | `string` | Version 4 UUID | The ID of the parent comment

<Snippet path="comments/view-a-comment/response-body.md" />

---

## Requests

### View all comments on a dataset

:::info
**GET** `/api/datasets/{dataset-id}/comments`
:::

Returns all comments on the dataset `{dataset-id}`.

#### Prerequisites

- Dataset `{dataset-id}` must exist

<Examples path="comments/view-all-comments-on-a-dataset" />

#### Response
`200 OK`

[Comment](comments#comment) collection with HAL links.
<Snippet path="comments/view-all-comments-on-a-dataset/response-body.md" />

---

### View a comment

:::info
**GET** `/api/comments/{comment-id}`
:::

Returns the comment `{comment-id}`.

#### Prerequisites

- Comment `{comment-id}` must exist

<Examples path="comments/view-a-comment" />

#### Response
`200 OK`

[Comment](comments#comment) with HAL links.
<Snippet path="comments/view-a-comment/response-body.md" />

---

### View the edit history of a comment

:::info
**GET** `/api/comments/{comment-id}/history`
:::

Returns the edit history of the comment `{comment-id}`.

#### Prerequisites

- Comment `{comment-id}` must exist

<Examples path="comments/view-the-edit-history-of-a-comment" />

#### Response
`200 OK`

<Snippet path="comments/view-the-edit-history-of-a-comment/response-body.md" />

---

### View all replies to a comment

:::info
**GET** `/api/comments/{comment-id}`
:::

Returns all replies to the comment `{comment-id}`.

#### Prerequisites

- Comment `{comment-id}` must exist

<Examples path="comments/view-all-replies-to-a-comment" />

#### Response
`200 OK`

[Comment](comments#comment) with HAL links.
<Snippet path="comments/view-all-replies-to-a-comment/response-body.md" />

---

### Initialise a comment on a dataset

:::info
**POST** `/api/datasets/{dataset-id}/comments`
:::

Initialises a new comment on the dataset `{dataset-id}`.

#### Prerequisites

- Dataset `{dataset-id}` must exist

<Examples path="comments/initialise-a-comment-on-a-dataset" />

#### Response
`200 OK`

[Comment](comments#comment) with HAL links.
<Snippet path="comments/initialise-a-comment-on-a-dataset/response-body.md" />

---

### Initialise a reply to a comment

:::info
**POST** `/api/comments/{comment-id}`
:::

Initialises a new reply comment to the comment `{comment-id}`.

#### Prerequisites

- Comment `{comment-id}` must exist

<Examples path="comments/initialise-a-reply-to-a-comment" />

#### Response
`200 OK`

[Comment](comments#comment) with HAL links.
<Snippet path="comments/initialise-a-reply-to-a-comment/response-body.md" />

---

### Create a comment

:::info
**PUT** `/api/comments/{comment-id}`
:::

Creates the comment `{comment-id}`.

#### Prerequisites

- The comment must have been initialised in order to create it
- The target dataset `{dataset-id}` or comment `{comment-id}` must exist

#### Body
[Comment](#comment) resource.
<Snippet path="comments/create-a-comment/request-body.md" />


<Examples path="comments/create-a-comment" />

#### Response
`201 Created`

[Comment](#comment) with HAL links.
<Snippet path="comments/create-a-comment/response-body.md" />

---

### Update a comment

:::info
**PUT** `/api/comments/{comment-id}`
:::

Updates the comment `{comment-id}`.

#### Prerequisites

- Comment `{comment-id}` must exist

#### Body
[Comment](#comment) resource.
<Snippet path="comments/update-a-comment/request-body.md" />


<Examples path="comments/view-a-comment" />

#### Response
`200 OK`

[Comment](comments#comment) with HAL links.
<Snippet path="comments/view-a-comment/response-body.md" />

---

### Record a like of a comment

:::info
**PUT** `/api/comments/{comment-id}/like`
:::

Records a like of the comment `{comment-id}` from the authenticated user profile.

#### Prerequisites

- Comment `{comment-id}` must exist

<Examples path="comments/record-a-like-of-a-comment" />

#### Response
`200 OK`

No response body provided.

---

### Remove a like from a comment

:::info
**DELETE** `/api/comments/{comment-id}/like`
:::

Removes a like of the comment `{comment-id}` from the authenticated user profile.

#### Prerequisites

- Comment `{comment-id}` must exist

<Examples path="comments/remove-a-like-from-a-comment" />

#### Response
`204 No Content`

No response body provided.

---

### Delete a comment

:::info
**DELETE** `/api/comments/{comment-id}`
:::

Deletes the comment `{comment-id}`.

#### Prerequisites

- Comment `{comment-id}` must exist

<Examples path="comments/delete-a-comment" />

#### Response
`204 No Content`

No response body provided.

---
