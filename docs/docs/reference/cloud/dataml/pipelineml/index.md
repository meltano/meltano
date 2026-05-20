---
title: PipelineML
description: Reference documentation for pipeline definition model.
sidebar_position: 5
---

import DocCardList from '@theme/DocCardList';

Use the pipeline YAML to orchestrate data actions in your workspace as code.

Pipeline definitions are stored as YAML file format, you can read more about the YAML format and its syntax [here](https://yaml.org/).

---

### Example: `pipelines/report_pipeline.yml`

```yaml
version: pipelines/v0.1
data_components:
- notebook
- sendgrid
actions:
- notebook:run-convert
- sendgrid:send
properties:
  notebook.path: notebook/data_quality_report.ipynb
timeout: 1500
max_retries: 3
schedule: 0 0 0 * * 0
triggered_by:
- other-pipeline
- deploy
```

### Key Information

Path | JSON Type | Description
---- | --------- | -----------
`version`         | `string`   | The version identifies this artifact type.
`data_components` | `string[]` | The meltano.yml data component name.
`actions`         | `string[]` | The Meltano tasks that will be run as defined in your meltano.yml or Plugins.
`inline_script`   | `string`   | Custom [Bash](https://www.gnu.org/software/bash/) script.  Overrides actions if supplied.
`timeout`         | `number`   | A timeout value in seconds that prevents pipelines from running for too long. A pipeline running longer that the timeout setting is automatically stopped.
`max_retries`      | `number`  | The maximum number of retries to attempt for a job ending with `ERROR`
`properties`      | `object`      | A map of properties, with Data Component name and setting as the key and the value e.g. `data-component-name.setting=value`, that configures the pipeline environment.
`schedule`        | `string`   | The automated schedule for this pipeline, in a standard cron format with seconds.  `0 0 9-17 * * MON-FRI` on the hour nine-to-five weekdays.
`triggered_by`    | `string[]` | Pipelines or workspace tasks that will trigger the pipeline on successful completion.<br/>Supported values for workspace tasks (case-insensitive):<ul><li>`deploy` - workspace [deployment](/reference/cloud/api/resources/deployments)</li></ul>

---

Further Reading:

- [Pipelines API resource](/reference/cloud/api/resources/pipelines)

---

<DocCardList />
