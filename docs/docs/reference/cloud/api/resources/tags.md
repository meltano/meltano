---
title: Tags
description: Matatika Tags resource reference documentation
permalink: /api/resources/tags
parent: Resources
grand_parent: API
nav_order: 8
components: request-md-components/tags
---

# {{page.title}}

Tags are hash-prefixed keywords or phrases that appear in the title, description, or comments of a dataset. Tags can be used to index datasets by their contained tags with a search, which allows for topical dataset categorisation.
{: .fs-5 }

---

## Objects
{: .no_toc}

### Tag

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`id` | `string` | Version 4 UUID | The tag ID 
`name` | `string` | | The tag name
`usage` | `number` | Unsigned integer | Number of times the tag is used within the workspace

{% include snippets/api/tags/view-a-tag-in-a-workspace/response-body.md %}

---

#### Requests

- TOC
{: toc }

#### See Also

- [Search for datasets in a workspace by tag name](search#search-for-datasets-in-a-workspace-by-tag-name)

---

{% include {{ page.components }}/view-all-tags-in-a-workspace.md %}
{% include {{ page.components }}/view-all-tags-in-the-news-for-a-workspace.md %}
{% include {{ page.components }}/view-a-tag-in-a-workspace.md %}

