---
title: Datastores
description: Meltano Cloud datastores resource reference documentation
sidebar_position: 17
---

import Examples from '@site/src/components/Examples';
import Snippet from '@site/src/components/Snippet';

Datastores define a destination for data loaded into a [workspace](workspaces) by [pipelines](pipelines). The default datastore for a workspace is its own PostgreSQL database hosted by Meltano Cloud, but this can be changed at any time to another datastore with your own credentials (see our supported [dataplugins](dataplugins) of type `LOADER`).

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

:::info
**GET** `/api/workspaces/{workspace-id}/datastores`
:::

Returns the datastores in the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist

<Examples path="datastores/view-all-datastores-in-a-workspace" />

#### Response
`200 OK`

[Datastore](#datastore) collection with HAL links.
<Snippet path="datastores/view-all-datastores-in-a-workspace/response-body.md" />

---

### View a datastore

:::info
**GET** `/api/datastores/{datastore-id}`
:::

Returns the datastore `{datastore-id}`.

#### Prerequisites
- Datastore `{datastore-id}` must exist

<Examples path="datastores/view-a-datastore" />

#### Response
`200 OK`

[Datastore](#datastore) with HAL links.
<Snippet path="datastores/view-a-datastore/response-body.md" />

---

### Set a datastore as the workspace default

:::info
**PUT** `/api/datastores/{datastore-id}/default`
:::

Sets the datastore `{datastore-id}` as the workspace default.

#### Prerequisites
- Datastore `{datastore-id}` must exist

<Examples path="datastores/set-a-datastore-as-the-workspace-default" />

#### Response
`200 OK`

No response body provided.

---

### Initialise a new datastore in a workspace

:::info
**POST** `/api/workspaces/{workspace-id}/datastores`
:::

Initialises a new datastore in the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist

<Examples path="datastores/initialise-a-new-datastore-in-a-workspace" />

#### Response
`200 OK`

[Datastore](#datastore) with HAL links.
<Snippet path="datastores/initialise-a-new-datastore-in-a-workspace/response-body.md" />

---

### Create or update a datastore in a workspace

:::info
**PUT** `/api/workspaces/{workspace-id}/datastores/{datastore-id}`
:::

Creates or updates the datastore `{datastore-id}` in the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist

#### Body
[Datastore](#datastore) resource.
<Snippet path="datastores/create-a-datastore-in-a-workspace/request-body.md" />


<Examples path="datastores/create-a-datastore-in-a-workspace" />

#### Response
`200 OK / 201 Created`

[Datastore](#datastore) with HAL links.
<Snippet path="datastores/create-a-datastore-in-a-workspace/response-body.md" />

---

### Delete a datastore

:::info
**DELETE** `/api/datastores/{datastore-id}`
:::

Deletes the datastore `{datastore-id}`.

#### Prerequisites
- Datastore `{datastore-id}` must exist

<Examples path="datastores/delete-a-datastore" />

#### Response
`204 No Content`

No response body provided.

---

##### See Also

- [DatastoreML](/reference/cloud/dataml/datastoreml/)
