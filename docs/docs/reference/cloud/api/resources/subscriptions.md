---
title: Subscriptions
description: Matatika Subscriptions resource reference documentation
permalink: /api/resources/subscriptions
parent: Resources
grand_parent: API
nav_order: 15
components: request-md-components/subscriptions
---

# {{page.title}}

Subscriptions are a declaration of interest in a particular resource, allowing a user to receive [notifications](notifications) when certain events occur. The events that trigger [notifications](notifications) are controlled by the [type of subscription](#subscription-type).
{: .fs-5 }

---

## Objects
{: .no_toc}

### Subscription

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`id` | `string` | Version 4 UUID | The subscription ID
`created` | `string` | ISO 8601 timestamp | The instant the subscription was created at
`lastModified` | `string` | ISO 8601 timestamp | The instant the subscription was last modified at
`type` | `string` | [Subscription Type](#subscription-type) | The type of subscription

{% include snippets/api/subscriptions/view-a-subscription/response-body.md %}

## Formats
{: .no_toc}

### Subscription Type
{: .d-inline-block }

`string`
{: .float-right .mt-5 }

Value | Description
----- | -----------
`ALL` | Triggers [notifications](notifications) for all resource events
`ALERTS` | Triggers [notifications](notifications) for resource alert events only
`NONE` | Does not trigger any [notifications](notifications)

---

#### Requests

- TOC
{: toc }

---

{% include {{page.components}}/view-all-subscriptions.md %}
{% include {{page.components}}/view-all-member-subscriptions-to-a-workspace.md %}
{% include {{page.components}}/view-a-subscription.md %}
{% include {{page.components}}/subscribe-to-a-workspace.md %}
{% include {{page.components}}/subscribe-to-a-channel.md %}
{% include {{page.components}}/subscribe-to-a-dataset.md %}
{% include {{page.components}}/subscribe-to-a-pipeline.md %}
{% include {{page.components}}/update-a-subscription.md %}
{% include {{page.components}}/remove-a-subscription.md %}
