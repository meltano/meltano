---
title: Channels
description: Matatika Channels resource reference documentation
permalink: /api/resources/channels
parent: Resources
grand_parent: API
nav_order: 6
components: request-md-components/channels
---

# {{page.title}}

Channels enable datasets to be categorised or grouped together. A single workspace can have multiple channels.
{: .fs-5 }

---

## Objects
{: .no_toc }

### Channel

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`id` | `string` | Version 4 UUID | The channel ID
`creator` | `object` | [`Member`](members#member) | The channel creator
`workspace` | `object` | [`Workspace`](workspaces#workspace) | The channel workspace
`created` | `string` |  ISO 8601 timestamp | The channel created at timestamp
`lastModified` | `string` | ISO 8601 timestamp | The channel last modified timestamp
`name` | `string` | | The channel name
`description` | `string` | | The channel description
`picture` | `string` | URL | The channel picture metadata

{% include snippets/api/channels/view-a-channel/response-body.md %}

---

#### Requests

- TOC
{: toc}

#### See Also

- [Subscribe to a channel](subscriptions#subscribe-to-a-channel)

---

{% include request-md-components/channels/initialise-a-channel.md %}
{% include request-md-components/channels/view-a-channel.md %}
{% include request-md-components/channels/view-a-channel-in-a-workspace.md %}
{% include request-md-components/channels/view-all-channels-in-a-workspace.md %}
{% include request-md-components/channels/create-or-update-a-channel-in-a-workspace.md %}
{% include request-md-components/channels/delete-a-channel.md %}
{% include request-md-components/channels/view-all-channels-in-your-workspace-news.md %}
{% include request-md-components/channels/add-dataset-to-list-channel.md %}
{% include request-md-components/channels/remove-dataset-from-list-channel.md %}
{% include request-md-components/channels/add-workspace-scope-to-a-channel.md %}
{% include request-md-components/channels/withdraw-workspace-scope-from-a-channel.md %}
