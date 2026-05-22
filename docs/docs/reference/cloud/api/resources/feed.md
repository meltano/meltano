---
title: Feed
description: Meltano Cloud feed resource reference documentation
sidebar_position: 13
---

import Examples from '@site/src/components/Examples';
import Snippet from '@site/src/components/Snippet';

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

<Examples path="feed/view-a-workspace-feed" />

#### Response
`200 OK`

[Dataset](datasets#dataset) collection with HAL links.
<Snippet path="feed/view-a-workspace-feed/response-body.md" />

---

##### See Also

- [View all datasets in a workspace](datasets#view-all-datasets-in-a-workspace)
