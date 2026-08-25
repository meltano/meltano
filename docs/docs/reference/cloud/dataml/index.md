---
title: DataML
description: Examples and reference documentation for **Data Management Language** **(DataML)**
sidebar_position: 2
---

import DocCardList from '@theme/DocCardList';

Examples and reference documentation for **Data Management Language** **(DataML)** artifacts.

<DocCardList />

## Deploy WorkspaceML
[WorkspaceML](/reference/cloud/dataml/workspaceml) configures the workspace you deploy to, rather than a resource within it. A deploy *merges* `workspace.yml` into the existing workspace: the provided properties are updated and those omitted are left unchanged - nothing resets to a default. The workspace name is set from the `name` property. `app_properties` are recomputed from the file, so removed keys are dropped.

## Deploy workspace artifacts
Every other DataML artifact backs a corresponding [resource](/reference/cloud/api/resources) that is created, updated or deleted by [deploying a workspace](/reference/cloud/api/resources/deployments).

A [create](#create), [update](#update) or [delete](#delete) operates on the resource that the artifact is matched to by `name` (`alias` for a dataset) unique within the workspace. This identifier is derived from the artifact filepath, minus the extension (pipeline names are additionally slugified).

### Create
When an artifact does not yet match a resource, deploying the workspace creates the corresponding resource from the artifact.

### Update
When an artifact matches a resource, deploying the workspace updates the corresponding resource from the artifact.

In general, a property is applied as a *replacement*: a value you provide overwrites the existing one, and a property you omit resets to its default (`null` or empty collection).

For example, given the following existing [pipeline resource](/reference/cloud/api/resources/pipelines#pipeline)
```json
{
    "dataComponents": ["tap-github", "target-snowflake"],
    "script": "echo 'Hello world!'",
    "timeout": 3600
}
```

backed by the following [PipelineML](/reference/cloud/dataml/pipelineml) artifact

```yml
data_components:
- tap-github
- target-snowflake
timeout: 3600
```

when deploying the workspace, the `script` is unset and the pipeline assumes default behaviour at runtime:
```json
{
    "dataComponents": ["tap-github", "target-snowflake"],
    "timeout": 3600
}
```

A property holding a schemaless object, such as pipeline `properties`, is instead applied as a *merge*: because the object can hold any number of keys, the artifact updates only those provided and leaves the rest unchanged.

For example, given the following existing pipeline resource
```json
{
    "properties": {
        "username": "example_user",
        "password": "***",
        "start_date": "2026-01-01"
    }
}
```

backed by the following PipelineML artifact

```yml
properties:
  username: another_example_user
  start_date: 2026-01-01
```

when deploying the workspace, only the provided keys of `properties` are updated:
```json
{
    "properties": {
        "username": "another_example_user",
        "password": "***",
        "start_date": "2026-01-01"
    }
}
```

An explicit `null` mapping can also be used to unset a key within a schemaless object:

```yml
properties:
  username: another_example_user
  start_date: null
```

```json
{
    "properties": {
        "username": "another_example_user",
        "password": "***"
    }
}
```

### Delete
When an artifact that previously matched a resource has its filepath modified or is deleted, deploying the workspace deletes the corresponding resource. Modifying the filepath will also [create](#create) a new resource under the new identifier.
