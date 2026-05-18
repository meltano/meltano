---
title: API Keys
description: Matatika API Keys resource reference documentation
permalink: /api/resources/apikeys
parent: Resources
grand_parent: API
nav_order: 18
components: request-md-components/apikeys
---

# {{page.title}}

API keys offer an alternate method of authentication to the Matatika API using a [client ID and secret](https://www.oauth.com/oauth2-servers/client-registration/client-id-secret/){:target="_blank"}. Access using API key credentials is supported by the Matatika [CLI]({{site.baseurl}}/cli) and [SDK]({{site.baseurl}}/sdk), which allows a user to remain authenticated permanently.
{: .fs-5 }

---

## Objects
{: .no_toc }

### API Key

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`id` | `string` | Version 4 UUID | The API key ID
`created` | `string` | ISO 8601 timestamp | The instant when the API key was created
`lastModified` | `string` | ISO 8601 timestamp | The instant when the API key was last modified
`name` | `string` | | The API key name
`clientId` | `string` | | The API key client ID
`profileId` | `string` | | The API key owner profile ID

{% include snippets/api/apikeys/view-an-api-key/response-body.md %}

---

#### Requests

- TOC
{: toc}

---

{% include {{page.components}}/view-all-api-keys.md %}
{% include {{page.components}}/view-an-api-key.md %}
{% include {{page.components}}/initialise-an-api-key.md %}
{% include {{page.components}}/create-an-api-key.md %}
{% include {{page.components}}/update-an-api-key.md %}
{% include {{page.components}}/delete-an-api-key.md %}
