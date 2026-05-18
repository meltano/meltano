---
title: Notifications
description: Matatika Notifications resource reference documentation
permalink: /api/resources/notifications
parent: Resources
grand_parent: API
nav_order: 16
components: request-md-components/notifications
---

# {{page.title}}

Notifications are alerts triggered by certain events pertaining to a resource. To receive notifications for a specific resource, a user must have a [subscription](subscriptions) to the resource.
{: .fs-5 }

---

## Objects
{: .no_toc}

### Notification

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`id` | `string` | Version 4 UUID | The notification ID
`created` | `string` | ISO 8601 timestamp | The instant the notification was created at
`lastModified` | `string` | ISO 8601 timestamp | The instant the notification was last modified at
`actor` | `object` | [`Member`](members#member) | The member whose action raised this notification
`type` | `string` | [Notification Type](#notification-type) | The type of notification
`resolved` | `bool` | | Whether or not the notification has been read

{% include snippets/api/notifications/view-a-notification/response-body.md %}

## Formats
{: .no_toc}

### Notification Type
{: .d-inline-block }

`string`
{: .float-right .mt-5 }

Value | Description
----- | -----------
`DATASET_ACTIVITY` | Any activity on the [dataset](datasets#dataset)
`DATASET_ANOMOLY` | A detected anomoly in the [dataset](datasets#dataset) data
`DATASET_COMMENT` | A [comment](comments#comment) on the [dataset](datasets#dataset)
`DATASET_LIKE` | A [like](datasets#record-a-like-of-a-dataset) recorded on the [dataset](datasets#dataset)
`DATASET_MESSAGE` | A [message](datasets#dataset-message) about the [dataset](datasets#dataset)
`JOB_STARTED` | A [job](jobs#job) started for a [pipeline](pipelines#pipeline)
`JOB_ENDED` | A [job](jobs#job) ended for a [pipeline](pipelines#pipeline)

---

#### Requests

- TOC
{: toc }

#### See Also

- [Create or update a dataset message](datasets#create-or-update-a-dataset-message)

---

{% include {{page.components}}/view-all-notifications.md %}
{% include {{page.components}}/view-all-notifications-for-a-workspace.md %}
{% include {{page.components}}/view-a-notification.md %}
{% include {{page.components}}/refresh-notifications.md %}
{% include {{page.components}}/delete-a-notification.md %}

