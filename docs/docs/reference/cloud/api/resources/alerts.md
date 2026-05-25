---
title: Alerts
description: Meltano Cloud API alerts resource reference documentation
sidebar_position: 9
---

import Examples from '@site/src/components/Examples';
import Snippet from '@site/src/components/Snippet';

Alerts can be created by users on [datasets](datasets). These alerts can then be used to inform users of information related to that dataset.

---

## Requests

### Initialise an alert on a dataset

:::info
**POST** `/datasets/{dataset-id}/alerts`
:::

Initialises a new alert on a dataset.

#### Prerequisites
- The authenticated user must own a Meltano Cloud account

<Examples path="alerts/initialise-an-alert-on-a-dataset" />

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
- The authenticated user must own a Meltano Cloud account

<Examples path="alerts/create-an-alert-on-a-dataset" />

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
- The authenticated user must own a Meltano Cloud account

<Examples path="alerts/view-alerts-on-a-dataset" />

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
- The authenticated user must own a Meltano Cloud account

<Examples path="alerts/view-an-alert" />

#### Response
`200 OK`

<Snippet path="alerts/view-an-alert/response-body.md" />

---
