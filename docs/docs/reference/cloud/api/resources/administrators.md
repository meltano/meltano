---
title: Administrators
description: Matatika Administrators resource reference documentation
permalink: api/resources/administrators
parent: Resources
grand_parent: API
nav_order: 4
components: request-md-components/administrators
---

# {{page.title}}

Administrators are types of [members](members) with delegated [workspace](workspaces) management permissions, equivalent to those held by the workspace owner.
{: .fs-5 }

---

## Objects
{: .no_toc}

### Administrator
{: .d-inline-block }

Extends from [Member](members#member)
{: .float-right .mt-5 }

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`administrator` | `bool` | | Whether or not the [member](members) is an administrator

{% include snippets/api/workspaces/add-an-administrator-to-a-workspace/response-body.md %}

---

#### Requests

- TOC
{: toc }

---

{% include {{page.components}}/view-all-administrators-of-a-workspace.md %}
{% include {{page.components}}/add-an-administrator-to-a-workspace.md %}
{% include {{page.components}}/withdraw-an-administrator-from-a-workspace.md %}
