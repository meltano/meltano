---
title: Datasets
description: Matatika Datasets resource reference documentation
permalink: /api/resources/datasets
parent: Resources
grand_parent: API
nav_order: 5
components: request-md-components/datasets
---

# {{page.title}}

Datasets are modules of data that can be published to workspaces. Datasets are visualised in the Matatika app following the [Chart.js](https://www.chartjs.org/){:target="_blank"} specifications.
{: .fs-5 }

---

## Objects
{: .no_toc}

### Dataset

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`id` | `string` | Version 4 UUID | The dataset ID
`published` | `string` | ISO 8601 timestamp | The instant the dataset was published
`alias` | `string` | | The dataset alias
`workspaceId` | `string` | Version 4 UUID | The workspace ID of the published dataset
`source` | `string` | | The channel ID where the dataset was initially published to
`title` | `string` | | The dataset title
`description` | `string` | | The dataset description (may contain markdown)
`questions` | `string` | | The dataset questions
`rawData` | `string` | JSON | The dataset raw data
`visualisation` | `string` | JSON | The dataset visualisation metadata. [More Info]({{site.baseurl}}/dataml/datasetml/visualisation)
`metadata` | `string` | JSON | The dataset metadata. [More Info]({{site.baseurl}}/dataml/datasetml/metadata)
`query` | `string` | SQL statement | The dataset query. [More Info]({{site.baseurl}}/dataml/datasetml/query)
`likeCount` | `number` | Unsigned integer | The number of likes the dataset has received
`likedByProfiles` | `object[]` | Array of [`Member`](members#member)s | The members that have liked the dataset
`commentCount` | `number` | Unsigned integer | The number of comments the dataset has received
`viewCount` | `number` | Unsigned integer | The number of views the dataset has received
`created` | `string` | ISO 8601 timestamp | The instant the dataset was create
`score` | `number` | Decimal | The dataset score used to determine its position in the workspace [Feed](feed)

{% include snippets/api/datasets/view-a-dataset/response-body.md %}

### Dataset Message

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`id` | `string` | Version 4 UUID | The dataset message ID (shared with the resulting [notification](notifications))
`recipientId` | `string` | | The recipient profile ID
`message` | `string` | | The dataset message content
`datasetId` | `string` | Version 4 UUID | The message subject dataset ID

{% include snippets/api/datasets/create-or-update-a-dataset-message/response-body.md %}

---

#### Requests

- TOC
{: toc }

#### See Also

- [View all comments on a dataset](comments#view-all-comments-on-a-dataset)
- [Search for datasets in a workspace by free text](search#search-for-datasets-in-a-workspace-by-free-text)
- [Search for datasets in a workspace by channel name](search#search-for-datasets-in-a-workspace-by-channel-name)
- [Search for datasets in a workspace by tag name](search#search-for-datasets-in-a-workspace-by-tag-name)
- [Subscribe to a dataset](subscriptions#subscribe-to-a-dataset)

---

{% include {{ page.components }}/view-all-datasets-in-a-workspace.md %}
{% include {{ page.components }}/view-datasets-in-a-workspace-liked-by-profile.md %}
{% include {{ page.components }}/view-datasets-by-channel.md %}
{% include {{ page.components }}/view-a-dataset.md %}
{% include {{ page.components }}/view-a-dataset-in-a-workspace.md %}
{% include {{ page.components }}/view-the-data-of-a-dataset.md %}
{% include {{ page.components }}/publish-a-dataset-to-a-workspace.md %}
{% include {{ page.components }}/edit-a-dataset.md %}
{% include {{ page.components }}/record-a-view-of-a-dataset.md %}
{% include {{ page.components }}/record-a-like-of-a-dataset.md %}
{% include {{ page.components }}/remove-a-like-from-a-dataset.md %}
{% include {{ page.components }}/initialise-a-new-dataset-message.md %}
{% include {{ page.components }}/create-or-update-a-dataset-message.md %}
{% include {{ page.components }}/delete-a-dataset.md %}

---

Further Reading:

- [Matatika dataset YAML file]({{site.baseurl}}/dataml/datasetml/)
- [Example Charts]({{site.baseurl}}/dataml/datasetml/basic-examples)