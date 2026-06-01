---
title: Postman Collection
description: Get started with a Postman collection for the Meltano Cloud API - contains all the requests and documentation.
sidebar_position: 1
---

import BrowserOnly from '@docusaurus/BrowserOnly';
import CodeBlock from '@theme/CodeBlock';

We automatically maintain a fully-tested Postman collection for the Meltano Cloud API, which contains all the requests documented for each [resource](resources) type.

Simply import the following collection URL into Postman to begin sending requests:

<BrowserOnly>
  {() => <CodeBlock>{window.location.origin}/reference/cloud/api/postman_collection.json</CodeBlock>}
</BrowserOnly>

---

## Setting Up Authorisation

The following steps outline how to set-up authorisation in Postman for the Meltano Cloud API collection using a Bearer token:

1. [Get a token from Meltano Cloud](https://app.meltano.com/api-key)
2. In the Postman application, locate the imported 'Meltano Cloud API' collection and click *Edit*
3. Under the *Variables* tab, locate the variable `BEARER_TOKEN` and paste the token into the *CURRENT VALUE* text field
4. Click *Update*

---

## Collection Variables

When running any request within the collection for the first time, the collection pre-request script will automatically attempt to populate the `{{profile-id}}` and `{{workspace-id}}` collection variables based on the provided token.

These variables can be manually created, set, and deleted when editing the collection, if required.
