---
title: Dataplugins
description: Meltano Cloud resource reference documentation
sidebar_position: 15
---

import Examples from '@site/src/components/Examples';
import Snippet from '@site/src/components/Snippet';

Dataplugins simply define a source of data from a given repository. Meltano Cloud provides a number of pre-configured platform-wide dataplugins out-the-box, as well as the ability to create custom dataplugins through the API. From these, [pipeline](pipelines) jobs can be run to inject data into a workspace.

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

<Snippet path="dataplugins/view-a-dataplugin/response-body.md" />

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

:::info
**GET** `/api/dataplugins`
:::

Returns all dataplugins supported by Meltano Cloud.

<Examples path="dataplugins/view-all-supported-dataplugins" />

#### Response
`200 OK`

[Dataplugin](#dataplugin) collection with HAL links.
<Snippet path="dataplugins/view-all-supported-dataplugins/response-body.md" />

---

### View all workspace dataplugins

:::info
**GET** `/api/workspaces/{workspace-id}/dataplugins`
:::

Returns all dataplugins available to the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist

<Examples path="dataplugins/view-all-workspace-dataplugins" />

#### Response
`200 OK`

[Dataplugin](#dataplugin) collection with HAL links.
<Snippet path="dataplugins/view-all-workspace-dataplugins/response-body.md" />

---

### View a dataplugin

:::info
**GET** `/api/dataplugins/{dataplugin-id}`
:::

Returns the dataplugin `{dataplugin-id}`.

#### Prerequisites
- Dataplugin `{dataplugin-id}` must exist

<Examples path="dataplugins/view-a-dataplugin" />

#### Response
`200 OK`

[Dataplugin](#dataplugin) with HAL links.
<Snippet path="dataplugins/view-a-dataplugin/response-body.md" />

---

### Initialise a new dataplugin

:::info
**POST** `/api/dataplugins`
:::

Initialises a new dataplugin.

<Examples path="dataplugins/initialise-a-new-dataplugin" />

#### Response
`200 OK`

[Dataplugin](#dataplugin) with HAL links.
<Snippet path="dataplugins/initialise-a-new-dataplugin/response-body.md" />

---

### Create a dataplugin

:::info
**PUT** `/api/dataplugins/{dataplugin-id}`
:::

Creates the dataplugin `{dataplugin-id}`.

#### Body
[Dataplugin](#dataplugin) resource.
<Snippet path="dataplugins/create-a-dataplugin/request-body.md" />


<Examples path="dataplugins/create-a-dataplugin" />

#### Response
`201 Created`

[Dataplugin](#dataplugin) with HAL links.
<Snippet path="dataplugins/update-a-dataplugin/response-body.md" />

---

### Update a dataplugin

:::info
**PUT** `/api/dataplugins/{dataplugin-id}`
:::

Updates the dataplugin `{dataplugin-id}`.

#### Prerequisites
- Dataplugin `{dataplugin-id}` must exist

#### Body
[Dataplugin](#dataplugin) resource.
<Snippet path="dataplugins/update-a-dataplugin/request-body.md" />

Path | JSON Type | Format | Description | Constraints
---- | ---- | ------ | ----------- | -----------
`description` | `string` | | A description of the dataplugin |
`repositoryUrl` | `string` | | A URL to the dataplugin repository |
`settings` | `object[]` | Array of [`Setting`](#setting)s | The dataplugin settings |


<Examples path="dataplugins/update-a-dataplugin" />

#### Response
`200 OK`

[Dataplugin](#dataplugin) with HAL links.
<Snippet path="dataplugins/update-a-dataplugin/response-body.md" />

---

### Delete a dataplugin

:::info
**DELETE** `/api/dataplugins/{dataplugin-id}`
:::

Deletes the dataplugin `{dataplugin-id}`.

<Examples path="dataplugins/delete-a-dataplugin" />

#### Response
`204 No Content`

No response body provided.

---
