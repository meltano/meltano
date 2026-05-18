---
title: Profiles
description: Matatika Profiles resource reference documentation
permalink: /api/resources/profiles
parent: Resources
grand_parent: API
nav_order: 1
components: request-md-components/profiles
---

# {{page.title}}

Profiles are individual consumers of the Matatika service. A profile is automatically created for a user when they first access the app, or accept an invitation to a workspace from an existing member via email.
{: .fs-5 }

---

## Objects
{: .no_toc}

### Profile

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`id` | `string` | Version 4 UUID | The profile ID 
`name` | `string` | The full name of the person or entity represented by this profile
`handle` | `string` | The unique `@`-prefixed handle for this profile (generated and read-only)
`phone` | `string` | Phone number | The profile phone number
`email` | `string` | Email address | The profile email address
`defaultWorkspace` | `object` | [`Workspace`](workspaces#workspace) | The profile default workspace

{% include snippets/api/profiles/view-a-profile/response-body.md %}

---

#### Requests

- TOC
{: toc }

---

{% include {{page.components}}/view-all-profiles.md %}
{% include {{page.components}}/view-a-profile.md %}
{% include {{page.components}}/create-or-update-a-profile.md %}
{% include {{page.components}}/set-a-workspace-as-default.md %}
