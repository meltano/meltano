---
title: Workspaces
description: Matatika Workspaces resource reference documentation
---

Workspaces allow users to operate within isolated instances of the Matatika service. This is useful for separating profiles based on the data they require access to.

---

## Objects

### Workspace

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`id` | `string` | Version 4 UUID | The workspace ID
`created` | `string` | ISO 8601 timestamp | The instant the workspace was created
`lastModified` | `string` | ISO 8601 timestamp | The instant the workspace was last modified
`alias` | `string` | | The workspace alias and database schema name
`name` | `string` | | The workspace name
`domains` | `string[]` | Array of domain hosts | The workspace allowed domains
`repositoryUrl` | `string` | URL | The workspace repository URL
`pipelinesImage` | `string` | Container image name path | The path name of an image to run pipelines from
`imageUrl` | `string` | Image [data URL](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URIs) | The workspace image data URL
`status` | `string` | [Workspace Status](#workspace-status) | The workspace status
`defaultWorkspace` | `bool` | | Whether or not the workspace is set as the default the authenticated user

<!-- {% include snippets/api/workspaces/view-a-workspace/response-body.md %} -->

## Formats

### Workspace Status

`string`

Value | Description
----- | -----------
`READY` | The workspace completed processing resource changes
`PROVISIONING` | The workspace is processing resource changes
`FAILED` | The workspace failed to process resource changes

---

## Requests

### View all workspaces

GET `/api/workspaces`

Returns all workspaces the authenticated user profile is an owner or member of.

#### Request
##### Example Snippets
cURL

<!-- {% include snippets/api/workspaces/view-all-workspaces/curl-request.md %} -->

Python (`requests`)

<!-- {% include snippets/api/workspaces/view-all-workspaces/python-requests.md %} -->

#### Response
`200 OK`

[Workspace](#workspace) collection with HAL links.
<!-- {% include snippets/api/workspaces/view-all-workspaces/response-body.md %} -->

---
### View a workspace

GET `/api/workspaces/{workspace-id}`

Returns the workspace `{workspace-id}`.

#### Prerequisites

- The user must be a member of the workspace `{workspace-id}`

#### Request
##### Example Snippets
cURL

<!-- {% include snippets/api/workspaces/view-a-workspace/curl-request.md %} -->

Python (`requests`)

<!-- {% include snippets/api/workspaces/view-a-workspace/python-requests.md %} -->

#### Response
`200 OK`

[Workspace](#workspace) with HAL links.
<!-- {% include snippets/api/workspaces/view-a-workspace/response-body.md %} -->

---
### Initialise a workspace

POST `/api/workspaces`

Initialises a new workspace.

#### Request
##### Example Snippets
cURL

<!-- {% include snippets/api/workspaces/initialise-a-workspace/curl-request.md %} -->

Python (`requests`)

<!-- {% include snippets/api/workspaces/initialise-a-workspace/python-requests.md %} -->

#### Response
`200 OK`

[Workspace](#workspace) with HAL links.
<!-- {% include snippets/api/workspaces/initialise-a-workspace/response-body.md %} -->

---
### Create a workspace

PUT `/api/workspaces/{workspace-id}`

Creates the workspace `{workspace-id}`.

#### Prerequisites

- The user must be the owner of workspace `{workspace-id}`
- The workspace must have been [initialised](#initialise-a-workspace) in order to create it

#### Request
##### Body
[Workspace](#workspace) resource.
<!-- {% include snippets/api/workspaces/create-a-workspace/request-body.md %} -->

##### Example Snippets
cURL

<!-- {% include snippets/api/workspaces/create-a-workspace/curl-request.md %} -->

Python (`requests`)

<!-- {% include snippets/api/workspaces/create-a-workspace/python-requests.md %} -->

#### Response
`201 Created`

[Workspace](#workspace) with HAL links.
<!-- {% include snippets/api/workspaces/create-a-workspace/response-body.md %} -->

---
### Update a workspace

PUT `/api/workspaces/{workspace-id}`

Updates the workspace `{workspace-id}`.

#### Prerequisites

- The user must be the owner of workspace `{workspace-id}`
- The workspace must have been [created](#create-a-workspace) in order to update it

#### Request
##### Body
[Workspace](#workspace) resource.
<!-- {% include snippets/api/workspaces/update-a-workspace/request-body.md %} -->

##### Example Snippets
cURL

<!-- {% include snippets/api/workspaces/update-a-workspace/curl-request.md %} -->

Python (`requests`)

<!-- {% include snippets/api/workspaces/update-a-workspace/python-requests.md %} -->

#### Response
`200 OK`

[Workspace](#workspace) with HAL links.
<!-- {% include snippets/api/workspaces/update-a-workspace/response-body.md %} -->

---
### Delete a workspace

DELETE `/api/workspaces/{workspace-id}`

Deletes the workspace `{workspace-id}`.

#### Prerequisites

- The user must be the owner of workspace `{workspace-id}`

#### Request
##### Example Snippets
cURL

<!-- {% include snippets/api/workspaces/delete-a-workspace/curl-request.md %} -->

Python (`requests`)

<!-- {% include snippets/api/workspaces/delete-a-workspace/python-requests.md %} -->

#### Response
`204 No Content`

No response body provided.

---

##### See Also

- [Set a workspace as default](profiles#set-a-workspace-as-default)
- [View all invitations to a workspace](invitations#view-all-invitations-to-a-workspace)
- [Create an invitation to a workspace](invitations#create-an-invitation-to-a-workspace)
- [Cancel an invitation](invitations#withdraw-an-invitation)
- [View all members of a workspace](members#view-all-members-of-a-workspace)
- [View a member of a workspace](members#view-a-member-of-a-workspace)
- [View all channels in a workspace](channels#view-all-channels-in-a-workspace)
- [View all liked datasets in a workspace](datasets#view-all-liked-datasets-in-a-workspace)
- [View the feed of a workspace](feed#view-the-feed-of-a-workspace)
- [View all pipelines in a workspace](pipelines#view-all-pipelines-in-a-workspace)
- [View a pipeline](pipelines#view-a-pipeline)
- [Initialise a pipeline in a workspace](pipelines#initialise-a-pipeline-in-a-workspace)
- [Create or update a pipeline in a workspace](pipelines#create-or-update-a-pipeline-in-a-workspace)
- [Delete a pipeline](pipelines#delete-a-pipeline)
- [View all running or completed jobs for a workspace](jobs#view-all-running-or-completed-jobs-for-a-workspace)
