---
title: Resources
description: Matatika resources resource reference documentation
permalink: /api/resources/resources
parent: Resources
grand_parent: API
nav_order: 21
components: request-md-components/resources
snippets: snippets/api/resources
---

# {{page.title}}

Resources are files that are managed by a workspace. A resource is accessible from `/api/workspaces/{workspace-id}/resources` by its `path`. 
{: .fs-5 }

---

## Objects
{: .no_toc}

### Resource

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`path` | `string` | | The resource path
`created` | `string` | ISO 8601 timestamp | The instant the resource was created at
`lastModified` | `string` | ISO 8601 timestamp | The instant the resource was last modified at
`contentType` | `string` | [MIME type](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types){:target="_blank"} | The content type of the resource
`content` | `string` | | The content of the resource

{% include {{page.snippets}}/view-a-resource-in-a-workspace/response-body.md %}

---

#### Requests

- TOC
{: toc }

---

{% include {{page.components}}/view-a-resource-in-a-workspace.md %}
{% include {{page.components}}/view-the-content-of-a-resource-in-a-workspace.md %}
{% include {{page.components}}/view-all-resources-in-a-workspace.md %}
{% include {{page.components}}/publish-multiple-resources-to-a-workspace.md %}
{% include {{page.components}}/create-or-update-a-resource-in-a-workspace.md %}
{% include {{page.components}}/delete-a-resource-in-a-workspace.md %}
