---
title: Advanced Topics
description: Learn about advanced topics in the Meltano.
layout: doc
sidebar_position: 10
---

## Installing Optional Components

Most of Meltano's features are available without installing any additional packages. However, some niche or environment-specific features require the installation of [Python extras](https://peps.python.org/pep-0508/#extras).

### System Database

The following extras add support for different [system database](/concepts/project/#system-database) types, which function as the default [state backend](/concepts/state_backends):

- `mssql` - Microsoft SQL Server.
- `psycopg2` - PostgreSQL. It uses the legacy `psycopg2` driver.
- `postgres` - PostgreSQL. It uses the modern `psycopg` driver.

### State backends

The following extras add support for other [state backends](/concepts/state_backends):

- `s3` - AWS S3.
- `gcs` - Google Cloud Storage.
- `azure` - Azure Blob Storage.

### Virtual Environment backends

The following extras add support for different [virtual environment backends](/concepts/python_virtual_environments#how-does-meltano-use-virtual-environments-internally):

- `uv` - Manage virtual environments with [astral.sh/uv](https://github.com/astral-sh/uv/).

:::info
  <p>
  After you switch to a different virtual environment backend, it's recommended to reinstall all plugins with `meltano install --clean`.
  </p>
:::

## Extension Developer Kit (EDK)

Meltano extensions are lightweight executables which allow you to integrate existing data tools with Meltano.
Extensions allow the developer to add additional features like pre/post-hooks to run before/after Meltano executes the application, as well enabling project scaffolding to be customized for each plugin. This project scaffolding was previously accomplished via files bundles.

The Meltano [Extension Developer Kit](https://github.com/meltano/edk) (EDK) was created to make it easier for developers to build Meltano extensions.
For more information on how to build your own EDK-based Meltano extension, see [the EDK docs](https://edk.meltano.com/en/latest/).

### Meltano Plugin Types

Meltano has traditionally assigned a plugin type to each plugin based on their functionality.
These plugin types were/are used in the Meltano codebase to activate plugin type specific features (i.e. piping Singer taps and targets together, running dbt deps before each run, or compiling and removing the Airflow config.cfg configuration file to avoid storing sensitive credentials).
This approach caused some challenges around getting new features implemented and accepted by the entire user base of Meltano because only one implementation was allowed:

- extractor (Singer Taps e.g. tap-github)
- loader (Singer Targets e.g. target-snowflake)
- transformer (dbt Adapters e.g. dbt-snowflake)
- utility (e.g. SqlFluff, Airflow, Dagster)

The new approach is to group all non-EL plugins under the `utility` plugin type, leaving only the following plugin types:

- extractor
- loader
- utility - now also including plugins previously called transformers and orchestrators

As part of this new approach the logic for non-EL plugin specific features has been extracted out of the Meltano codebase and into a Meltano extension.
This allows the community to iterate on plugin features more quickly without relying on merging features into the Meltano core repository.
It also allows the community to develop many variants of the wrapper logic for a plugin with different features.

The transformer and orchestrator plugin types are still supported for now but will eventually be phased out as utilities take over.

## Running Custom Scripts

In addition to the ability to build EDK based python utilities, Meltano also allows you to run arbitrary scripts as utilities.
This feature is usually helpful for user who need to do very minor tasks that don't require any additional dependencies.
It let you use Meltano in a very flexible manner to solve various use cases like set up or tear down tasks prior to running EL, interfacing with external services, etc.

To run a python script present at the root of your project, add a custom utility with a command that references the script as the executable:

```yaml
utilities:
- name: my_script_util
  namespace: my_script_util
  commands:
    run_script:
      executable: python
      args: my_script.py
    run_another_script:
      executable: python
      args: my_other_script.py
```

You add it to your meltano.yml as a utility then you can run it just like any other Meltano [plugin command](/concepts/project#plugin-commands).
Running the install command is not necessary for this utility.
See the examples below of running the sample commands:

```bash
meltano run my_script_util:run_script
meltano invoke my_script_util:run_another_script
```

Similarly this can be used to run bash scripts as well:

```yaml
utilities:
- name: my_script_util
  namespace: my_script_util
  commands:
    ls_directory:
      executable: /bin/bash
      args: -c ls
    remove_directory:
      executable: /bin/bash
      args: -c "rm -rf target"
```

## Airbyte Connector Integration FAQ

This FAQ section is for [tap-airbyte-wrapper](https://github.com/MeltanoLabs/tap-airbyte-wrapper) which is a Singer tap which enables any Airbyte source to be used as a Meltano extractor.

### How do the Singer and Airbyte specifications relate?

The Singer specification was started in 2016 by Stitch Data. It specified a data transfer format that would allow any number of data systems, called taps, to send data to any data destinations, called targets. Airbyte was incorporated in 2020 and created their own specification that was heavily inspired by Singer. There are differences, but the core of each specification is sending new-line delimited JSON data from STDOUT of a tap to STDIN of a target.

### How does the Airbyte Connector with Meltano integration work?

A community member used the Meltano Singer SDK to write tap-airbyte-wrapper. This wrapper connector calls the Docker image for a given Airbyte Source and translates the messages into a Singer-compatible format. The output of the tap is conformed to the Singer standard and then can be sent to any Singer target, many of which are listed on [MeltanoHub](https://hub.meltano.com/loaders/).

### How do I get help if I need it?

We first recommend you read through this FAQ to see if your question has been answered. We next recommend searching the [Meltano docs](https://docs.meltano.com) to see if your answer is there.

If you still need help we’d recommend either filing an issue in the [Meltano Github repository](https://github.com/meltano/meltano/issues) or join our [Slack community](https://meltano.com/slack) to ask there.

We also have [weekly Office Hours](https://www.addevent.com/calendar/Li390615) where you can talk to the Meltano team and ask any questions you have to us!

### Do I need to have an Airbyte UI or API instance to use this?

No. This integration makes it possible to directly run Airbyte [Source Connectors](https://docs.airbyte.com/category/sources) within your Meltano project. There's no need to run the Airbyte UI or API to use this feature.

### Does this support Airbyte destination connectors as well?

Airbyte destinations are _not_ supported with tap-airbyte-wrapper. This is a feature that could be added in the future.

### What is the recommended way to install and use these connectors?

Any connector that is listed on MeltanoHub as being maintained by `airbyte` can be installed and run as you would any other connector. Use `meltano add extractor <tap>` to add and install.

### What are the limitations of running Airbyte-based connectors with Meltano?

Based on the current implementation and testing, the main challenge is putting these connectors into production with Meltano. See the next question for more details on this.

### Am I able to put my Meltano project with Airbyte connectors in production?

The short answer is: It depends where its deployed!

The main potential challenge with putting this into production is if you use Docker to package and deploy your Meltano project. If you're able to set up Docker-in-docker, then a Dockerized Meltano project with tap-airbyte-wrapper will work as expected. Since each Airbyte connector is itself a Docker image, running inside a dockerized Meltano project would require “docker in docker” which has some possible challenges around privileges and permissions on certain systems.

For example, AWS ECS does not support docker in docker and Meltano Cloud does not currently have plans to support container based connectors at this time either. Although a simple EC2 instance with Docker available would work as expected.

Within [Github Codespaces](https://github.com/features/codespaces), adding support for docker-in-docker was as easy as [adding a few lines](https://github.com/meltano/meltano-codespace-ready/commit/5ffb9fb6e3232142c8e2307340c0a4fb66379db4) to the devcontainer.json file.

It is also possible to run [Meltano on GitHub Actions](https://github.com/brooklyn-data/meltano-on-github-actions). It’s likely possible to update this action to supporting docker-in-docker as well.

There are several articles on the web which discuss docker-in-docker in more detail:

- [Run dind without privileged access](https://zhsj.me/blog/view/dind-without-privileged)
- [How to Run Docker in Docker](https://shisho.dev/blog/posts/docker-in-docker/)
- [Run the Docker daemon as a non-root user](https://docs.docker.com/engine/security/rootless/)

We are interested in exploring this challenge with the community. Please share in [this discussion](https://github.com/meltano/meltano/discussions/7142) or connect with us in [Slack](https://meltano.com/slack) about your experiences with attempting to put this into production.

### How does this work with custom connectors made with the Airbyte CDK?

This integration will work with any dockerized Airbyte source, whether it was made with their CDK or not.

To configure your Airbyte connector as a [custom plugin](https://docs.meltano.com/concepts/project#custom-plugin-definitions) in Meltano you can copy the configuration shown below into your meltano.yml file then replace `name`, and the `value` for the airbyte_spec.image to reference your docker image. You can configure your connector without defining all of the settings and their metadata.

```yaml
 - name: tap-pokeapi # REPLACE THIS WITH YOUR CONNECTOR NAME
   variant: airbyte
   executable: tap-airbyte
   namespace: tap_airbyte
   pip_url: git+https://github.com/MeltanoLabs/tap-airbyte.git
   capabilities:
   - catalog
   - state
   - discover
   - about
   - stream-maps
   - schema-flattening
   settings:
   - description: Airbyte image to run
     kind: string
     label: Airbyte Spec Image
     name: airbyte_spec.image
     value: airbyte/source-pokeapi # REPLACE THIS WITH YOUR IMAGE NAME
   - description: Airbyte image tag
     kind: string
     label: Airbyte Spec Tag
     name: airbyte_spec.tag
     value: latest
   - [INSERT OTHER SETTINGS HERE]
```

### What features does this add to Airbyte connectors?

Running Airbyte sources with Meltano brings a number of benefits to those connectors. With Meltano you get the ability to run stream maps to adjust data on the fly, you can define multiple environments to override configuration depending on where the EL pipeline is run, and you get the benefits of version control since everything is defined in your meltano.yml file.

We also recently added support for alternative [state backends](https://docs.meltano.com/concepts/state_backends) to Meltano. This means if you want to store the incremental state between runs in a place other than your system database or local filesystem, you can! Currently Meltano supports AWS S3, Azure Blob Storage, and Google Cloud Storage as alternative state backends.

Since tap-airbyte-wrapper was written with the SDK, this also unlocks the `BATCH` message format which can help with overall pipeline throughput to compatible targets.

### Do I need to do anything different with state?

Nope! Meltano manages state for you and you can use any command you normally would with Singer-based connectors.

### I have an Airbyte pipeline already running, how can I transfer it to Meltano?

Transferring a pipeline to Meltano would require determining your strategy for handling incremental state and overall table structure.

Because with Meltano you would be using a different loader (aka destination or target) than you would in your Airbyte pipeline, it’s likely that the table structure that would appear in your destination would be different. Due to this difference, we have two recommendations for migrating a pipeline.

The first may be possible only if your data source allows you to quickly backfill data. You can do a full sync with your Meltano pipeline to get all of the data into the new format and then switch any downstream process to point at this new table. However, for many sources this may not be possible.

Another option would be to stop your Airbyte pipeline and have the Meltano pipeline start at that point. For example, if the Airbyte pipeline stops on 2022-12-31 you could have the Meltano pipeline start at 2023-01-01 and write to a different table. You could then use a tool like dbt to transform both tables into a common format and then union them together into a single source.

There are tradeoffs for both of these methods and you would have to determine where to best invest your time depending on your needs.

If you have other ways to make this transition easier, we’d love to discuss them in Slack or Office Hours with you!

### Do these connectors work with `meltano run` and `meltano elt`?

Yes! Since the wrapper is based on the Meltano Singer SDK these connectors work just as they would a python-based Singer connector. You can [run](https://docs.meltano.com/reference/command-line-interface#run), [elt](https://docs.meltano.com/reference/command-line-interface#elt), [invoke](https://docs.meltano.com/reference/command-line-interface#invoke), [test](https://docs.meltano.com/reference/command-line-interface#test), and [configure](https://docs.meltano.com/reference/command-line-interface#config) them as you normally would.

### Does this integration support stream maps for PII filtering/hashing?

Yes! This is a unique feature of Meltano that is not found in a comprehensive manner in other modern EL tools. With stream maps users are able to hash, filter, duplicate, and alias any column or table during their extract. Because this Airbyte integration was built using the SDK, streams maps can be defined on the connector itself ([SDK docs](https://sdk.meltano.com/en/latest/stream_maps.html)), or they can be added separately as a mapper in between a tap and target executing using `meltano run`. See [our tutorial](https://docs.meltano.com/getting-started/part4#undefined) for an example.

### Does this work with interactive config?

Yes! For each connector added to the Hub we have mapped the configuration output from the connector to our metadata spec on MeltanoHub. This means interactive configuration will work normally. Note that there was a [bug with nested config](https://github.com/meltano/meltano/issues/7132) which was addressed in release [2.13.0](https://github.com/meltano/meltano/releases/tag/v2.13.0), which could affect your configuration behavior.

### How do I know if a bug is related to the wrapper or the Airbyte connector?

Errors from the Airbyte connector are output via [LOG](https://docs.airbyte.com/understanding-airbyte/airbyte-protocol#airbytelogmessage) and [TRACE](https://docs.airbyte.com/understanding-airbyte/airbyte-protocol#airbytetracemessage) messages. If a container has a non-zero exit code then the wrapper will output on stderr along with the failing Airbyte command. Errors from the wrapper are unlikely but if there are any then they will not have the preceding characteristics.

### What do I do if I find a bug or want to request a new feature for an Airbyte connector?

Submit a bug report in the [airbytehq/airbyte repo](https://github.com/airbytehq/airbyte/issues).

### How do I access local files from my Airbyte connector?

Airbyte connectors are run inside Docker containers, this means they don’t automatically have access to your local file system. To access local files you can use the `docker_mount` setting. An example of using Airbyte’s tap-file to access a CSV file in a “data” directory within my local meltano project would look like this:

```yaml
   config:
     docker_mounts: [{"source": "/<YOUR_FULL_LOCAL_PATH>/", "target": "/local/", "type": "bind"}]
     airbyte_spec:
       image: airbyte/source-file
     airbyte_config:
       dataset_name: test_file
       format: csv
       url: /local/data/test.csv
```

### What is the performance like compared to raw Airbyte sources?

Based on some testing the original community contributor did, we see a less than 5% drop in overall throughput for the same source run natively via Docker versus via Meltano. For most sources this is an acceptable change for the workflow gains from running these connectors in a tool that supports truly custom and decentralized sources and enables the software engineering best practices of version control, isolated run environments, and continuous integration.

### Is this an experimental feature?

After seeing these plugins in the wild for several weeks, hundreds of successful invocations from users in the community, and successful production use cases (e.g. [Harness](https://www.harness.io/)) we're comfortable taking these plugins out of the experimental phase.

We hope the community continue to test these out and push the integration further.
Please open any issues or features requests related to the wrapper on [MeltanoLabs/tap-airbyte-wrapper](https://github.com/MeltanoLabs/tap-airbyte-wrapper).

### Will this be able to run on Meltano Cloud?

We don't currently have plans for supporting Airbyte, or other container based connectors, in Meltano Cloud.

If this is something you’re interested in, please reach out to us via the [Meltano Cloud Waitlist](https://meltano.com/cloud/) or on [Slack](https://meltano.com/slack).
