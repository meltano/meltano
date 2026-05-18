---
title: Feed
description: Matatika Feed resource reference documentation
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

The feed returns the most relevant datasets for the authenticated user profile. [Member](members) interactions with datasets are scored, determining their position within the feed.

User and member interactions that affect a dataset's score:
- Creating or modifying a dataset
- Viewing a dataset
- Liking a dataset
- Commenting on a dataset

---

## Requests

### View the feed of a workspace

GET `/api/workspaces/{workspace-id}/feed`

Returns the feed of the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<!-- {% include snippets/api/feed/view-a-workspace-feed/curl-request.md %} -->

</TabItem>
<TabItem value="python" label="Python (requests)">

<!-- {% include snippets/api/feed/view-a-workspace-feed/python-requests.md %} -->

</TabItem>
</Tabs>

#### Response
`200 OK`

[Dataset](datasets#dataset) collection with HAL links.
<!-- {% include snippets/api/feed/view-a-workspace-feed/response-body.md %} -->

---

##### See Also

- [View all datasets in a workspace](datasets#view-all-datasets-in-a-workspace)
