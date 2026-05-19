---
title: Search
description: Matatika Search resource reference documentation
---

import Snippet from '@site/src/components/Snippet';
import TabItem from '@theme/TabItem';
import Tabs from '@theme/Tabs';

[Datasets](datasets#dataset) can be searched for within their containing [workspace](workspaces). Searches can filter datasets by arbitrary text, [channel](channels) name, or [tag](tags) name.

See [here]({{site.baseurl}}/api/links#search) for more information on constructing a search filter query.

---

## Requests

### Search for datasets in a workspace by free text

:::info
**GET** `/api/workspaces/{workspaces-id}/search?q={free-text}`
:::

Searches the workspace `{workspace-id}` for datasets by the free text `{free-text}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<Snippet path="search/search-for-datasets-in-a-workspace-by-free-text/curl-request.md" />

</TabItem>
<TabItem value="python" label="Python (requests)">

<Snippet path="search/search-for-datasets-in-a-workspace-by-free-text/python-requests.md" />

</TabItem>
</Tabs>

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

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<Snippet path="search/search-for-datasets-in-a-workspace-by-channel-name/curl-request.md" />

</TabItem>
<TabItem value="python" label="Python (requests)">

<Snippet path="search/search-for-datasets-in-a-workspace-by-channel-name/python-requests.md" />

</TabItem>
</Tabs>

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

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<Snippet path="search/search-for-datasets-in-a-workspace-by-tag-name/curl-request.md" />

</TabItem>
<TabItem value="python" label="Python (requests)">

<Snippet path="search/search-for-datasets-in-a-workspace-by-tag-name/python-requests.md" />

</TabItem>
</Tabs>

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

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<Snippet path="search/msearch-in-a-workspace-by-free-text/curl-request.md" />

</TabItem>
<TabItem value="python" label="Python (requests)">

<Snippet path="search/msearch-in-a-workspace-by-free-text/python-requests.md" />

</TabItem>
</Tabs>

#### Response
`200 OK`

<Snippet path="search/msearch-in-a-workspace-by-free-text/response-body.md" />

`204 No Content`

No response body provided.

---
