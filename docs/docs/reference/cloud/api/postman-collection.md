---
title: Postman Collection
description: Get started with a Postman collection for the Matatika API - contains all the requests and documentation.
permalink: /api/postman-collection
parent: API
nav_order: 1
---

# {{page.title}}

---

We automatically maintain a fully-tested Postman collection for the Matatika API, which contains all the requests documented for each [resource](resources) type.

Simply import the following collection URL into Postman to begin sending requests:

`{{site.matatika.links.www}}/docs/matatika.json`{: #postman-collection-url .fs-5 }
{: .text-center }

---

## Setting Up Authorisation

The following steps outline how to set-up authorisation in Postman for the Matatika API collection using a Bearer token:

1. [Get a token from the Matatika app]({{site.baseurl}}/security#getting-a-developer-token)
2. In the Postman application, locate the imported 'Matatika API' collection and click *Edit*
3. Under the *Variables* tab, locate the variable `BEARER_TOKEN` and paste the token into the *CURRENT VALUE* text field
4. Click *Update*

---

## Collection Variables

{% raw %}
When running any request within the collection for the first time, the collection pre-request script will automatically attempt to populate the `{{profile-id}}` and `{{workspace-id}}` collection variables based on the provided token.
{% endraw %}

These variables can be manually created, set, and deleted when editing the collection, if required.
