---
title: Alerts
description: Matatika Alerts resource reference documentation
---

import Snippet from '@site/src/components/Snippet';
import TabItem from '@theme/TabItem';
import Tabs from '@theme/Tabs';

Alerts can be created by users on [datasets](datasets). These alerts can then be used to inform users of information related to that dataset.

---

## Requests

### Initialise an alert on a dataset

:::info
**POST** `/datasets/{dataset-id}/alerts`
:::

Initialises a new alert on a dataset.

#### Prerequisites
- The authenticated user must own a Matatika account

#### Request

##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<Snippet path="alerts/initialise-an-alert-on-a-dataset/curl-request.md" />

</TabItem>
<TabItem value="python" label="Python (requests)">

<Snippet path="alerts/initialise-an-alert-on-a-dataset/python-requests.md" />

</TabItem>
</Tabs>

#### Response
`200 OK`

<Snippet path="alerts/initialise-an-alert-on-a-dataset/response-body.md" />

---

### Create an alert on a dataset

:::info
**PUT** `/datasets/{dataset-id}/alerts/{alert-id}`
:::

Create a new alert on a dataset.

#### Prerequisites
- The authenticated user must own a Matatika account

#### Request

##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<Snippet path="alerts/create-an-alert-on-a-dataset/curl-request.md" />

</TabItem>
<TabItem value="python" label="Python (requests)">

<Snippet path="alerts/create-an-alert-on-a-dataset/python-requests.md" />

</TabItem>
</Tabs>

#### Response
`201 Created`

<Snippet path="alerts/create-an-alert-on-a-dataset/response-body.md" />

---

### View alerts on a dataset

:::info
**GET** `/datasets/{dataset-id}/alerts`
:::

View alerts on a dataset.

#### Prerequisites
- The authenticated user must own a Matatika account

#### Request

##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<Snippet path="alerts/view-alerts-on-a-dataset/curl-request.md" />

</TabItem>
<TabItem value="python" label="Python (requests)">

<Snippet path="alerts/view-alerts-on-a-dataset/python-requests.md" />

</TabItem>
</Tabs>

#### Response
`200 OK`

<Snippet path="alerts/view-alerts-on-a-dataset/response-body.md" />

---

### View an alert

:::info
**GET** `/alerts/{alert-id}`
:::

View an alert.

#### Prerequisites
- The authenticated user must own a Matatika account

#### Request

##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<Snippet path="alerts/view-an-alert/curl-request.md" />

</TabItem>
<TabItem value="python" label="Python (requests)">

<Snippet path="alerts/view-an-alert/python-requests.md" />

</TabItem>
</Tabs>

#### Response
`200 OK`

<Snippet path="alerts/view-an-alert/response-body.md" />

---