---
title: Subscriptions
description: Matatika Subscriptions resource reference documentation
components: request-md-components/subscriptions
---

Subscriptions are a declaration of interest in a particular resource, allowing a user to receive [notifications](notifications) when certain events occur. The events that trigger [notifications](notifications) are controlled by the [type of subscription](#subscription-type).

---

## Objects

### Subscription

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`id` | `string` | Version 4 UUID | The subscription ID
`created` | `string` | ISO 8601 timestamp | The instant the subscription was created at
`lastModified` | `string` | ISO 8601 timestamp | The instant the subscription was last modified at
`type` | `string` | [Subscription Type](#subscription-type) | The type of subscription

<!-- {% include snippets/api/subscriptions/view-a-subscription/response-body.md %} -->

## Formats

### Subscription Type

`string`

Value | Description
----- | -----------
`ALL` | Triggers [notifications](notifications) for all resource events
`ALERTS` | Triggers [notifications](notifications) for resource alert events only
`NONE` | Does not trigger any [notifications](notifications)

---

#### Requests

---

<!-- {% include {{page.components}}/view-all-subscriptions.md %}
{% include {{page.components}}/view-all-member-subscriptions-to-a-workspace.md %}
{% include {{page.components}}/view-a-subscription.md %}
{% include {{page.components}}/subscribe-to-a-workspace.md %}
{% include {{page.components}}/subscribe-to-a-channel.md %}
{% include {{page.components}}/subscribe-to-a-dataset.md %}
{% include {{page.components}}/subscribe-to-a-pipeline.md %}
{% include {{page.components}}/update-a-subscription.md %}
{% include {{page.components}}/remove-a-subscription.md %} -->
