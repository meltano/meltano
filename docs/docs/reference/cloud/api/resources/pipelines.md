---
title: Pipelines
description: Meltano Cloud pipelines resource reference documentation
sidebar_position: 18
---

import Examples from '@site/src/components/Examples';
import Snippet from '@site/src/components/Snippet';

A pipeline defines a set of runnable actions composed from [datacomponents](datacomponents) to complete a set of tasks - for example, [ELT](https://en.wikipedia.org/wiki/Extract,_load,_transform). Pipelines are run as [jobs](jobs), either manually or on a predetermined schedule. Only a single pipeline can be run at any given time.

---

## Objects

### Pipeline

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`id` | `string` | Version 4 UUID | The pipeline ID
`status` | `string` | [Pipeline Status](#pipeline-status)
`name` | `string` | | The pipeline name
`schedule` | `string` | Cron | The interval at which to launch a new job e.g. `0 0 9-17 * * MON-FRI` launches a job on the hour nine-to-five weekdays
`timeout` | `number` | Unsigned integer | The number of seconds after which the job will terminate - if set to `0`, an implicit default value of 300 seconds is used
`maxRetries` | `number` | Unsigned integer | The maximum number of retries to attempt for a job ending with `ERROR`
`script` | `string` | Bash script | Custom script to execute during a [job](jobs)
`created` | `string` | ISO 8601 timestamp | When the pipeline was created
`lastModified` | `string` | ISO 8601 timestamp | When the pipeline was last modified
`properties` | `object` | [`Properties`](#properties) | The pipeline properties, defined by the [dataplugin](dataplugins) [`settings`](dataplugins#setting) of each [datacomponent](datacomponents)<br/>Properties are key-value pairs, where keys reference setting `name`s qualified by datacomponent `name`s
`dataComponents` | `string[]` | Array of [datacomponent](datacomponents) `name`s | The pipeline [datacomponent](datacomponents) `name`s or create / update with [dataplugin](dataplugins#dataplugin) `fullyQualifiedName`
`actions` | `string[]` | Array of [datacomponent](datacomponents) `name`s or commands | The pipeline actions to run during a [job](jobs)
`triggeredBy` | `string[]` | Array of [pipeline](pipelines) `name`s or workspace task identifiers | Pipelines or workspace tasks that will trigger the pipeline on successful completion<br/>Supported values for workspace tasks (case-insensitive):<ul><li>`deploy` - workspace [deployment](deployments)</li></ul>

<Snippet path="pipelines/view-a-pipeline/response-body.md" />

### Properties

For each setting in the [datacomponents](datacomponents)' [dataplugin](dataplugins) [`settings`](dataplugins#setting) for each

Path | JSON Type | Format | Description
---- | --------- | ------ | -----------
`{datacomponent_name}.{setting_name}` | Refer to setting `kind` | Refer to setting `kind` | Refer to setting `description`

- Any required settings not satisfied by a [datacomponent](datacomponents) property must be provided as a pipeline property
- Any settings that are already satisfied by a [datacomponent](datacomponents) property can be overridden by a pipeline property

See [create or update a pipeline in a workspace request](#request-3) for a working example.

#### Reserved Properties for Extractor Datacomponents

Path | JSON Type | Format | Description
---- | --------- | ------ | -----------
`{datacomponent_name}._select` | `string` | JSON array | Meltano [stream and property selection rules](https://docs.meltano.com/concepts/plugins#select-extra)
`{datacomponent_name}._metadata` | `string` | JSON object | Meltano [stream and property metadata rules](https://docs.meltano.com/concepts/plugins#metadata-extra)

<Snippet path="jobs/configure-extractor-datacomponent-stream-selection-and-metadata-for-a-pipeline/request-body.md" />

## Formats

### Pipeline Status

Value | Description
----- | -----------
`READY` | The pipeline completed processing resource changes
`PROVISIONING` | The pipeline is processing resource changes
`FAILED` | The pipeline failed to process resource changes

---

## Requests

### View all pipelines in a workspace

:::info
**GET** `/api/workspaces/{workspace-id}/pipelines`
:::

Returns all configured pipelines in the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist

<Examples path="pipelines/view-all-pipelines-in-a-workspace" />

#### Response
`200 OK`

[Pipeline](#pipeline) collection with HAL links.
<Snippet path="pipelines/view-all-pipelines-in-a-workspace/response-body.md" />

---

### View a pipeline

:::info
**GET** `/api/pipelines/{pipeline-id}`
:::

Returns the pipeline `{pipeline-id}`.

#### Prerequisites
- Pipeline `{pipeline-id}` must exist

<Examples path="pipelines/view-a-pipeline" />

#### Response
`200 OK`

[Pipeline](#pipeline) with HAL links.
<Snippet path="pipelines/view-a-pipeline/response-body.md" />

---

### Initialise a pipeline in a workspace

:::info
**POST** `/api/workspaces/{workspace-id}/pipelines`
:::

Initialises a new pipeline in the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist

<Examples path="pipelines/initialise-a-pipeline-in-a-workspace" />

#### Response
`200 OK`

[Pipeline](#pipeline) with HAL links.
<Snippet path="pipelines/initialise-a-pipeline-in-a-workspace/response-body.md" />

---

### Create or update a pipeline in a workspace

:::info
**PUT** `/api/workspaces/{workspace-id}/pipelines/{pipeline-id}`
:::

Creates or updates the pipeline `{pipeline-id}` in the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist


#### Body
[Pipeline](#pipeline) resource.
<Snippet path="pipelines/create-a-pipeline-in-a-workspace/request-body.md" />


<Examples path="pipelines/create-a-pipeline-in-a-workspace" />

#### Response
`200 OK / 201 Created`

[Pipeline](#pipeline) with HAL links.
<Snippet path="pipelines/create-a-pipeline-in-a-workspace/response-body.md" />

---

### Create or update a pipeline as a draft

:::info
**PUT** `/api/workspaces/{workspace-id}/pipelines/{pipeline-id}/draft`
:::

Creates or updates the pipeline `{pipeline-id}` in the workspace `{workspace-id}` as a draft.

#### Prerequisites
- Workspace `{workspace-id}` must exist


#### Body
[Pipeline](#pipeline) resource.
<Snippet path="pipelines/create-a-pipeline-as-a-draft/request-body.md" />


<Examples path="pipelines/create-a-pipeline-as-a-draft" />

#### Response
`200 OK / 201 Created`

[Pipeline](#pipeline) with HAL links.
<Snippet path="pipelines/create-a-pipeline-as-a-draft/response-body.md" />

---

### Validate a pipeline configuration in a workspace

:::info
**POST** `/api/workspaces/{workspace-id}/pipelines/validation`
:::

Validates a pipeline configuration in the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist

#### Body

[Pipeline](#pipeline) resource.
<Snippet path="pipelines/validate-a-pipeline-configuration-in-a-workspace/request-body.md" />


<Examples path="pipelines/validate-a-pipeline-configuration-in-a-workspace" />

#### Response
`200 OK`

No response body provided.

`400 Bad Request`

[Pipeline property](pipelines#properties) validation errors.
<Snippet path="pipelines/validate-a-pipeline-configuration-in-a-workspace/response-body.md" />

---

### Verify a pipeline

:::info
**POST** `/api/pipelines/{pipeline-id}/verification`
:::

Verifies the configuration of the pipeline `{pipeline-id}`.

#### Prerequisites
- Pipeline `{pipeline-id}` must exist

<Examples path="pipelines/verify-a-pipeline" />

#### Response
`200 OK`

[Job](jobs#job) with HAL links.
<Snippet path="pipelines/verify-a-pipeline/response-body.md" />

---

### Delete a pipeline

:::info
**DELETE** `/api/pipelines/{pipeline-id}`
:::

Deletes the pipeline `{pipeline-id}`.

#### Prerequisites
- Pipeline `{pipeline-id}` must exist

<Examples path="pipelines/delete-a-pipeline" />

#### Response
`204 No Content`

No response body provided.

---

### View pipeline metrics

:::info
**GET** `/api/pipelines/{pipeline-id}/metrics`
:::

Returns the pipeline metrics for each job of `{pipeline-id}`.

#### Prerequisites
- Pipeline `{pipeline-id}` must exist

<Examples path="pipelines/view-the-pipeline-metrics-data" />

#### Response
- `200`: The dataset data (defaults to JSON format).

<Snippet path="pipelines/view-the-pipeline-metrics-data/response-body.md" />

- `204`: No response body, metrics not enabled.

---

##### See Also

- [View all running or completed jobs for a pipeline](jobs#view-all-running-or-completed-jobs-for-a-pipeline)
- [Create a job from a pipeline](jobs#create-a-job-from-a-pipeline)
- [Subscribe to a pipeline](subscriptions#subscribe-to-a-pipeline)
- [PipelineML](/reference/cloud/dataml/pipelineml/)
