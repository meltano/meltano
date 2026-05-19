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
- `DBT_TARGET`, pertaining to a datasatore referenced by the pipeline, or the worksapce default
- `DBT_SOURCE_SCHEMA`, pertaining to a datasatore referenced by the pipeline, or the worksapce default
- `DBT_TARGET_SCHEMA`, pertaining to a datasatore referenced by the pipeline, or the worksapce default
- `MELTANO_STATE_BACKEND_URI`
- `MELTANO_ENVIRONMENT`

The `MELTANO_DATABASE_URI` is where your [workspaces's]() [Meltano project](https://github.com/Matatika/matatika-examples/tree/master/matatika_technical_glossary#meltano) job information is stored. Also stored in along with the Meltano job information is any saved state. Depending on if a data source supports it, the saved state can be used in the next run of the data source as a starting point of where to get data from. This can save a time by limiting the amount of data synced to only new data since the state checkpoint.

By default we set every data import's `MELTANO_DATABASE_URI` to be the `public` schema of your workspace's default managed data store. (A postgres database that we set up and provide with each workspace). For more information about `MELTANO_DATABASE_URI`s and State, see the links at the bottom of this page.

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