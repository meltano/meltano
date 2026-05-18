---
title: Datastores
description: Matatika Datastores resource reference documentation
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Datastores define a destination for data loaded into a [workspace](workspaces) by [pipelines](pipelines). The default datastore for a workspace is its own PostgreSQL database hosted by Matatika, but this can be changed at any time to another datastore with your own credentials (see our supported [dataplugins](dataplugins) of type `LOADER`).

---

## Objects

### Datastore

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`id` | `string` | Version 4 UUID | The datastore ID
`created` | `string` | ISO 8601 timestamp | The instant at which the datastore was created
`lastModified` | `string` | ISO 8601 timestamp | The instant at which the datastore was last modified
`name` | `string` | | The datastore name
`dataPlugin` | `string` | | Create / update with [dataplugin](dataplugins#dataplugin) `fullyQualifiedName`
`workspace` | `string` | Version 4 UUID | The datastore [workspace](workspaces#workspace) `id`
`jdbcUrl` | `string` | [JDBC URL](https://docs.oracle.com/javase/tutorial/jdbc/basics/connecting.html) | The datastore JDBC URL
`properties` | `object` | [`Properties`](#properties) | The datastore properties

### Properties

For each setting `s` in the [dataplugin](dataplugins) [`settings`](dataplugins#setting):

Path | Type | Description
---- | ---- | -----------
`s.name` | `s.kind` | Refer to `s.description`

## Requests

### View all datastores in a workspace

GET `/api/workspaces/{workspace-id}/datastores`

Returns the datastores in the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<!-- {% include snippets/api/datastores/view-all-datastores-in-a-workspace/curl-request.md %} -->

</TabItem>
<TabItem value="python" label="Python (requests)">

<!-- {% include snippets/api/datastores/view-all-datastores-in-a-workspace/python-requests.md %} -->

</TabItem>
</Tabs>

#### Response
`200 OK`

[Datastore](#datastore) collection with HAL links.
<!-- {% include snippets/api/datastores/view-all-datastores-in-a-workspace/response-body.md %} -->

---
### View a datastore

GET `/api/datastores/{datastore-id}`

Returns the datastore `{datastore-id}`.

#### Prerequisites
- Datastore `{datastore-id}` must exist

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<!-- {% include snippets/api/datastores/view-a-datastore/curl-request.md %} -->

</TabItem>
<TabItem value="python" label="Python (requests)">

<!-- {% include snippets/api/datastores/view-a-datastore/python-requests.md %} -->

</TabItem>
</Tabs>

#### Response
`200 OK`

[Datastore](#datastore) with HAL links.
<!-- {% include snippets/api/datastores/view-a-datastore/response-body.md %} -->

---
### Set a datastore as the workspace default

PUT `/api/datastores/{datastore-id}/default`

Sets the datastore `{datastore-id}` as the workspace default.

#### Prerequisites
- Datastore `{datastore-id}` must exist

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<!-- {% include snippets/api/datastores/set-a-datastore-as-the-workspace-default/curl-request.md %} -->

</TabItem>
<TabItem value="python" label="Python (requests)">

<!-- {% include snippets/api/datastores/set-a-datastore-as-the-workspace-default/python-requests.md %} -->

</TabItem>
</Tabs>

#### Response
`200 OK`

No response body provided.

---
### Initialise a new datastore in a workspace

POST `/api/workspaces/{workspace-id}/datastores`

Initialises a new datastore in the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<!-- {% include snippets/api/datastores/initialise-a-new-datastore-in-a-workspace/curl-request.md %} -->

</TabItem>
<TabItem value="python" label="Python (requests)">

<!-- {% include snippets/api/datastores/initialise-a-new-datastore-in-a-workspace/python-requests.md %} -->

</TabItem>
</Tabs>

#### Response
`200 OK`

[Datastore](#datastore) with HAL links.
<!-- {% include snippets/api/datastores/initialise-a-new-datastore-in-a-workspace/response-body.md %} -->

---
### Create or update a datastore in a workspace

PUT `/api/workspaces/{workspace-id}/datastores/{datastore-id}`

Creates or updates the datastore `{datastore-id}` in the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist

#### Request
##### Body
[Datastore](#datastore) resource.
<!-- {% include snippets/api/datastores/create-a-datastore-in-a-workspace/request-body.md %} -->

##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<!-- {% include snippets/api/datastores/create-a-datastore-in-a-workspace/curl-request.md %} -->

</TabItem>
<TabItem value="python" label="Python (requests)">

<!-- {% include snippets/api/datastores/create-a-datastore-in-a-workspace/python-requests.md %} -->

</TabItem>
</Tabs>

#### Response
`200 OK / 201 Created`

[Datastore](#datastore) with HAL links.
<!-- {% include snippets/api/datastores/create-a-datastore-in-a-workspace/response-body.md %} -->

---
### Delete a datastore

DELETE `/api/datastores/{datastore-id}`

Deletes the datastore `{datastore-id}`.

#### Prerequisites
- Datastore `{datastore-id}` must exist

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<!-- {% include snippets/api/datastores/delete-a-datastore/curl-request.md %} -->

</TabItem>
<TabItem value="python" label="Python (requests)">

<!-- {% include snippets/api/datastores/delete-a-datastore/python-requests.md %} -->

</TabItem>
</Tabs>

#### Response
`204 No Content`

No response body provided.

---
