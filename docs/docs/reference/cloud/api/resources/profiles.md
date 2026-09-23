---
title: Profiles
description: Meltano Cloud profiles resource reference documentation
sidebar_position: 2
---

import Examples from '@site/src/components/Examples';
import Snippet from '@site/src/components/Snippet';

Profiles are individual consumers of the Meltano Cloud service. A profile is automatically created for a user when they first access the app, or accept an invitation to a workspace from an existing member via email.

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
`workingAccount` | `object` | [`Account`](accounts#account) | The profile working account under which new workspaces are created

<Snippet path="profiles/view-a-profile/response-body.md" />

---

## Requests

### View all profiles

:::info
**GET** `/api/profiles`
:::

Returns all profiles under the authenticated user account.

<Examples path="profiles/view-all-profiles" />

#### Response
`200 OK`

[Profile](#profile) collection with HAL links.
<Snippet path="profiles/view-all-profiles/response-body.md" />

---

### View a profile

:::info
**GET** `/api/profiles/{profile-id}`
:::

Returns the profile `{profile-id}`.

#### Prerequisites

- Profile `{profile-id}` must exist under the authenticated user account

<Examples path="profiles/view-a-profile" />

#### Response
`200 OK`

[Profile](#profile) with HAL links.
<Snippet path="profiles/view-a-profile/response-body.md" />

---

### Create or update profile

:::info
**PUT** `/api/profiles/{profile-id}`
:::

Creates or updates the user profile.

#### Prerequisites

- The authentication subject must match the profile ID `{profile-id}`


#### Body
[Profile](#profile) resource.
<Snippet path="profiles/update-a-profile/request-body.md" />


<Examples path="profiles/update-a-profile" />

#### Response
`200 OK / 201 Created`

[Profile](#profile) with HAL links.
<Snippet path="profiles/update-a-profile/response-body.md" />

---

### Set a workspace as default

:::info
**PATCH** `/api/profiles/{profile-id}`
:::

Sets a default workspace for the profile `{profile-id}`.

#### Prerequisites

- The authentication subject must match the profile ID `{profile-id}`

A workspace can be set as default, which defines the environment Meltano Cloud will initially load with for a given profile. The default workspace setting persists only for the profile that sets it.

#### Body
[Profile](#profile) resource.
<Snippet path="profiles/set-a-workspace-as-default/request-body.md" />


<Examples path="profiles/set-a-workspace-as-default" />

#### Response
`200 OK`

[Profile](#profile) with HAL links.
<Snippet path="profiles/set-a-workspace-as-default/response-body.md" />

---

### Set the working account for a profile

:::info
**PUT** `/api/profiles/{profile-id}/working-account/{account-id}`
:::

Sets the working account `{account-id}` for the profile `{profile-id}`.

#### Prerequisites

- Profile `{profile-id}` must exist
- Account `{account-id}` must exist
- The authentication subject must match the profile ID `{profile-id}`
- The profile `{profile-id}` must be an owner of the account `{account-id}`

<Examples path="profiles/set-the-working-account-for-a-profile" />

#### Response
`200 OK`

[Profile](#profile) with HAL links.
<Snippet path="profiles/set-the-working-account-for-a-profile/response-body.md" />

---

##### See Also

- [View all account admins](accounts#view-all-account-admins)
- [Add an account admin](accounts#add-an-account-admin)
- [Remove an account admin](accounts#remove-an-account-admin)
- [Set an account owner](accounts#set-an-account-owner)
