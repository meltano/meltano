---
title: Custom Scripts
description: Reference documentation for pipeline custom scripts.
sidebar_position: 2
---

Custom scripts can be used in pipelines by choosing "Custom Bash Script" from the "Actions" tab when editing your pipeline in Meltano Cloud, or by defining an `script` in your [pipeline YAML file](.).

---

## Basics

Custom scripts are Bash scripts that generally invoke Meltano commands. As mentioned before you can also control the pipeline environment in these scripts.

When you provide a script to a pipeline, we will still add your plugins properties to the pipeline environment. Other than that, you are now in complete control of the environment, installation of plugins and execution of your pipeline.

---

## Recommendations

### Minimal Script

Generally at a minimum you will need to:

```bash
MELTANO_ENVIRONMENT=<env_name>
meltano environment add <env_name>

export MELTANO_ENVIRONMENT

meltano install
meltano run <tap_name> <target_name>
```

Adding a Meltano environment will allow your tap to save a state for next time it runs, if your tap supports this.

Running `meltano install` will install all plugins in your workspace. You can run `meltano install <plugin_type> <plugin_name>` to install specific ones if you wish.

`meltano run <tap_name> <target_name>` is the actual command to run the data import and get your data into your data store.

### Using Meltano To Invoke Other Plugins

```bash
meltano invoke dbt deps
meltano invoke dbt run
```

By invoking other plugins through Meltano, you gain the benefit of Meltano taking base level environment variables and passing them these plugins to use. This isn't perfect in every case, but generally will get you around setting a lot of environment variables manually.

## Further Reading

- [Examples of custom scripts](https://github.com/Matatika/matatika-examples/tree/master/example_data_import_scripts)
- [Default pipeline run script](https://github.com/Matatika/matatika-examples/blob/master/example_data_import_scripts/default.sh)
- [Technical glossary](https://github.com/Matatika/matatika-examples/tree/master/matatika_technical_glossary#custom-data-source)