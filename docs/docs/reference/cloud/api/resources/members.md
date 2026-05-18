---
title: Members
description: Matatika Members resource reference documentation
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Members are users that belong to a particular [workspace](workspaces). Every member is derived from a corresponding [profile](profiles#profile), inheriting its `id` and `name`. Within the scope of a workspace, each member is visible to one another, so operating with a reduced property set allows for enhanced data security.

---

## Objects

### Member

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`id` | `string` | Version 4 UUID | The member ID (derived from corresponding profile ID)
`name` | `string` | | The member name (derived from corresponding profile name)
`handle` | `string` | | The unique `@`-prefixed handle for this member (derived from corresponding profile handle)

<!-- {% include snippets/api/workspaces/view-a-member-of-a-workspace/response-body.md %} -->

---

## Requests

### View all members of a workspace

GET `/api/workspaces/{workspace-id}/members`

Returns all members of the workspace `{workspace-id}`.

#### Prerequisites

- The user must be a member of the workspace `{workspace-id}`

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<!-- {% include snippets/api/workspaces/view-all-members-of-a-workspace/curl-request.md %} -->

</TabItem>
<TabItem value="python" label="Python (requests)">

<!-- {% include snippets/api/workspaces/view-all-members-of-a-workspace/python-requests.md %} -->

</TabItem>
</Tabs>

#### Response
`200 OK`

[Member](#member) collection with HAL links.
<!-- {% include snippets/api/workspaces/view-all-members-of-a-workspace/response-body.md %} -->

---
### View a member of a workspace

GET `/api/workspaces/{workspace-id}/members/{member-id}`

Returns the member `{member-id}` of the workspace `{workspace-id}`.

#### Prerequisites

- The user must be a member of the workspace `{workspace-id}`

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<!-- {% include snippets/api/workspaces/view-a-member-of-a-workspace/curl-request.md %} -->

</TabItem>
<TabItem value="python" label="Python (requests)">

<!-- {% include snippets/api/workspaces/view-a-member-of-a-workspace/python-requests.md %} -->

</TabItem>
</Tabs>

#### Response
`200 OK`

[Member](#member) with HAL links.
<!-- {% include snippets/api/workspaces/view-a-member-of-a-workspace/response-body.md %} -->

---
