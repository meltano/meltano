---
title: Administrators
description: Meltano Cloud administrators resource reference documentation
sidebar_position: 5
---

import Examples from '@site/src/components/Examples';
import Snippet from '@site/src/components/Snippet';

Administrators are types of [members](members) with delegated [workspace](workspaces) management permissions, equivalent to those held by the workspace owner.

---

## Objects

### Administrator

Extends from [Member](members#member)

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`administrator` | `bool` | | Whether or not the [member](members) is an administrator

<Snippet path="workspaces/add-an-administrator-to-a-workspace/response-body.md" />

---

## Requests

### View all administrators of a workspace

:::info
**GET** `/api/workspaces/{workspace-id}/administrators`
:::

Returns all administrators of the workspace `{workspace-id}`.

#### Prerequisites
- The user must be a member of the workspace `{workspace-id}`

<Examples path="workspaces/view-all-administrators-of-a-workspace" />

#### Response
`200 OK`

[Administrator](#administrator) collection with HAL links.
<Snippet path="workspaces/view-all-administrators-of-a-workspace/response-body.md" />

---

### Add an administrator to a workspace

:::info
**PUT** `/api/workspaces/{workspace-id}/administrators/{profile-id}`
:::

Adds the profile `{profile-id}` as an administrator to the workspace `{workspace-id}`.

#### Prerequisites
- The authenticated user profile must be the owner of the workspace `{workspace-id}`
- The profile `{profile-id}` must be a [member](members) of the workspace `{workspace-id}`

<Examples path="workspaces/add-an-administrator-to-a-workspace" />

#### Response
`200 OK`

[Administrator](#administrator) with HAL links.
<Snippet path="workspaces/add-an-administrator-to-a-workspace/response-body.md" />

---

### Withdraw an administrator from a workspace

:::info
**DELETE** `/api/workspaces/{workspace-id}/administrators/{profile-id}`
:::

Withdraws the profile `{profile-id}` as an administrator from the workspace `{workspace-id}`.

#### Prerequisites
- The authenticated user profile must be the owner of the workspace `{workspace-id}`
- The profile `{profile-id}` must be an administrator of the workspace `{workspace-id}`

<Examples path="workspaces/withdraw-an-administrator-from-a-workspace" />

#### Response
`200 OK`

[Administrator](#administrator) with HAL links.
<Snippet path="workspaces/withdraw-an-administrator-from-a-workspace/response-body.md" />

---
