---
title: Environment
description: Reference documentation for pipeline environment customisation.
sidebar_position: 1
---

Pipelines have environments that are used to pass configuration to the underlying plugins it references.

---

### Viewing your Environment

You can see what environment a pipeline is running with by navigating to it, clicking the expand arrow and choosing the Environment tab. This tab will show all setting being used for your data source, data store and any other plugins you are using.

Some of these setting will be hidden with the value `***`, but when you copy and paste your environment, which you can do just by clicking anywhere in the environment window, these values will be shown.

---

### Default Environment

Your pipeline's environment by default will contain:
- Configuration values for all dataplugin settings set on the pipeline or referenced datacomponents
- `EXTRACTOR`, if referencing a datacomponent backed by an extractor dataplugin
- `LOADER`, if referencing a datacomponent/datastore backed by a loader dataplugin
- `DBT_TARGET`, pertaining to a datasatore referenced by the pipeline, or the workspace default
- `DBT_SOURCE_SCHEMA`, pertaining to a datasatore referenced by the pipeline, or the workspace default
- `DBT_TARGET_SCHEMA`, pertaining to a datasatore referenced by the pipeline, or the workspace default
- `MELTANO_STATE_BACKEND_URI`
- `MELTANO_ENVIRONMENT`

  See [Configuring settings](/guide/configuration#configuring-settings) for more information on how Meltano handles plugin configuration from environment variables.

- `EXTRACTOR`, `LOADER`

  `name` of the extractor/loader dataplugin referenced by a pipeline datacomponent.

- `DBT_TARGET`

  `namespace` of the loader dataplugin referenced by a pipeline datastore datacomponent, or the workspace default datastore.

- `DBT_SOURCE_SCHEMA`, `DBT_TARGET_SCHEMA`

  Schema of the pipeline datastore datacomponent, or the workspace default datastore.

- [`MELTANO_STATE_BACKEND_URI`](/reference/settings#state_backenduri)

  Defines where state for the pipeline is stored. By default, this points at the Postgres database provisioned for the workspace (if no other supported datastore is referenced by the pipeline). State is generally stored in a `meltano` schema, unless otherwise specified.

- [`MELTANO_ENVIRONMENT`](/concepts/environments#activation)

  The active Meltano [environment](/concepts/environments), controlled by the workspace default environment.

---

### Editing Your Environment

You can add to or overwrite your environment variables by using a [custom data import script](custom-scripts). How to use and whats expected when you do use a custom data import script can also be found [here](custom-scripts).

In your custom data import script you can add new or overwrite existing environment variables with a single line:

```bash
export <NEW_OR_EXISTING_SETTING_NAME>=<NEW_VALUE>
```

---

## Further Reading

- [`MELTANO_STATE_BACKEND_URI](/reference/settings/#state_backenduri)
- [`MELTANO_ENVIRONMENT`](/concepts/environments/#activation)
