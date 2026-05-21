---
title: Jobs
description: Meltano Cloud jobs resource reference documentation
sidebar_position: 19
---

import Examples from '@site/src/components/Examples';
import Snippet from '@site/src/components/Snippet';

A job is an arbitrary task with some stored state, pertaining to the governing [workspace](workspaces). Typically, jobs are orchestrated by [pipeline](pipelines) operations, but can also represent tasks for the user to complete.

---

## Objects

### Job

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`id` | `string` | Version 4 UUID | The job ID
`created` | `string` | ISO 8601 timestamp | The instant at which the job was created
`type` | `string` | [Job Type](#job-type) | The descriptor for the process undertaken by the job
`exitCode` | `number` | Process exit status | The job exit code
`status` | `string` | [Job Status](#job-status) | The job status
`startTime` | `string` | ISO 8601 timestamp | The instant at which the job run started
`endTime` | `string` | ISO 8601 timestamp | The instant at which the job run ended

<Snippet path="jobs/view-a-job/response-body.md" />

## Formats

### Job Status

`string`

Value | Description
----- | -----------
`QUEUED` | The job is queued
`RUNNING` | The job is running
`COMPLETE` | The job finished with no errors
`ERROR` | The job finished with errors
`STOPPED` | The job timed out or was manually stopped

### Job Type

`string`

Value | Description
----- | -----------
`WORKSPACE_INIT` | A system task to create a Meltano project in a [workspace](workspaces) repository - automatically run when a workspace is created
`PIPELINE_CONFIG` | A system task to configure the Meltano project and publish [datasets](datasets) with reference to a [pipeline](pipelines) - automatically run when a pipeline is created, or a pipeline with a [`status`](pipelines#pipeline-status) of `FAILED` is updated
`PIPELINE_VERIFY` | A system task to display and test the configuration of a [pipeline](pipelines)
`PIPELINE_RUN` | A system task to run a [pipeline](pipelines) to load data into the [workspace](workspaces)  default [datastore](datastores), or some other destination external to the platform - manually run by the user or automatically run on the defined `schedule`
`PROFILE_COLLABORATE` | A user task to send an [invitation](invitations)
`PROFILE_IMPORT` | A user task to create a [pipeline](pipelines)

---

## Requests

### View all running or completed jobs for a workspace

:::info
**GET** `/api/workspaces/{workspace-id}/jobs`
:::

Returns all running or completed jobs for the workspace `{workspace-id}`.

#### Prerequisites
- Workspace `{workspace-id}` must exist

<Examples path="jobs/view-all-running-or-completed-jobs-for-a-workspace" />

#### Response
`200 OK`

[Job](#job) collection with HAL links.
<Snippet path="jobs/view-all-running-or-completed-jobs-for-a-workspace/response-body.md" />

---

### View all running or completed jobs for a pipeline

:::info
**GET** `/api/pipelines/{pipeline-id}/jobs`
:::

Returns all running or completed jobs for the pipeline `{pipeline-id}`.

#### Prerequisites
- Pipeline `{pipeline-id}` must exist

<Examples path="jobs/view-all-running-or-completed-jobs-for-a-pipeline" />

#### Response
`200 OK`

[Job](#job) collection with HAL links.
<Snippet path="jobs/view-all-running-or-completed-jobs-for-a-pipeline/response-body.md" />

---

### View a job

:::info
**GET** `/api/jobs/{job-id}`
:::

Returns the job `{job-id}`.

#### Prerequisites
- Job `{job-id}` must exist

<Examples path="jobs/view-a-job" />

#### Response
`200 OK`

[Job](#job) with HAL links.
<Snippet path="jobs/view-a-job/response-body.md" />

---

### View the logs of a job

:::info
**GET** `/api/jobs/{job-id}/logs?sequence={sequence}`
:::

Returns the logs of the job `{job-id}`.

#### Prerequisites
- Job `{job-id}` must exist

#### Query Parameters

Query Parameter | Format | Default Value | Description
--------------- | ------ | ------------- | -----------
`sequence` | Unsigned integer | `0` | The line number in the logs to read from

#### Headers
##### `Accept`

Media Type(s) | Description
------------- | -----------
`text/plain` `*/*` | Sets the response content type format to plain text
`application/stream+json` `application/x-ndjson` | Sets the response content type format to [NDJSON](http://ndjson.org/)


<Examples path="jobs/view-the-logs-of-a-job-as-json" />

#### Response
- `200`: The job logs in the format specified by associated request `Accept` header

<Snippet path="jobs/view-the-logs-of-a-job-as-json/response-body.md" />

- `204`: No response body provided.

---

### Create a job from a pipeline

:::info
**POST** `/api/pipelines/{pipeline-id}/jobs`
:::

Creates a new job from the pipeline `{pipeline-id}`.

#### Prerequisites
- Pipeline `{pipeline-id}` must exist and not already be running

<Examples path="jobs/create-a-job-from-a-pipeline" />

#### Response
`201 Created`

[Job](#job) with HAL links.
<Snippet path="jobs/create-a-job-from-a-pipeline/response-body.md" />

---

### Stop a job

:::info
**PUT** `/api/jobs/{job-id}/stopped`
:::

Stops the execution of the job `{job-id}`.

#### Prerequisites
- Job `{job-id}` must exist
- Job `{job-id}` must have [status](#job-status) `RUNNING`

<Examples path="jobs/stop-a-job" />

#### Response
`202 Accepted`

Job stop acceptance message.
<Snippet path="jobs/stop-a-job/response-body.md" />

---

### Delete a job

:::info
**DELETE** `/api/jobs/{job-id}`
:::

Deletes and stops the execution of the job `{job-id}`.

#### Prerequisites
- Job `{job-id}` must exist


<Examples path="jobs/delete-a-job" />

#### Response
`204 No Content`

No response body provided.

---
