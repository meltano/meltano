---
title: Administrators
description: Matatika Administrators resource reference documentation
components: request-md-components/administrators
---

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

#### Requests

---

<!-- {% include {{page.components}}/view-all-administrators-of-a-workspace.md %}
{% include {{page.components}}/add-an-administrator-to-a-workspace.md %}
{% include {{page.components}}/withdraw-an-administrator-from-a-workspace.md %} -->
