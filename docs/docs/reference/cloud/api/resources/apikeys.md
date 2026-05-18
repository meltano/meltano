---
title: API Keys
description: Matatika API Keys resource reference documentation
---

API keys offer an alternate method of authentication to the Matatika API using a [client ID and secret](https://www.oauth.com/oauth2-servers/client-registration/client-id-secret/). Access using API key credentials is supported by the Matatika [CLI]({{site.baseurl}}/cli) and [SDK]({{site.baseurl}}/sdk), which allows a user to remain authenticated permanently.

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

<!-- {% include snippets/api/apikeys/view-an-api-key/response-body.md %} -->

---

## Requests

### View all API keys

GET `/api/apikeys`

Returns all API keys owned by the authenticated user profile.

#### Prerequisites
- The authenticated user must own a Matatika account
- The API key `{apikey-id}` must exist

#### Request

##### Example Snippets
cURL

<!-- {% include snippets/api/apikeys/view-all-api-keys/curl-request.md %} -->

Python (`requests`)

<!-- {% include snippets/api/apikeys/view-all-api-keys/python-requests.md %} -->

#### Response
`200 OK`

[API key](#api-key) collection with HAL links.
<!-- {% include snippets/api/apikeys/view-all-api-keys/response-body.md %} -->

---
### View an API key

GET `/api/apikeys/{apikey-id}`

Returns the API key `{apikey-id}`.

#### Prerequisites
- The authenticated user must own a Matatika account
- The API key `{apikey-id}` must exist

#### Request

##### Example Snippets
cURL

<!-- {% include snippets/api/apikeys/view-an-api-key/curl-request.md %} -->

Python (`requests`)

<!-- {% include snippets/api/apikeys/view-an-api-key/python-requests.md %} -->

#### Response
`200 OK`

[API key](#api-key) with HAL links.
<!-- {% include snippets/api/apikeys/view-an-api-key/response-body.md %} -->

---
### Initialise an API key

POST `/api/apikeys`

Initialises a new API key.

#### Prerequisites
- The authenticated user must own a Matatika account

#### Request

##### Example Snippets
cURL

<!-- {% include snippets/api/apikeys/initialise-an-api-key/curl-request.md %} -->

Python (`requests`)

<!-- {% include snippets/api/apikeys/initialise-an-api-key/python-requests.md %} -->

#### Response
`200 OK`

[API key](#api-key) with HAL links.
<!-- {% include snippets/api/apikeys/initialise-an-api-key/response-body.md %} -->

---
### Create an API key

PUT `/api/apikeys/{apikey-id}`

Creates the API key `{apikey-id}`.

#### Prerequisites
- The authenticated user must own a Matatika account

#### Request

##### Body
[API key](#api-key) resource.
<!-- {% include snippets/api/apikeys/create-an-api-key/request-body.md %} -->

##### Example Snippets
cURL

<!-- {% include snippets/api/apikeys/create-an-api-key/curl-request.md %} -->

Python (`requests`)

<!-- {% include snippets/api/apikeys/create-an-api-key/python-requests.md %} -->

#### Response
`201 Created`

[API key](#api-key) with HAL links.
<!-- {% include snippets/api/apikeys/create-an-api-key/response-body.md %} -->

---
### Update an API key

PUT `/api/apikeys/{apikey-id}`

Updates the API key `{apikey-id}`.

#### Prerequisites
- The authenticated user must own a Matatika account

#### Request

##### Body
[API key](#api-key) resource.
<!-- {% include snippets/api/apikeys/update-an-api-key/request-body.md %} -->

##### Example Snippets
cURL

<!-- {% include snippets/api/apikeys/update-an-api-key/curl-request.md %} -->

Python (`requests`)

<!-- {% include snippets/api/apikeys/update-an-api-key/python-requests.md %} -->

#### Response
`200 OK`

[API key](#api-key) with HAL links.
<!-- {% include snippets/api/apikeys/update-an-api-key/response-body.md %} -->

---
### Delete an API key

DELETE `/api/apikeys/{apikey-id}`

Deletes the API key `{apikey-id}`.

#### Prerequisites
- The authenticated user must own a Matatika account
- The API key `{apikey-id}` must exist

#### Request

##### Example Snippets
cURL

<!-- {% include snippets/api/apikeys/delete-an-api-key/curl-request.md %} -->

Python (`requests`)

<!-- {% include snippets/api/apikeys/delete-an-api-key/python-requests.md %} -->

#### Response
`204 No Content`

No response body provided.

---
