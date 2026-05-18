---
title: Dataplugins
description: Matatika Dataplugins resource reference documentation
---

Dataplugins simply define a source of data from a given repository. Matatika provides a number of pre-configured platform-wide dataplugins out-the-box, as well as the ability to create custom dataplugins through the API. From these, [pipeline](pipelines) jobs can be run to inject data into a workspace.

---

## Objects

### Dataplugin

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`id` | `string` | Version 4 UUID | The dataplugin ID
`name` | `string` | | The dataplugin name
`description` | `string` | | A description of the dataplugin
`repositoryUrl` | `string` | URL | The dataplugin repository URL
`settings` | `object[]` | Array of [`Setting`](#setting)s | The dataplugin settings

<!-- {% include snippets/api/dataplugins/view-a-dataplugin/response-body.md %} -->

### Setting

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`name` | `string` | | The setting name
`value` | `string` | | The setting default value
`label` | `string` | | The setting label
`protected` | `bool` | | The setting protection status
`kind` | `string` | [Setting Kind](#setting-kind) | The setting kind
`description` | `string` | | A description of the setting
`placeholder` | `string` | | The setting placeholder text
`envAliases` | `string[]` | | Environment variable aliases for the setting
`documentation` | `string` | URL | The setting documentation URL
`oauth` | [`OAuth`](#oauth) | | The setting OAuth configuration
`env` | `string` | | 

### OAuth

Path | JSON Type | Format | Description
---- | ---- | ------- | -----------
`provider` | `string` | | The OAuth provider

## Formats

### Setting Kind

`string`

Value | Description
----- | -----------
`STRING` | String setting
`INTEGER` | Integer setting
`PASSWORD` | Password setting 
`HIDDEN` | Hidden setting
`BOOLEAN` | Boolean setting
`DATE_ISO8601` | ISO 8601 date setting
`EMAIL` | Email setting
`OAUTH` | OAuth setting
`FILE` | File setting
`ARRAY` | Array setting

---

## Requests

### View all supported dataplugins

GET `/api/dataplugins`

Returns all dataplugins supported by Matatika.

#### Request
##### Example Snippets
cURL

<!-- {% include snippets/api/dataplugins/view-all-supported-dataplugins/curl-request.md %} -->

Python (`requests`)

<!-- {% include snippets/api/dataplugins/view-all-supported-dataplugins/python-requests.md %} -->

#### Response
`200 OK`

[Dataplugin](#dataplugin) collection with HAL links.
<!-- {% include snippets/api/dataplugins/view-all-supported-dataplugins/response-body.md %} -->

---
### View the Matatika `discovery.yml`

GET `/api/discovery.yml`

Returns a [Meltano `discovery.yml`](https://docs.meltano.com/reference/settings#discovery_url) containing all dataplugins supported by Matatika.

#### Request
##### Example Snippets
cURL

<!-- {% include snippets/api/dataplugins/view-the-matatika-discovery-yml/curl-request.md %} -->

Python (`requests`)

<!-- {% include snippets/api/dataplugins/view-the-matatika-discovery-yml/python-requests.md %} -->

#### Response
`200 OK`

[Meltano `discovery.yml`](https://docs.meltano.com/reference/settings#discovery_url).
<!-- {% include snippets/api/dataplugins/view-the-matatika-discovery-yml/response-body.md %} -->

---
### View all workspace dataplugins

GET `/api/workspaces/{workspace-id}/dataplugins`

Returns all dataplugins available to the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist

#### Request
##### Example Snippets
cURL

<!-- {% include snippets/api/dataplugins/view-all-workspace-dataplugins/curl-request.md %} -->

Python (`requests`)

<!-- {% include snippets/api/dataplugins/view-all-workspace-dataplugins/python-requests.md %} -->

#### Response
`200 OK`

[Dataplugin](#dataplugin) collection with HAL links.
<!-- {% include snippets/api/dataplugins/view-all-workspace-dataplugins/response-body.md %} -->

---
### View a workspace `discovery.yml`

GET `/api/workspaces/{workspace-id}/discovery.yml`

Returns a [Meltano `discovery.yml`](https://docs.meltano.com/reference/settings#discovery_url) containing all dataplugins available to the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist

#### Request
##### Example Snippets
cURL

<!-- {% include snippets/api/dataplugins/view-a-workspace-discovery-yml/curl-request.md %} -->

Python (`requests`)

<!-- {% include snippets/api/dataplugins/view-a-workspace-discovery-yml/python-requests.md %} -->

#### Response
`200 OK`

[Meltano `discovery.yml`](https://docs.meltano.com/reference/settings#discovery_url).
<!-- {% include snippets/api/dataplugins/view-a-workspace-discovery-yml/response-body.md %} -->

---
### View a dataplugin

GET `/api/dataplugins/{dataplugin-id}`

Returns the dataplugin `{dataplugin-id}`.

#### Prerequisites
- Dataplugin `{dataplugin-id}` must exist

#### Request
##### Example Snippets
cURL

<!-- {% include snippets/api/dataplugins/view-a-dataplugin/curl-request.md %} -->

Python (`requests`)

<!-- {% include snippets/api/dataplugins/view-a-dataplugin/python-requests.md %} -->

#### Response
`200 OK`

[Dataplugin](#dataplugin) with HAL links.
<!-- {% include snippets/api/dataplugins/view-a-dataplugin/response-body.md %} -->

---
### Initialise a new dataplugin

POST `/api/dataplugins`

Initialises a new dataplugin.

#### Request
##### Example Snippets
cURL

<!-- {% include snippets/api/dataplugins/initialise-a-new-dataplugin/curl-request.md %} -->

Python (`requests`)

<!-- {% include snippets/api/dataplugins/initialise-a-new-dataplugin/python-requests.md %} -->

#### Response
`200 OK`

[Dataplugin](#dataplugin) with HAL links.
<!-- {% include snippets/api/dataplugins/initialise-a-new-dataplugin/response-body.md %} -->

---
### Publish dataplugins from a `discovery.yml`

POST `/api/workspaces/{workspace-id}/discovery.yml`

Publishes dataplugins from a [Meltano `discovery.yml`](https://docs.meltano.com/reference/settings#discovery_url).

#### Prerequisites
- Workspace `{workspace-id}` must exist

#### Request

##### Body
[Meltano `discovery.yml`](https://docs.meltano.com/reference/settings#discovery_url)
<!-- {% include snippets/api/dataplugins/publish-dataplugins-from-a-discovery-yml/request-body.md %} -->

##### Example Snippets
cURL

<!-- {% include snippets/api/dataplugins/publish-dataplugins-from-a-discovery-yml/curl-request.md %} -->

Python (`requests`)

<!-- {% include snippets/api/dataplugins/publish-dataplugins-from-a-discovery-yml/python-requests.md %} -->

#### Response
`201 Created`

[Dataplugin](#dataplugin) collection with HAL links.
<!-- {% include snippets/api/dataplugins/publish-dataplugins-from-a-discovery-yml/response-body.md %} -->

---
### Create a dataplugin

PUT `/api/dataplugins/{dataplugin-id}`

Creates the dataplugin `{dataplugin-id}`.

#### Request
##### Body
[Dataplugin](#dataplugin) resource.
<!-- {% include snippets/api/dataplugins/create-a-dataplugin/request-body.md %} -->

##### Example Snippets
cURL

<!-- {% include snippets/api/dataplugins/create-a-dataplugin/curl-request.md %} -->

Python (`requests`)

<!-- {% include snippets/api/dataplugins/create-a-dataplugin/python-requests.md %} -->

#### Response
`201 Created`

[Dataplugin](#dataplugin) with HAL links.
<!-- {% include snippets/api/dataplugins/update-a-dataplugin/response-body.md %} -->

---
### Update a dataplugin

PUT `/api/dataplugins/{dataplugin-id}`

Updates the dataplugin `{dataplugin-id}`.

#### Prerequisites
- Dataplugin `{dataplugin-id}` must exist

#### Request
##### Body
[Dataplugin](#dataplugin) resource.
<!-- {% include snippets/api/dataplugins/update-a-dataplugin/request-body.md %} -->

Path | JSON Type | Format | Description | Constraints
---- | ---- | ------ | ----------- | -----------
`description` | `string` | | A description of the dataplugin |
`repositoryUrl` | `string` | | A URL to the dataplugin repository | 
`settings` | `object[]` | Array of [`Setting`](#setting)s | The dataplugin settings |

##### Example Snippets
cURL

<!-- {% include snippets/api/dataplugins/update-a-dataplugin/curl-request.md %} -->

Python (`requests`)

<!-- {% include snippets/api/dataplugins/update-a-dataplugin/python-requests.md %} -->

#### Response
`200 OK`

[Dataplugin](#dataplugin) with HAL links.
<!-- {% include snippets/api/dataplugins/update-a-dataplugin/response-body.md %} -->

---
### Delete a dataplugin

DELETE `/api/dataplugins/{dataplugin-id}`

Deletes the dataplugin `{dataplugin-id}`.

#### Request
##### Example Snippets
cURL

<!-- {% include snippets/api/dataplugins/delete-a-dataplugin/curl-request.md %} -->

Python (`requests`)

<!-- {% include snippets/api/dataplugins/delete-a-dataplugin/python-requests.md %} -->

#### Response
`204 No Content`

No response body provided.

---
