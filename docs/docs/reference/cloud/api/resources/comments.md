---
title: Comments
description: Matatika Comments resource reference documentation
permalink: /api/resources/comments
parent: Resources
grand_parent: API
nav_order: 7
components: request-md-components/comments
---

# {{page.title}}

Comments aid conversation and collaboration around workspace datasets. Comments can be made on datasets, or other comments to form threads.
{: .fs-5 }

---

## Objects
{: .no_toc}

### Comment

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`id` | `string` | Version 4 UUID | The comment ID
`message` | `string` | | The comment message
`likeCount` | `number` | Unsigned integer | The number of likes the comment has received
`likedByProfiles` | `object[]` | Array of [`Member`](members#member)s | The workspace members that have liked the comment
`created` | `string` | ISO 8601 timestamp | Timestamp denoting when the comment was created
`lastModified` | `string` | ISO 8601 timestamp | Timestamp denoting when the comment was last modified
`from` | `object` | [`Member`](members#member) | The comment author
`commentCount` | `number` | Unsigned integer | The number of replies the comment has received
`datasetId` | `string` | Version 4 UUID | The ID of the dataset comment subject
`parentId` | `string` | Version 4 UUID | The ID of the parent comment

{% include snippets/api/comments/view-a-comment/response-body.md %}

---

#### Requests

- TOC
{: toc }

---

{% include {{ page.components }}/view-all-comments-on-a-dataset.md %}
{% include {{ page.components }}/view-a-comment.md %}
{% include {{ page.components }}/view-the-edit-history-of-a-comment.md %}
{% include {{ page.components }}/view-all-replies-to-a-comment.md %}
{% include {{ page.components }}/initialise-a-comment-on-a-dataset.md %}
{% include {{ page.components }}/initialise-a-reply-to-a-comment.md %}
{% include {{ page.components }}/create-a-comment.md %}
{% include {{ page.components }}/update-a-comment.md %}
{% include {{ page.components }}/record-a-like-of-a-comment.md %}
{% include {{ page.components }}/remove-a-like-from-a-comment.md %}
{% include {{ page.components }}/delete-a-comment.md %}
