---
title: API Keys
description: Meltano Cloud API keys resource reference documentation
sidebar_position: 22
---

import Examples from '@site/src/components/Examples';
import Snippet from '@site/src/components/Snippet';

API keys offer an alternate method of authentication to the Meltano Cloud API using a [client ID and secret](https://www.oauth.com/oauth2-servers/client-registration/client-id-secret/).

---

## Objects

### API Key

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`id` | `string` | Version 4 UUID | The API key ID
`created` | `string` | ISO 8601 timestamp | The instant when the API key was created
`lastModified` | `string` | ISO 8601 timestamp | The instant when the API key was last modified
`name` | `string` | | The API key name
`clientId` | `string` | | The API key client ID
`profileId` | `string` | | The API key owner profile ID

<Snippet path="apikeys/view-an-api-key/response-body.md" />

---

## Requests

### View all API keys

:::info
**GET** `/api/apikeys`
:::

Returns all API keys owned by the authenticated user profile.

#### Prerequisites
- The authenticated user must own a Meltano Cloud account
- The API key `{apikey-id}` must exist

<Examples path="apikeys/view-all-api-keys" />

#### Response
`200 OK`

[API key](#api-key) collection with HAL links.
<Snippet path="apikeys/view-all-api-keys/response-body.md" />

---

### View an API key

:::info
**GET** `/api/apikeys/{apikey-id}`
:::

Returns the API key `{apikey-id}`.

#### Prerequisites
- The authenticated user must own a Meltano Cloud account
- The API key `{apikey-id}` must exist

<Examples path="apikeys/view-an-api-key" />

#### Response
`200 OK`

[API key](#api-key) with HAL links.
<Snippet path="apikeys/view-an-api-key/response-body.md" />

---

### Initialise an API key

:::info
**POST** `/api/apikeys`
:::

Initialises a new API key.

#### Prerequisites
- The authenticated user must own a Meltano Cloud account

<Examples path="apikeys/initialise-an-api-key" />

#### Response
`200 OK`

[API key](#api-key) with HAL links.
<Snippet path="apikeys/initialise-an-api-key/response-body.md" />

---

### Create an API key

:::info
**PUT** `/api/apikeys/{apikey-id}`
:::

Creates the API key `{apikey-id}`.

#### Prerequisites
- The authenticated user must own a Meltano Cloud account


#### Body
[API key](#api-key) resource.
<Snippet path="apikeys/create-an-api-key/request-body.md" />


<Examples path="apikeys/create-an-api-key" />

#### Response
`201 Created`

[API key](#api-key) with HAL links.
<Snippet path="apikeys/create-an-api-key/response-body.md" />

---

### Update an API key

:::info
**PUT** `/api/apikeys/{apikey-id}`
:::

Updates the API key `{apikey-id}`.

#### Prerequisites
- The authenticated user must own a Meltano Cloud account


#### Body
[API key](#api-key) resource.
<Snippet path="apikeys/update-an-api-key/request-body.md" />


<Examples path="apikeys/update-an-api-key" />

#### Response
`200 OK`

[API key](#api-key) with HAL links.
<Snippet path="apikeys/update-an-api-key/response-body.md" />

---

### Delete an API key

:::info
**DELETE** `/api/apikeys/{apikey-id}`
:::

Deletes the API key `{apikey-id}`.

#### Prerequisites
- The authenticated user must own a Meltano Cloud account
- The API key `{apikey-id}` must exist

<Examples path="apikeys/delete-an-api-key" />

#### Response
`204 No Content`

No response body provided.

---
