---
title: Invitations
description: Matatika Invitations resource reference documentation
---

import Snippet from '@site/src/components/Snippet';
import TabItem from '@theme/TabItem';
import Tabs from '@theme/Tabs';

Invitations allow access to private workspaces. When an invitation is created, an email containing an access link to the workspace will be sent to the recipient. Invitations can be sent to email addresses under the allowed domains configured for a workspace.

---

## Objects

### Invitation

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`id` | `string` | Version 4 UUID | The invitation ID
`created` | `string` | ISO 8601 timestamp | The instant the invitation was created
`lastModified` | `string` | ISO 8601 timestamp | The instant the invitation was last modified
`status` | `string` | [Invitation Status](#invitation-status) | The invitation status
`email` | `string` | Email address | The invitation target email address
`creator` | `object` | [`Member`](members#member) | The invitation creator
`workspace` | `object` | [`Workspace`](workspaces#workspace) | The invitation target workspace

<Snippet path="invitations/view-all-invitations-to-a-workspace/response-body.md" />

## Formats

### Invitation Status

`string`

Value | Description
----- | -----------
`ACCEPTED` | The invitation has been accepted by the recipient
`PENDING` | The invitation has been sent to the recipient and is awaiting acceptance
`REVOKED` | The invitation has been revoked and can no longer be accepted

---

## Requests

### View all sent invitations

:::info
**GET** `/api/invitations`
:::

Returns all invitations sent by the authenticated user profile.

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<Snippet path="invitations/view-all-sent-invitations/curl-request.md" />

</TabItem>
<TabItem value="python" label="Python (requests)">

<Snippet path="invitations/view-all-sent-invitations/python-requests.md" />

</TabItem>
</Tabs>

#### Response
`200 OK`

[Invitation](#invitation) collection with HAL links.
<Snippet path="invitations/view-all-sent-invitations/response-body.md" />

---
### View all received invitations

:::info
**GET** `/api/invitations?email={user-email}`
:::

Returns all invitations received by the authenticated user profile.

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<Snippet path="invitations/view-all-received-invitations/curl-request.md" />

</TabItem>
<TabItem value="python" label="Python (requests)">

<Snippet path="invitations/view-all-received-invitations/python-requests.md" />

</TabItem>
</Tabs>

#### Response
`200 OK`

[Invitation](#invitation) collection with HAL links.
<Snippet path="invitations/view-all-received-invitations/response-body.md" />

---
### View all invitations to a workspace

:::info
**GET** `/api/workspaces/{workspace-id}/invitations`
:::

*As a workspace owner...*

Returns all active invitations to the workspace `{workspace-id}`.

*As a workspace member...*

Returns all active invitations to the workspace `{workspace-id}` sent by the authenticated user profile. 

#### Prerequisites

- The user must be a member of the workspace `{workspace-id}`

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<Snippet path="invitations/view-all-invitations-to-a-workspace/curl-request.md" />

</TabItem>
<TabItem value="python" label="Python (requests)">

<Snippet path="invitations/view-all-invitations-to-a-workspace/python-requests.md" />

</TabItem>
</Tabs>

#### Response
`200 OK`

[Invitation](#invitation) collection with HAL links.
<Snippet path="invitations/view-all-invitations-to-a-workspace/response-body.md" />

---
### Create an invitation to a workspace

:::info
**POST** `/api/workspaces/{workspace-id}/invitations`
:::

Creates an invitation to the workspace `{workspace-id}`.

#### Prerequisites

- The user must be a member of the workspace `{workspace-id}`

#### Request

##### Body
[Invitation](#invitation) resource.
<Snippet path="invitations/create-an-invitation-to-a-workspace/request-body.md" />

##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<Snippet path="invitations/create-an-invitation-to-a-workspace/curl-request.md" />

</TabItem>
<TabItem value="python" label="Python (requests)">

<Snippet path="invitations/create-an-invitation-to-a-workspace/python-requests.md" />

</TabItem>
</Tabs>

#### Response
`202 Accepted`

No response body provided.

---
### Accept an invitation

:::info
**PATCH** `/api/invitations/{invitation-id}`
:::

Accepts the invitation `{invitation-id}`.

#### Prerequisites

- Workspace `{workspace-id}` must exist
- Invitation `{invitation-id}` must exist for the authenticated user profile

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<Snippet path="invitations/accept-an-invitation/curl-request.md" />

</TabItem>
<TabItem value="python" label="Python (requests)">

<Snippet path="invitations/accept-an-invitation/python-requests.md" />

</TabItem>
</Tabs>

#### Response
`200 OK`

[Invitation](#invitation) with HAL links.
<Snippet path="invitations/accept-an-invitation/response-body.md" />

---
### Delete an invitation

:::info
**DELETE** `/api/invitations/{invitation-id}`
:::

Deletes a pending or revoked invitation `{invitation-id}`.

#### Prerequisites

- The authenticated user must be the owner of workspace the invitation belongs to
- or the authenticated user must have sent the invitation `{invitation-id}`

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<Snippet path="invitations/delete-an-invitation-to-a-workspace/curl-request.md" />

</TabItem>
<TabItem value="python" label="Python (requests)">

<Snippet path="invitations/delete-an-invitation-to-a-workspace/python-requests.md" />

</TabItem>
</Tabs>

#### Response
`204 No Content`

No response body provided.

---
### Withdraw an invitation

:::info
**PUT** `/api/invitations/{invitation-id}/revoked`
:::

Withdraws the pending or accepted invitation `{invitation-id}`.

#### Prerequisites

- The authenticated user must be the owner of workspace the invitation belongs to
- or the authenticated user must have sent the invitation `{invitation-id}`

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<Snippet path="invitations/withdraw-an-invitation-to-a-workspace/curl-request.md" />

</TabItem>
<TabItem value="python" label="Python (requests)">

<Snippet path="invitations/withdraw-an-invitation-to-a-workspace/python-requests.md" />

</TabItem>
</Tabs>

#### Response
`200 OK`

No response body provided.

---
