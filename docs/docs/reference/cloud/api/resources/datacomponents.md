---
title: Datacomponents
description: Matatika Datacomponents resource reference documentation
components: request-md-components/datacomponents
---

Datacomponents hold configuration for [dataplugins](dataplugins), and are the building blocks for constructing [pipelines](pipelines). One dataplugin may be referenced by many datacomponents, each with a different set of `properties` for the dataplugin [`settings`](dataplugins#setting). One pipeline may reference multiple datacomponents.

---

## Objects

### Datacomponent

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`id` | `string` | Version 4 UUID | The datacomponent ID
`created` | `string` | ISO 8601 timestamp | When the datacomponent was created
`lastModified` | `string` | ISO 8601 timestamp | When the datacomponent was last modified
`name` | `string` | | The datacomponent name
`dataPlugin` | `string` | | Create / update with [dataplugin](dataplugins#dataplugin) `fullyQualifiedName`
`properties` | `object` | [`Properties`](#properties) | The datacomponent properties, defined by the [dataplugin](dataplugins) [`settings`](dataplugins#setting)<br/>Properties are key-value pairs, where keys reference setting `name`s

<!-- {% include snippets/api/datacomponents/view-a-datacomponent/response-body.md %} -->

#### Extractor Datacomponent
Datacomponents that are backed by [dataplugins](dataplugins) of `type` `EXTRACTOR` expose the following additional configuration:

Path | JSON Type | Format | Description
---- | --------- | ------ | -----------
`streams` | `object[]` | Array of [Stream](#stream)s | The available streams (populated after [verifying a pipeline](pipelines#verify-a-pipeline) that references this datacomponent)

<!-- {% include snippets/api/jobs/view-an-extractor-datacomponent/response-body.md %} -->

### Properties

For each setting in the [dataplugin](dataplugins) [`settings`](dataplugins#setting):

Path | JSON Type | Format | Description
---- | --------- | ------ | -----------
Refer to setting `name` | Refer to setting `kind` | Refer to setting `kind` | Refer to setting `description`

#### Reserved Properties for Extractor Datacomponents

Path | JSON Type | Format | Description
---- | --------- | ------ | -----------
`_select` | `string` | JSON array | Meltano [stream and property selection rules](https://docs.meltano.com/concepts/plugins#select-extra)
`_metadata` | `string` | JSON object | Meltano [stream and property metadata rules](https://docs.meltano.com/concepts/plugins#metadata-extra)

### Stream

Path | JSON Type | Format | Description
---- | --------- | ------ | -----------
`name` | `string` | | The stream name
`selected` | `string` | [Entity Selection](#entity-selection) | The stream entity selection type
`fields` | `object[]` | Array of [Field](#field)s | The available stream fields

### Field

Path | JSON Type | Format | Description
---- | --------- | ------ | -----------
`name` | `string` | | The field name
`selected` | `string` | [Entity Selection](#entity-selection) | The field entity selection type

## Formats

### Entity Selection

Value | Description
----- | -----------
`AUTOMATIC` | The entity is automatically selected by the underlying [extractor](https://docs.meltano.com/concepts/plugins#extractors) and will always be synced
`SELECTED` | The entity is selected and will be synced
`EXCLUDED` | The entity is excluded and will not be synced

---

## Requests

### View all datacomponents in a workspace

GET `/api/workspaces/{workspace-id}/datacomponents`

Returns all datacomponents in the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist

#### Request
##### Example Snippets
cURL

<!-- {% include snippets/api/datacomponents/view-all-datacomponents-in-a-workspace/curl-request.md %} -->

Python (`requests`)

<!-- {% include snippets/api/datacomponents/view-all-datacomponents-in-a-workspace/python-requests.md %} -->

#### Response
`200 OK`

[Datacomponent](#datacomponent) collection with HAL links.
<!-- {% include snippets/api/datacomponents/view-all-datacomponents-in-a-workspace/response-body.md %} -->

---
### View a datacomponent

GET `/api/datacomponents/{datacomponent-id}`

Returns the datacomponent `{datacomponent-id}`.

#### Prerequisites
- Datacomponent `{datacomponent-id}` must exist

#### Request
##### Example Snippets
cURL

<!-- {% include snippets/api/datacomponents/view-a-datacomponent/curl-request.md %} -->

Python (`requests`)

<!-- {% include snippets/api/datacomponents/view-a-datacomponent/python-requests.md %} -->

#### Response
`200 OK`

[Datacomponent](#datacomponent) with HAL links.
<!-- {% include snippets/api/datacomponents/view-a-datacomponent/response-body.md %} -->

---
### Initialise a new datacomponent in a workspace

POST `/api/workspaces/{workspace-id}/datacomponents`

Initialises a new datacomponent in the workspace `{workspace-id}`.

#### Request
##### Example Snippets
cURL

<!-- {% include snippets/api/datacomponents/initialise-a-new-datacomponent-in-a-workspace/curl-request.md %} -->

Python (`requests`)

<!-- {% include snippets/api/datacomponents/initialise-a-new-datacomponent-in-a-workspace/python-requests.md %} -->

#### Response
`200 OK`

[datacomponent](#datacomponent) with HAL links.
<!-- {% include snippets/api/datacomponents/initialise-a-new-datacomponent-in-a-workspace/response-body.md %} -->

---
### Create or update a datacomponent in a workspace

PUT `/api/workspaces/{workspace-id}/datacomponents/{datacomponent-id}`

Creates or updates the datacomponent `{datacomponent-id}` in the workspace `{workspace-id}`.

#### Request
##### Body
[Datacomponent](#datacomponent) resource.
<!-- {% include snippets/api/datacomponents/create-or-update-a-datacomponent-in-a-workspace/request-body.md %} -->

##### Example Snippets
cURL

<!-- {% include snippets/api/datacomponents/create-or-update-a-datacomponent-in-a-workspace/curl-request.md %} -->

Python (`requests`)

<!-- {% include snippets/api/datacomponents/create-or-update-a-datacomponent-in-a-workspace/python-requests.md %} -->

#### Response
`200 OK / 201 Created`

[Datacomponent](#datacomponent) with HAL links.
<!-- {% include snippets/api/datacomponents/create-or-update-a-datacomponent-in-a-workspace/response-body.md %} -->

---
### Update a datacomponent

PUT `/api/datacomponents/{datacomponent-id}`

Updates the datacomponent `{datacomponent-id}`.

#### Prerequisites
- Datacomponent `{datacomponent-id}` must exist

#### Request
##### Body
[Datacomponent](#datacomponent) resource.
<!-- {% include snippets/api/datacomponents/update-a-datacomponent/request-body.md %} -->

##### Example Snippets
cURL

<!-- {% include snippets/api/datacomponents/update-a-datacomponent/curl-request.md %} -->

Python (`requests`)

<!-- {% include snippets/api/datacomponents/update-a-datacomponent/python-requests.md %} -->

#### Response
`200 OK`

[Datacomponent](#datacomponent) with HAL links.
<!-- {% include snippets/api/datacomponents/update-a-datacomponent/response-body.md %} -->

---
### Delete a datacomponent

DELETE `/api/datacomponents/{datacomponent-id}`

Deletes the datacomponent `{datacomponent-id}`.

#### Request
##### Example Snippets
cURL

<!-- {% include snippets/api/datacomponents/delete-a-datacomponent/curl-request.md %} -->

Python (`requests`)

<!-- {% include snippets/api/datacomponents/delete-a-datacomponent/python-requests.md %} -->

#### Response
`204 No Content`

No response body provided.

---
