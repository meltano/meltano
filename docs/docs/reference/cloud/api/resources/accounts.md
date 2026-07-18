---
title: Accounts
description: Meltano Cloud accounts resource reference documentation
sidebar_position: 1
---

import Examples from '@site/src/components/Examples';
import Snippet from '@site/src/components/Snippet';

Accounts are passive entities that store quota information for resources consumed by associated [profiles](profiles). An account is created for a user when they first sign up.

---

## Objects

### Account

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`id` | `string` | Version 4 UUID | The account ID
`created` | `string` | ISO 8601 timestamp | The instant at which the account was created
`lastModified` | `string` | ISO 8601 timestamp | The instant at which the account was last modified
`company` | `string` | | The name of the company associated with the account
`ownerEmail` | `string` | Email address | The email address of the owner profile
`ownerProfileId` | `string` | | The ID of the owner profile
`maxWorkspaces` | `number` | Unsigned integer | The maximum number of workspaces that can be created under the account
`maxRows` | `number` | Unsigned integer | The maximum number of managed database rows available to the account
`minutesPerMonth` | `number` | Unsigned integer | The number of [pipeline](pipelines) run minutes available to the account per month
`minutesUsed` | `number` | Unsigned integer | The number of [pipeline](pipelines) run minutes used by the account per month
`maxClients` | `number` | Unsigned integer | The number of [API key](apikeys) clients available to the account

---

## Requests

### View all accounts

:::info
**GET** `/api/accounts`
:::

Returns all accounts the authenticated user profile is an owner of.

<Examples path="accounts/view-all-accounts" />

#### Response
`200 OK`

[Account](#account) collection with HAL links.
<Snippet path="accounts/view-all-accounts/response-body.md" />

---

### View an account

:::info
**GET** `/api/accounts/{account-id}`
:::

Returns the account `{account-id}`.

#### Prerequisites

- Account `{account-id}` must exist
- The authenticated user profile must be an owner of the account `{account-id}`

<Examples path="accounts/view-an-account" />

#### Response
`200 OK`

[Account](#account) with HAL links.
<Snippet path="accounts/view-an-account/response-body.md" />

---

### Initialise a new account

:::info
**POST** `/api/accounts/new`
:::

Initialises a new account.

<Examples path="accounts/initialise-a-new-account" />

#### Response
`200 OK`

[Account](#account) with HAL links.
<Snippet path="accounts/initialise-a-new-account/response-body.md" />

---

### Create an account

:::info
**PUT** `/api/accounts/{account-id}`
:::

Creates the account `{account-id}`.

#### Prerequisites

- The `ownerEmail` must match the authenticated user profile's email address

#### Body
[Account](#account) resource.
<Snippet path="accounts/create-an-account/request-body.md" />


<Examples path="accounts/create-an-account" />

#### Response
`201 Created`

[Account](#account) with HAL links.
<Snippet path="accounts/create-an-account/response-body.md" />

---

### Update an account

:::info
**PUT** `/api/accounts/{account-id}`
:::

Updates the account `{account-id}`.

#### Prerequisites

- Account `{account-id}` must exist
- The authenticated user profile must be an owner of the account `{account-id}`

#### Body
[Account](#account) resource.
<Snippet path="accounts/update-an-account/request-body.md" />


<Examples path="accounts/update-an-account" />

#### Response
`200 OK`

[Account](#account) with HAL links.
<Snippet path="accounts/update-an-account/response-body.md" />

---

### View all account admins

:::info
**GET** `/api/accounts/{account-id}/admins`
:::

Returns all admins of the account `{account-id}`.

#### Prerequisites

- The authenticated user profile must be an owner of the account `{account-id}`

<Examples path="accounts/view-all-account-admins" />

#### Response
`200 OK`

[Profile](profiles#profile) collection with HAL links.
<Snippet path="accounts/view-all-account-admins/response-body.md" />

---

### Add an account admin

:::info
**PUT** `/api/accounts/{account-id}/admins/{profile-id}`
:::

Adds the profile `{profile-id}` as an admin of the account `{account-id}`.

#### Prerequisites

- The authenticated user profile must be an owner of the account `{account-id}`
- Profile `{profile-id}` must exist

<Examples path="accounts/add-an-account-admin" />

#### Response
`200 OK`

[Account](#account) with HAL links.
<Snippet path="accounts/add-an-account-admin/response-body.md" />

---

### Remove an account admin

:::info
**DELETE** `/api/accounts/{account-id}/admins/{profile-id}`
:::

Removes the profile `{profile-id}` as an admin of the account `{account-id}`.

#### Prerequisites

- The authenticated user profile must be an owner of the account `{account-id}`
- Profile `{profile-id}` must be an admin of the account `{account-id}`

<Examples path="accounts/remove-an-account-admin" />

#### Response
`204 No Content`

No response body provided.

---

### Set an account owner

:::info
**PUT** `/api/accounts/{account-id}/owner/{profile-id}`
:::

Sets the profile `{profile-id}` as the primary owner of the account `{account-id}`.

#### Prerequisites

- The authenticated user profile must be an owner of the account `{account-id}`
- Profile `{profile-id}` must be an admin of the account `{account-id}`

<Examples path="accounts/set-an-account-owner" />

#### Response
`200 OK`

[Account](#account) with HAL links.
<Snippet path="accounts/set-an-account-owner/response-body.md" />

---

### Transfer a workspace

:::info
**PUT** `/api/accounts/{account-id}/workspaces/{workspace-id}/transfer`
:::

Transfers the workspace `{workspace-id}` to the account `{account-id}`.

#### Prerequisites

- The user must be the owner of the account `{account-id}`

<Examples path="workspaces/transfer-a-workspace" />

#### Response
`200 OK`

[Workspace](#workspace) with HAL links.
<Snippet path="accounts/transfer-a-workspace/response-body.md" />

---

##### See Also

- [Set the working account for a profile](profiles#set-the-working-account-for-a-profile)
