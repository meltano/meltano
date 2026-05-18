---
title: Invitations
description: Matatika Invitations resource reference documentation
permalink: /api/resources/invitations
parent: Resources
grand_parent: API
nav_order: 3
components: request-md-components/invitations
---

# {{page.title}}

Invitations allow access to private workspaces. When an invitation is created, an email containing an access link to the workspace will be sent to the recipient. Invitations can be sent to email addresses under the allowed domains configured for a workspace.
{: .fs-5 }

---

## Objects
{: .no_toc}

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

{% include snippets/api/invitations/view-all-invitations-to-a-workspace/response-body.md %}

## Formats
{: .no_toc}

### Invitation Status
{: .d-inline-block }

`string`
{: .float-right .mt-5 }

Value | Description
----- | -----------
`ACCEPTED` | The invitation has been accepted by the recipient
`PENDING` | The invitation has been sent to the recipient and is awaiting acceptance
`REVOKED` | The invitation has been revoked and can no longer be accepted

---

#### Requests

- TOC
{: toc }

---

{% include {{ page.components }}/view-all-sent-invitations.md %}
{% include {{ page.components }}/view-all-received-invitations.md %}
{% include {{ page.components }}/view-all-invitations-to-a-workspace.md %}
{% include {{ page.components }}/create-an-invitation-to-a-workspace.md %}
{% include {{ page.components }}/accept-an-invitation.md %}
{% include {{ page.components }}/delete-an-invitation-to-a-workspace.md %}
{% include {{ page.components }}/withdraw-an-invitation-to-a-workspace.md %}
