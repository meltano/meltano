---
title: Resources
description: Matatika resources resource reference documentation
slug: resources
---

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

<!-- {% include snippets/api/resources/view-a-resource-in-a-workspace/response-body.md %} -->

---

## Requests

### View a resource in a workspace

GET `/api/workspaces/{workspace-id}/resources/{resource-path}`

Returns the resource `{resource-path}` in the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist
- Resource `{resource-path}` must exist

#### Request
##### Example Snippets

<!-- {% include snippets/api/resources/view-a-resource-in-a-workspace/curl-request.md %} -->
<!-- {% include snippets/api/resources/view-a-resource-in-a-workspace/python-requests.md %} -->

#### Response

`200 OK`

[Resource](#resource) with HAL links.

<!-- {% include snippets/api/resources/view-a-resource-in-a-workspace/response-body.md %} -->

---

### View the content of a resource in a workspace

GET `/api/workspaces/{workspace-id}/resources/{resource-path}`

Returns the content of the resource `{resource-path}` in the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist
- Resource `{resource-path}` must exist

#### Request
##### Example Snippets

<!-- {% include snippets/api/resources/view-the-content-of-a-resource-in-a-workspace/curl-request.md %} -->
<!-- {% include snippets/api/resources/view-the-content-of-a-resource-in-a-workspace/python-requests.md %} -->

#### Response

`200 OK`

The resource content.

<!-- {% include snippets/api/resources/view-the-content-of-a-resource-in-a-workspace/response-body.md %} -->

---

### View all resources in a workspace

GET `/api/workspaces/{workspace-id}/resources`

Returns all resources in the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist
- Resource `{resource-path}` must exist

#### Request
##### Example Snippets

<!-- {% include snippets/api/resources/view-all-resources-in-a-workspace/curl-request.md %} -->
<!-- {% include snippets/api/resources/view-all-resources-in-a-workspace/python-requests.md %} -->

#### Response
`200 OK`

[Resource](#resource) collection with HAL links.

<!-- {% include snippets/api/resources/view-all-resources-in-a-workspace/response-body.md %} -->

---

### Publish multiple resources to a workspace

POST `/api/workspaces/{workspace-id}/resources`

Publishes multiple resources to the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist

#### Request
##### Example Snippets

<!-- {% include snippets/api/resources/publish-multiple-resources-to-a-workspace/curl-request.md %} -->
<!-- {% include snippets/api/resources/publish-multiple-resources-to-a-workspace/python-requests.md %} -->

#### Response
`200 OK`

[Resource](#resource) collection with HAL links.

<!-- {% include snippets/api/resources/publish-multiple-resources-to-a-workspace/response-body.md %} -->

---

### Create or update a resource in a workspace

PUT `/api/workspaces/{workspace-id}/resources/{resource-path}`

Creates or updates the resource `{resource-path}` in the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist

#### Request

##### Body
[Resource](#resource) resource.

<!-- {% include snippets/api/resources/create-or-update-a-resource-in-a-workspace/request-body.md %} -->

##### Example Snippets

<!-- {% include snippets/api/resources/create-or-update-a-resource-in-a-workspace/curl-request.md %} -->
<!-- {% include snippets/api/resources/create-or-update-a-resource-in-a-workspace/python-requests.md %} -->

#### Response
`200 OK / 201 Created`

[Resource](#resource) with HAL links.

<!-- {% include snippets/api/resources/create-or-update-a-resource-in-a-workspace/response-body.md %} -->

---

### Delete a resource in a workspace

DELETE `/api/workspaces/{workspace-id}/resources/{resource-path}`

Deletes the resource `{resource-path}` in the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist

#### Request
##### Example Snippets

<!-- {% include snippets/api/resources/delete-a-resource-in-a-workspace/curl-request.md %} -->
<!-- {% include snippets/api/resources/delete-a-resource-in-a-workspace/python-requests.md %} -->

#### Response
`204 No Content`

No response body provided.

---
