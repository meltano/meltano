---
title: Search
description: Meltano Cloud search resource reference documentation
sidebar_position: 12
---

import Examples from '@site/src/components/Examples';
import Snippet from '@site/src/components/Snippet';

[Datasets](datasets#dataset) can be searched for within their containing [workspace](workspaces). Searches can filter datasets by arbitrary text, [channel](channels) name, or [tag](tags) name.

See [here](/reference/cloud/api/links#searching-and-filtering) for more information on constructing a search filter query.

---

## Requests

### Search for datasets in a workspace by free text

:::info
**GET** `/api/workspaces/{workspaces-id}/search?q={free-text}`
:::

Searches the workspace `{workspace-id}` for datasets by the free text `{free-text}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist

<Examples path="search/search-for-datasets-in-a-workspace-by-free-text" />

#### Response
`200 OK`

<Snippet path="search/search-for-datasets-in-a-workspace-by-free-text/response-body.md" />

`204 No Content`

No response body provided.

---

### Search for datasets in a workspace by channel name

:::info
**GET** `/api/workspaces/{workspaces-id}/search?q=in:{channel-name}`
:::

Searches the workspace `{workspace-id}` for datasets by the channel `{channel-name}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist

<Examples path="search/search-for-datasets-in-a-workspace-by-channel-name" />

#### Response
`200 OK`

[Dataset](datasets#dataset) collection with HAL links.
<Snippet path="search/search-for-datasets-in-a-workspace-by-channel-name/response-body.md" />

`204 No Content`

No response body provided.

---

### Search for datasets in a workspace by tag name

:::info
**GET** `/api/workspaces/{workspace-id}/search?q=tag:{tag-name}`
:::

Searches the workspace `{workspace-id}` for datasets by the tag `{tag-name}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist

<Examples path="search/search-for-datasets-in-a-workspace-by-tag-name" />

#### Response
`200 OK`

<Snippet path="search/search-for-datasets-in-a-workspace-by-tag-name/response-body.md" />

`204 No Content`

No response body provided.

---

### Search for datasets in a workspace using msearch

:::info
**POST** `/api/workspaces/{workspace-id}/datasets/_msearch`
:::

Searches the workspace `{workspace-id}` for datasets using an elastic search query.

#### Prerequisites
- Workspace `{workspace-id}` must exist

<Examples path="search/msearch-in-a-workspace-by-free-text" />

#### Response
`200 OK`

<Snippet path="search/msearch-in-a-workspace-by-free-text/response-body.md" />

`204 No Content`

No response body provided.

---
