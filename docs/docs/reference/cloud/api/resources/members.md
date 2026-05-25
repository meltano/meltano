---
title: Members
description: Meltano Cloud members resource reference documentation
sidebar_position: 6
---

import Examples from '@site/src/components/Examples';
import Snippet from '@site/src/components/Snippet';

Members are users that belong to a particular [workspace](workspaces). Every member is derived from a corresponding [profile](profiles#profile), inheriting its `id` and `name`. Within the scope of a workspace, each member is visible to one another, so operating with a reduced property set allows for enhanced data security.

---

## Objects

### Member

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`id` | `string` | Version 4 UUID | The member ID (derived from corresponding profile ID)
`name` | `string` | | The member name (derived from corresponding profile name)
`handle` | `string` | | The unique `@`-prefixed handle for this member (derived from corresponding profile handle)

<Snippet path="workspaces/view-a-member-of-a-workspace/response-body.md" />

---

## Requests

### View all members of a workspace

:::info
**GET** `/api/workspaces/{workspace-id}/members`
:::

Returns all members of the workspace `{workspace-id}`.

#### Prerequisites

- The user must be a member of the workspace `{workspace-id}`

<Examples path="workspaces/view-all-members-of-a-workspace" />

#### Response
`200 OK`

[Member](#member) collection with HAL links.
<Snippet path="workspaces/view-all-members-of-a-workspace/response-body.md" />

---

### View a member of a workspace

:::info
**GET** `/api/workspaces/{workspace-id}/members/{member-id}`
:::

Returns the member `{member-id}` of the workspace `{workspace-id}`.

#### Prerequisites

- The user must be a member of the workspace `{workspace-id}`

<Examples path="workspaces/view-a-member-of-a-workspace" />

#### Response
`200 OK`

[Member](#member) with HAL links.
<Snippet path="workspaces/view-a-member-of-a-workspace/response-body.md" />

---
