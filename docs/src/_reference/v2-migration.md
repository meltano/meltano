---
title: Meltano 2.0 Migration Guide
description: Migrate existing "v1" projects to the latest version of Meltano
layout: doc
redirect_from:
  - /guide/ui/
weight: 10
---

## Full list of migration tasks and breaking changes

The following list includes all breaking changes in Meltano version 2.0 as well as other recommended migration tasks.

1. **Removed: `model` plugin type**
   - This plugin type provided very basic BI capabilities using Meltano UI. This functionality has been removed in favor of 3rd party open source BI solutions.
1. **Removed: `dashboard` plugin type**
   - This plugin type provided very basic BI capabilities using Meltano UI. This functionality has been removed in favor of 3rd party open source BI solutions.
1. **Removed: `env_aliases` in plugin config**
1. **Removed: transforms support in `meltano elt`**
   - Meltano 2.0 continues to support extract-load (EL) operations with `meltano elt`. However, for EL+T operations which also need to transform data, please use `meltano run`.
1. **Removed: transforms support in Meltano schedules**
   - Meltano 2.0 continues to support extract-load (EL) operations in schedules. However, for EL+T operations which also need to transform data, please use the new `meltano job add` command to create a job definition and then specify the new job name in your schedule.
1. **Recommended: migrating to an adapter-specific dbt plugin
   - We recommend re-adding an adapter-specific version of dbt for existing projects which may be using the legacy `dbt` plugin name.
