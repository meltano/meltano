---
title: Custom Scripts
description: Reference documentation for pipeline custom scripts.
permalink: /dataml/pipelineml/custom-scripts
nav_order: 2
parent: PipelineML
grand_parent: DataML
---

# {{page.title}}

---

Custom scripts can be used in [Pipelines]({{site.baseurl}}/glossary#pipeline) by choosing `Script` from `Section 2 - Clean, transform and organise` when creating or editing your data import or by defining an 'inline_script' in your [Pipeline YAML]({{site.baseurl}}/dataml/pipelineml/).

---

## Basics

Custom scripts are bash scripts that generally invoke [Meltano](https://docs.meltano.com/guide/plugin-management){:target="_blank"} commands. As mentioned before you can also control the [data import's]({{site.baseurl}}/glossary#data-import) environment in these scripts.

When you provide a `Script` to a pipeline, we will still add your plugins properties to the pipeline environment. Other than that, you are now in complete control of the environment, installation of plugins and execution of your pipeline.

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

- [Matatika Examples of Custom Scripts](https://github.com/Matatika/matatika-examples/tree/master/example_data_import_scripts){:target="_blank"}
- [Matatika Default Pipeline Run Script](https://github.com/Matatika/matatika-examples/blob/master/example_data_import_scripts/default.sh)
- [Matatika Technical Glossary](https://github.com/Matatika/matatika-examples/tree/master/matatika_technical_glossary#custom-data-source){:target="_blank"}
- [Meltano Documentation](https://docs.meltano.com/guide/plugin-management){:target="_blank"}