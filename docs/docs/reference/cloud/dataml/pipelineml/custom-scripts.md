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

The following runs an extract-load to sync data from `<tap>` to `<target>`. For a pipeline with datacomponents referencing this tap and target only, this script identical to what is run by default.

```bash
meltano run --state-id-suffix $PIPELINE_ID <tap> <target>
```

`--state-id-suffix $PIPELINE_ID` ensures state is unique to the pipeline for the given tap/target combination.


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
