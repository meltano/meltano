---
title: Members
description: Matatika Members resource reference documentation
permalink: api/resources/members
parent: Resources
grand_parent: API
nav_order: 4
components: request-md-components/members
---

# {{page.title}}

Members are users that belong to a particular [workspace](workspaces). Every member is derived from a corresponding [profile](profiles#profile), inheriting its `id` and `name`. Within the scope of a workspace, each member is visible to one another, so operating with a reduced property set allows for enhanced data security.
{: .fs-5 }

---

## Objects
{: .no_toc}

### Member

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`id` | `string` | Version 4 UUID | The member ID (derived from corresponding profile ID)
`name` | `string` | | The member name (derived from corresponding profile name)
`handle` | `string` | | The unique `@`-prefixed handle for this member (derived from corresponding profile handle)

{% include snippets/api/workspaces/view-a-member-of-a-workspace/response-body.md %}

---

#### Requests

- TOC
{: toc }

---

{% include {{page.components}}/view-all-members-of-a-workspace.md %}
{% include {{page.components}}/view-a-member-of-a-workspace.md %}
