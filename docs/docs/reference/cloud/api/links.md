---
title: Links
description: Reference documentation for link relations used by the Matatika API to communicate the capabilities of our resources
permalink: /api/links
parent: API
nav_order: 8
---

# {{page.title}}

The Matatika API uses link relations to communicate the capabilities of our resources.  Where you see a link with one of the following relations, you can expect our API to act accordingly provided nothing has changed in the meantime.
{: .fs-5 }

---

## Resource Type Relations

All resource types define an item and collection relation. These appear as or in (alongside [actions](#actions)) link relations throughout the Matatika API.

Resource | Item relation | Collection relation
-------- | ------------- | -------------------
[Profile](resources/profiles) | `profile` | `profiles`
[Workspace](resources/workspaces) | `workspace` | `workspaces`
[Invitation](resources/invitations) | `invitation` | `invitations`
[Member](resources/members) | `member` | `members`
[Administrator](resources/administrators) | `administrator` | `administrators`
[Dataset](resources/datasets) | `dataset` | `datasets`
[Channel](resources/channels) | `channel` | `channels`
[Comment](resources/comments) | `comment` | `comments`
[Tag](resources/tags) | `tag` | `tags`
[Dataplugin](resources/dataplugins) | `dataplugin` | `dataplugins`
[Datastore](resources/datastores) | `datastore` | `datastores`
[Pipeline](resources/pipelines) | `pipeline` | `pipelines`
[Job](resources/jobs) | `job` | `jobs`
[Subscription](resources/subscriptions) | `subscription` | `subscriptions`
[Notification](resources/notifications) | `notification` | `notifications`
[API Key](resources/apikeys) | `apikey` | `apikeys`

A link relation formed entirely from an item or collection relation will accept a <span>GET</span>{:.label .label-GET} request and return the respective resource. Expect `200 OK` to indicate the resource was successfully returned.

---

## Paging, Sizing and Sorting
Collection link relations accept paging, sizing and sorting query parameters, which can be used to modify the dimensions of the response payload.

Query Parameter | Description | Syntax | Example
--------------- | ----------- | ------ | -------
`page` | The page of the collection | `page={page-number}` | `?page=1`
`size` | The number of elements to display per page | `size={number-of-elements}` | `?size=20`
`sort` | The property to sort the collection results by, in either ascending - `asc` - or descending - `desc` -  order | `sort={property-name},(asc|desc)` | `?sort=name,asc`

---

## Searching and Filtering
A [`search` action](#search) indicates the acceptance of the `q` query parameter, which is used to filter the content returned in the response payload. Filter definitions control the type of filtering applied.

### Filter

Type | Description | Syntax | Example
---- | ----------- | ------ | -------
Free text | The free text to filter by | `{free-text}` | `?q=data%20insights`
Channel | The [channel](resources/channels) to filter by | `in:{channel-name}` | `?q=in:matatika-limited`
Tag | The [tag](resources/tags) to filter by | `tag:{tag-name}` | `?q=tag:jupyternotebook`

The Matatika API supports multiple filter definitions, including those of the same type:

```
?q=data%20insights in:matatika-limited tag:jupyternotebook`
```

```
?tag:ai tag:deeplearning tag:machinelearning
```

---

## Actions
Actions are phrases that define the behaviour of a HTTP transaction. A link relation is formed from an action verb either entirely or in conjunction with a subject resource relation in the format `"{action} {resource-relation}"`.

```
"self"
"update workspace"
"publish dataset"
"create pipeline"
"new job"
```

### `latest`
Make a <span>GET</span>{:.label .label-GET} request to this link to return the latest resource. Expect `200 OK` to indicate the resource was successfully returned.

### `search`
Make a <span>GET</span>{:.label .label-GET} request to this link to a return a [filtered view](#searching-and-filtering) of the current respective resource. Expect `200 OK` to indicate the resource was successfully returned.

### `self`
Make a  <span>GET</span>{:.label .label-GET} request to this link to return the current respective resource. Expect `200 OK` to indicate the resource was successfully returned.

### `new`
Make a <span>POST</span>{:.label .label-POST} request to this link to initialise a new resource. Expect `200 OK` to indicate the resource was successfully initialised.

### `publish`
Make a <span>POST</span>{:.label .label-POST} request to this link to publish data into a resource. Expect `201 Created` or `200 OK` to indicate the resource was successfully published.

### `validate`
Make a <span>POST</span>{:.label .label-POST} request to this link to validate a resource. Expect `200 OK` to indicate the resource was successfully validated.

### `verify`
Make a <span>POST</span>{:.label .label-POST} request to this link to verify a resource. Expect `200 OK` to indicate the resource was successfully verified.

### `add`
Make a <span>PUT</span>{:.label .label-PUT} request to this link to add a new resource. Expect `200 OK` to indicate the resource was successfully added.

### `create`
Make a <span>PUT</span>{:.label .label-PUT} request to this link to create a new resource. Expect `201 Created` or `202 Accepted` to indicate the resource was successfully created.

### `draft`
Make a <span>PUT</span>{:.label .label-PUT} request to this link to create or update a draft resource. Expect `200 OK` or `201 Created` to indicate the resource was successfully drafted.

### `make-default`
Make a <span>PUT</span>{:.label .label-PUT} request to this link to set a particular resource within a collection as default. Expect `200 OK` to indicate the resource was successfully set as default.

### `update`
Make a <span>PUT</span>{:.label .label-PUT} request to this link to update a resource. Expect `200 OK` to indicate the resource was successfully updated.

### `withdraw` 
Make a <span>PUT</span>{:.label .label-PUT} request to this link to withdraw a resource. Expect `200 OK` to indicate the resource was successfully withdrawn.

### `edit`
Make a <span>PATCH</span>{:.label .label-PATCH} request to this link to edit a resource. Expect `200 OK` to indicate the resource was successfully edited.

### `delete`
Make a <span>DELETE</span>{:.label .label-DELETE} request to this link to delete a resource. Expect `204 No Content` to indicate the resource was successfully deleted.
