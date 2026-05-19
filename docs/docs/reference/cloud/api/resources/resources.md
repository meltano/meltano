---
title: Resources
description: Meltano Cloud resources resource reference documentation
slug: resources
sidebar_position: 24
---

import Examples from '@site/src/components/Examples'
import Snippet from '@site/src/components/Snippet'

Resources are files that are managed by a workspace. A resource is accessible from `/api/workspaces/{workspace-id}/resources` by its `path`.

---

## Objects

### Resource

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`path` | `string` | | The resource path
`created` | `string` | ISO 8601 timestamp | The instant the resource was created at
`lastModified` | `string` | ISO 8601 timestamp | The instant the resource was last modified at
`contentType` | `string` | [MIME type](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types) | The content type of the resource
`content` | `string` | | The content of the resource

<Snippet path="resources/view-a-resource-in-a-workspace/response-body.md" />

---

## Requests

### View a resource in a workspace

:::info
**GET** `/api/workspaces/{workspace-id}/resources/{resource-path}`
:::

Returns the resource `{resource-path}` in the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist
- Resource `{resource-path}` must exist

<Examples path="resources/view-a-resource-in-a-workspace" />

#### Response

`200 OK`

[Resource](#resource) with HAL links.

<Snippet path="resources/view-a-resource-in-a-workspace/response-body.md" />

---

### View the content of a resource in a workspace

:::info
**GET** `/api/workspaces/{workspace-id}/resources/{resource-path}`
:::

Returns the content of the resource `{resource-path}` in the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist
- Resource `{resource-path}` must exist

<Examples path="resources/view-the-content-of-a-resource-in-a-workspace" />

#### Response

`200 OK`

The resource content.

<Snippet path="resources/view-the-content-of-a-resource-in-a-workspace/response-body.md" />

---

### View all resources in a workspace

:::info
**GET** `/api/workspaces/{workspace-id}/resources`
:::

Returns all resources in the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist
- Resource `{resource-path}` must exist

<Examples path="resources/view-all-resources-in-a-workspace" />

#### Response
`200 OK`

[Resource](#resource) collection with HAL links.

<Snippet path="resources/view-all-resources-in-a-workspace/response-body.md" />

---

### Publish multiple resources to a workspace

:::info
**POST** `/api/workspaces/{workspace-id}/resources`
:::

Publishes multiple resources to the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist

<Examples path="resources/publish-multiple-resources-to-a-workspace" />

#### Response
`200 OK`

[Resource](#resource) collection with HAL links.

<Snippet path="resources/publish-multiple-resources-to-a-workspace/response-body.md" />

---

### Create or update a resource in a workspace

:::info
**PUT** `/api/workspaces/{workspace-id}/resources/{resource-path}`
:::

Creates or updates the resource `{resource-path}` in the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist


#### Body
[Resource](#resource) resource.

<Snippet path="resources/create-or-update-a-resource-in-a-workspace/request-body.md" />

<Examples path="resources/create-or-update-a-resource-in-a-workspace" />

#### Response
`200 OK / 201 Created`

[Resource](#resource) with HAL links.

<Snippet path="resources/create-or-update-a-resource-in-a-workspace/response-body.md" />

---

### Delete a resource in a workspace

:::info
**DELETE** `/api/workspaces/{workspace-id}/resources/{resource-path}`
:::

Deletes the resource `{resource-path}` in the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist

<Examples path="resources/delete-a-resource-in-a-workspace" />

#### Response
`204 No Content`

No response body provided.

---
