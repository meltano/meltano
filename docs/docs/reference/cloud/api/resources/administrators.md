---
title: Administrators
description: Matatika Administrators resource reference documentation
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Administrators are types of [members](members) with delegated [workspace](workspaces) management permissions, equivalent to those held by the workspace owner.

---

## Objects

### Administrator

Extends from [Member](members#member)

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`administrator` | `bool` | | Whether or not the [member](members) is an administrator

<!-- {% include snippets/api/workspaces/add-an-administrator-to-a-workspace/response-body.md %} -->

---

## Requests

### View all administrators of a workspace

:::info
**GET** `/api/workspaces/{workspace-id}/administrators`
:::

Returns all administrators of the workspace `{workspace-id}`.

#### Prerequisites
- The user must be a member of the workspace `{workspace-id}`

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<!-- {% include snippets/api/workspaces/view-all-administrators-of-a-workspace/curl-request.md %} -->

</TabItem>
<TabItem value="python" label="Python (requests)">

<!-- {% include snippets/api/workspaces/view-all-administrators-of-a-workspace/python-requests.md %} -->

</TabItem>
</Tabs>

#### Response
`200 OK`

[Administrator](#administrator) collection with HAL links.
<!-- {% include snippets/api/workspaces/view-all-administrators-of-a-workspace/response-body.md %} -->

---
### Add an administrator to a workspace

:::info
**PUT** `/api/workspaces/{workspace-id}/administrators/{profile-id}`
:::

Adds the profile `{profile-id}` as an administrator to the workspace `{workspace-id}`.

#### Prerequisites
- The authenticated user profile must be the owner of the workspace `{workspace-id}`
- The profile `{profile-id}` must be a [member](members) of the workspace `{workspace-id}`

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<!-- {% include snippets/api/workspaces/add-an-administrator-to-a-workspace/curl-request.md %} -->

</TabItem>
<TabItem value="python" label="Python (requests)">

<!-- {% include snippets/api/workspaces/add-an-administrator-to-a-workspace/python-requests.md %} -->

</TabItem>
</Tabs>

#### Response
`200 OK`

[Administrator](#administrator) with HAL links.
<!-- {% include snippets/api/workspaces/add-an-administrator-to-a-workspace/response-body.md %} -->

---
### Withdraw an administrator from a workspace

:::info
**DELETE** `/api/workspaces/{workspace-id}/administrators/{profile-id}`
:::

Withdraws the profile `{profile-id}` as an administrator from the workspace `{workspace-id}`.

#### Prerequisites
- The authenticated user profile must be the owner of the workspace `{workspace-id}`
- The profile `{profile-id}` must be an administrator of the workspace `{workspace-id}`

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<!-- {% include snippets/api/workspaces/withdraw-an-administrator-from-a-workspace/curl-request.md %} -->

</TabItem>
<TabItem value="python" label="Python (requests)">

<!-- {% include snippets/api/workspaces/withdraw-an-administrator-from-a-workspace/python-requests.md %} -->

</TabItem>
</Tabs>

#### Response
`200 OK`

[Administrator](#administrator) with HAL links.
<!-- {% include snippets/api/workspaces/withdraw-an-administrator-from-a-workspace/response-body.md %} -->

---
