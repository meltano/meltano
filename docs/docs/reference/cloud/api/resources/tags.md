---
title: Tags
description: Matatika Tags resource reference documentation
---

import Snippet from '@site/src/components/Snippet';
import TabItem from '@theme/TabItem';
import Tabs from '@theme/Tabs';

Tags are hash-prefixed keywords or phrases that appear in the title, description, or comments of a dataset. Tags can be used to index datasets by their contained tags with a search, which allows for topical dataset categorisation.

---

## Objects

### Tag

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`id` | `string` | Version 4 UUID | The tag ID 
`name` | `string` | | The tag name
`usage` | `number` | Unsigned integer | Number of times the tag is used within the workspace

<Snippet path="tags/view-a-tag-in-a-workspace/response-body.md" />

---

## Requests

### View all tags in a workspace

:::info
**GET** `/api/workspaces/{workspace-id}/tags`
:::

Returns all tags in the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<Snippet path="tags/view-all-tags-in-a-workspace/curl-request.md" />

</TabItem>
<TabItem value="python" label="Python (requests)">

<Snippet path="tags/view-all-tags-in-a-workspace/python-requests.md" />

</TabItem>
</Tabs>

#### Response
`200 OK`

[Tag](#tag) collection with HAL links.

<Snippet path="tags/view-all-tags-in-a-workspace/response-body.md" />

---
### View all tags in the news for a workspace

:::info
**GET** `/api/workspaces/{workspace-id}/news/tags`
:::

Returns all tags in the news for the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist

#### Response
`200 OK`

[Tag](#tag) collection with HAL links.

---
### View a tag in a workspace

:::info
**GET** `/api/workspaces/{workspace-id}/tags/{tag-id}`
:::

Returns the tag `{tag-id}` in the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist
- Tag `{tag-id}` must exist

#### Request
##### Example Snippets
<Tabs>
<TabItem value="curl" label="cURL">

<Snippet path="tags/view-a-tag-in-a-workspace/curl-request.md" />

</TabItem>
<TabItem value="python" label="Python (requests)">

<Snippet path="tags/view-a-tag-in-a-workspace/python-requests.md" />

</TabItem>
</Tabs>

#### Response
`200 OK`

[Tag](#tag) with HAL links.

<Snippet path="tags/view-a-tag-in-a-workspace/response-body.md" />

---

##### See Also

- [Search for datasets in a workspace by tag name](search#search-for-datasets-in-a-workspace-by-tag-name)
