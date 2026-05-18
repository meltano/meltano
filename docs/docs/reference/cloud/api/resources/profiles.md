---
title: Profiles
description: Matatika Profiles resource reference documentation
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Profiles are individual consumers of the Matatika service. A profile is automatically created for a user when they first access the app, or accept an invitation to a workspace from an existing member via email.

---

## Objects

### Profile

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`id` | `string` | Version 4 UUID | The profile ID 
`name` | `string` | The full name of the person or entity represented by this profile
`handle` | `string` | The unique `@`-prefixed handle for this profile (generated and read-only)
`phone` | `string` | Phone number | The profile phone number
`email` | `string` | Email address | The profile email address
`defaultWorkspace` | `object` | [`Workspace`](workspaces#workspace) | The profile default workspace

<!-- {% include snippets/api/profiles/view-a-profile/response-body.md %} -->

---

## Requests

### View all profiles

GET `/api/profiles`

Returns all profiles under the authenticated user account.

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<!-- {% include snippets/api/profiles/view-all-profiles/curl-request.md %} -->

</TabItem>
<TabItem value="python" label="Python (requests)">

<!-- {% include snippets/api/profiles/view-all-profiles/python-requests.md %} -->

</TabItem>
</Tabs>

#### Response
`200 OK`

[Profile](#profile) collection with HAL links.
<!-- {% include snippets/api/profiles/view-all-profiles/response-body.md %} -->

---
### View a profile

GET `/api/profiles/{profile-id}`

Returns the profile `{profile-id}`.

#### Prerequisites

- Profile `{profile-id}` must exist under the authenticated user account

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<!-- {% include snippets/api/profiles/view-a-profile/curl-request.md %} -->

</TabItem>
<TabItem value="python" label="Python (requests)">

<!-- {% include snippets/api/profiles/view-a-profile/python-requests.md %} -->

</TabItem>
</Tabs>

#### Response
`200 OK`

[Profile](#profile) with HAL links.
<!-- {% include snippets/api/profiles/view-a-profile/response-body.md %} -->

---
### Create or update profile

PUT `/api/profiles/{profile-id}`

Creates or updates the user profile.

#### Prerequisites

- The authentication subject must match the profile ID `{profile-id}`

#### Request

##### Body
[Profile](#profile) resource.
<!-- {% include snippets/api/profiles/update-a-profile/request-body.md %} -->

##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<!-- {% include snippets/api/profiles/update-a-profile/curl-request.md %} -->

</TabItem>
<TabItem value="python" label="Python (requests)">

<!-- {% include snippets/api/profiles/update-a-profile/python-requests.md %} -->

</TabItem>
</Tabs>

#### Response
`200 OK / 201 Created`

[Profile](#profile) with HAL links.
<!-- {% include snippets/api/profiles/update-a-profile/response-body.md %} -->

---
### Set a workspace as default

PATCH `/api/profiles/{profile-id}`

Sets a default workspace for the profile `{profile-id}`.

#### Prerequisites

- The authentication subject must match the profile ID `{profile-id}`

A workspace can be set as default, which defines the environment the Matatika app will initially load for a given profile. The default workspace setting persists only for the profile that sets it.

#### Request
##### Body
[Profile](#profile) resource.
<!-- {% include snippets/api/profiles/set-a-workspace-as-default/request-body.md %} -->

##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<!-- {% include snippets/api/profiles/set-a-workspace-as-default/curl-request.md %} -->

</TabItem>
<TabItem value="python" label="Python (requests)">

<!-- {% include snippets/api/profiles/set-a-workspace-as-default/python-requests.md %} -->

</TabItem>
</Tabs>

#### Response
`200 OK`

[Profile](#profile) with HAL links.
<!-- {% include snippets/api/profiles/set-a-workspace-as-default/response-body.md %} -->

---
