---
title: Feed
description: Matatika Feed resource reference documentation
---

import Snippet from '@site/src/components/Snippet';
import TabItem from '@theme/TabItem';
import Tabs from '@theme/Tabs';

The feed returns the most relevant datasets for the authenticated user profile. [Member](members) interactions with datasets are scored, determining their position within the feed.

User and member interactions that affect a dataset's score:
- Creating or modifying a dataset
- Viewing a dataset
- Liking a dataset
- Commenting on a dataset

---

## Requests

### View the feed of a workspace

:::info
**GET** `/api/workspaces/{workspace-id}/feed`
:::

Returns the feed of the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<Snippet path="feed/view-a-workspace-feed/curl-request.md" />

</TabItem>
<TabItem value="python" label="Python (requests)">

<Snippet path="feed/view-a-workspace-feed/python-requests.md" />

</TabItem>
</Tabs>

#### Response
`200 OK`

[Dataset](datasets#dataset) collection with HAL links.
<Snippet path="feed/view-a-workspace-feed/response-body.md" />

---

##### See Also

- [View all datasets in a workspace](datasets#view-all-datasets-in-a-workspace)
