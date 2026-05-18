---
title: Pipelines
description: Matatika Pipelines resource reference documentation
permalink: /api/resources/pipelines
parent: Resources
grand_parent: API
nav_order: 13
components: request-md-components/pipelines
---

# {{page.title}}

A pipeline defines a set of runnable actions composed from [datacomponents](datacomponents) to complete a set of tasks - for example, [ELT](https://en.wikipedia.org/wiki/Extract,_load,_transform){:target="_blank"}. Pipelines are run as [jobs](jobs), either manually or on a predetermined schedule. Only a single pipeline can be run at any given time.
{: .fs-5 }

---

## Objects
{: .no_toc }

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
`properties` | `object` | [`Properties`](#properties) | The pipeline properties, defined by the [dataplugin](dataplugins) [`settings`](dataplugins#setting) of each [datacomponent](datacomponents)<br>Properties are key-value pairs, where keys reference setting `name`s qualified by datacomponent `name`s
`dataComponents` | `string[]` | Array of [datacomponent](datacomponents) `name`s | The pipeline [datacomponent](datacomponents) `name`s or create / update with [dataplugin](dataplugins#dataplugin) `fullyQualifiedName`
`actions` | `string[]` | Array of [datacomponent](datacomponents) `name`s or commands | The pipeline actions to run during a [job](jobs)
`triggeredBy` | `string[]` | Array of [pipeline](pipelines) `name`s or workspace task identifiers | Pipelines or workspace tasks that will trigger the pipeline on successful completion<br>Supported values for workspace tasks (case-insensitive):{::nomarkdown}<ul><li>{:/nomarkdown}`deploy` - workspace [deployment](deployments){::nomarkdown}</li></ul>{:/nomarkdown}

{% include snippets/api/pipelines/view-a-pipeline/response-body.md %}

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

{% include snippets/api/jobs/configure-extractor-datacomponent-stream-selection-and-metadata-for-a-pipeline/request-body.md %}

## Formats
{: .no_toc}

### Pipeline Status
{: .d-inline-block }

Value | Description
----- | -----------
`READY` | The pipeline completed processing resource changes
`PROVISIONING` | The pipeline is processing resource changes
`FAILED` | The pipeline failed to process resource changes

---

#### Requests

- TOC
{: toc }

#### See Also

- [View all running or completed jobs for a pipeline](jobs#view-all-running-or-completed-jobs-for-a-pipeline)
- [Create a job from a pipeline](jobs#create-a-job-from-a-pipeline)
- [Subscribe to a pipeline](subscriptions#subscribe-to-a-pipeline)

---

{% include {{page.components}}/view-all-pipelines-in-a-workspace.md %}
{% include {{page.components}}/view-a-pipeline.md %}
{% include {{page.components}}/initialise-a-pipeline-in-a-workspace.md %}
{% include {{page.components}}/create-or-update-a-pipeline-in-a-workspace.md %}
{% include {{page.components}}/create-or-update-a-pipeline-as-a-draft.md %}
{% include {{page.components}}/validate-a-pipeline-configuration-in-a-workspace.md %}
{% include {{page.components}}/verify-a-pipeline.md %}
{% include {{page.components}}/delete-a-pipeline.md %}
{% include {{page.components}}/view-the-pipeline-metrics-data.md %}
