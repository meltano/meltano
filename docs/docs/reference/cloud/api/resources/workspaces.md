---
title: Workspaces
description: Matatika Workspaces resource reference documentation
permalink: /api/resources/workspaces
parent: Resources
grand_parent: API
nav_order: 2
components: request-md-components/workspaces
---

# {{page.title}}

Workspaces allow users to operate within isolated instances of the Matatika service. This is useful for separating profiles based on the data they require access to.
{: .fs-5 }

---

## Objects
{: .no_toc}

### Workspace

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`id` | `string` | Version 4 UUID | The workspace ID
`created` | `string` | ISO 8601 timestamp | The instant the workspace was created
`lastModified` | `string` | ISO 8601 timestamp | The instant the workspace was last modified
`alias` | `string` | | The workspace alias and database schema name
`name` | `string` | | The workspace name
`domains` | `string[]` | Array of domain hosts | The workspace allowed domains
`repositoryUrl` | `string` | URL | The workspace repository URL
`pipelinesImage` | `string` | Container image name path | The path name of an image to run pipelines from
`imageUrl` | `string` | Image [data URL](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URIs){:target="_blank"} | The workspace image data URL
`status` | `string` | [Workspace Status](#workspace-status) | The workspace status
`defaultWorkspace` | `bool` | | Whether or not the workspace is set as the default the authenticated user

{% include snippets/api/workspaces/view-a-workspace/response-body.md %}

## Formats
{: .no_toc}

### Workspace Status
{: .d-inline-block }

`string`
{: .float-right .mt-5 }

Value | Description
----- | -----------
`READY` | The workspace completed processing resource changes
`PROVISIONING` | The workspace is processing resource changes
`FAILED` | The workspace failed to process resource changes

---

#### Requests

- TOC
{: toc}

#### See Also

- [Set a workspace as default](profiles#set-a-workspace-as-default)
- [View all invitations to a workspace](invitations#view-all-invitations-to-a-workspace)
- [Create an invitation to a workspace](invitations#create-an-invitation-to-a-workspace)
- [Cancel an invitation](invitations#withdraw-an-invitation)
- [View all members of a workspace](members#view-all-members-of-a-workspace)
- [View a member of a workspace](members#view-a-member-of-a-workspace)
- [View all channels in a workspace](channels#view-all-channels-in-a-workspace)
- [View all liked datasets in a workspace](datasets#view-all-liked-datasets-in-a-workspace)
- [View the feed of a workspace](feed#view-the-feed-of-a-workspace)
- [View all pipelines in a workspace](pipelines#view-all-pipelines-in-a-workspace)
- [View a pipeline](pipelines#view-a-pipeline)
- [Initialise a pipeline in a workspace](pipelines#initialise-a-pipeline-in-a-workspace)
- [Create or update a pipeline in a workspace](pipelines#create-or-update-a-pipeline-in-a-workspace)
- [Delete a pipeline](pipelines#delete-a-pipeline)
- [View all running or completed jobs for a workspace](jobs#view-all-running-or-completed-jobs-for-a-workspace)

---

{% include {{page.components}}/view-all-workspaces.md %}
{% include {{page.components}}/view-a-workspace.md %}
{% include {{page.components}}/initialise-a-workspace.md %}
{% include {{page.components}}/create-a-workspace.md %}
{% include {{page.components}}/update-a-workspace.md %}
{% include {{page.components}}/delete-a-workspace.md %}
