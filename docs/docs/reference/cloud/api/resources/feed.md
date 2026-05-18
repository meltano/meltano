---
title: Feed
description: Matatika Feed resource reference documentation
permalink: /api/resources/feed
parent: Resources
grand_parent: API
nav_order: 9
components: request-md-components/feed
---

# {{page.title}}

The feed returns the most relevant datasets for the authenticated user profile. [Member](members) interactions with datasets are scored, determining their position within the feed.
{: .fs-5 }

User and member interactions that affect a dataset's score:
- Creating or modifying a dataset
- Viewing a dataset
- Liking a dataset
- Commenting on a dataset

---

#### Requests

- TOC
{: toc }

#### See Also

- [View all datasets in a workspace](datasets#view-all-datasets-in-a-workspace)

---

{% include {{ page.components }}/view-the-feed-of-a-workspace.md %}
