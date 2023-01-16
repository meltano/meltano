---
title: Advanced Topics
description: Learn about advanced topics in the Meltano.
layout: doc
weight: 10
---

## Installing Optional Components

Most of Meltano's features are available without installing any additional packages. However, some niche or environment-specific features require the installation of [Python extras](https://peps.python.org/pep-0508/#extras). The following extras are currently supported:

* `mssql` - Support for Microsoft SQL Server
* `s3` - Support for using S3 as a [state backend](/concepts/state_backends)
* `gcs` - Support for using Google Cloud Storage as a [state backend](/concepts/state_backends)
* `azure` - Support for using Azure Blob Storage as a [state backend](/concepts/state_backends)

## Airbyte Connector Integration FAQ

This FAQ section is for [tap-airbyte-wrapper](https://github.com/MeltanoLabs/tap-airbyte-wrapper) which is a Singer tap which enables any Airbyte source to be used as a Meltano extractor.

### How do the Singer and Airbyte specifications relate?

The Singer specification was started in 2016 by Stitch Data. It specified a data transfer format that would allow any number of data systems, called taps, to send data to any data destinations, called targets. Airbyte was incorporated in 2020 and created their own specification that was heavily inspired by Singer. There are differences, but the core of each specification is sending new-line delimited JSON data from STDOUT of a tap to STDIN of a target.

### How does the Airbyte Connector with Meltano integration work?

A community member used the Meltano Singer SDK to write tap-airbyte-wrapper. This wrapper connector calls the Docker image for a given Airbyte Source and translates the messages into a Singer-compatible format. The output of the tap is conformed to the Singer standard and then can be sent to any Singer target, many of which are listed on [MeltanoHub](hub.meltano.com/loaders/).

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

Yes you can!

The main potential challenge with putting this into production is if you user Docker to package and deploy your Meltano project. If you're able to set up Docker-in-docker, then a Dockerized Meltano project with tap-airbyte-wrapper will work. Since each Airbyte connector is itself a Docker image, running inside a dockerized Meltano project would require “docker in docker” which has some possible challenges around privileges and permissions on certain systems.

Within Codespaces, adding support for docker-in-docker was as easy as [adding a few lines](https://github.com/meltano/meltano-codespace-ready/commit/5ffb9fb6e3232142c8e2307340c0a4fb66379db4) to the devcontainer.json file.

It is also possible to run [Meltano on GitHub Actions](https://github.com/brooklyn-data/meltano-on-github-actions). It’s likely possible to update this action to supporting docker-in-docker as well.

There are several articles on the web which discuss docker-in-docker in more detail:

* [Run dind without privileged access](https://zhsj.me/blog/view/dind-without-privileged)
* [How to Run Docker in Docker](https://shisho.dev/blog/posts/docker-in-docker/)
* [Run the Docker daemon as a non-root user](https://docs.docker.com/engine/security/rootless/)

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

Yes! For each connector added to the Hub we have mapped the configuration output from the connector to our metadata spec on MeltanoHub. This means interactive configuration will work normally. Note that there is currently a [bug with nested config](https://github.com/meltano/meltano/issues/7132) which we are actively addressing. Until this is resolved we don’t recommend using interactive config for Airbyte connectors. However, updating each setting individually works as expected.

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

### When will this not be an experimental feature?

This is currently an experimental feature from Meltano’s perspective. For us to feel comfortable recommending this for long term use we’d like to see a few key milestones.

We want this to be out in the wild for several weeks with hundreds of successful invocations from our community happening. We hope the community will kick the tires on this and help improve it in the coming weeks.

We’d also like to see more examples from folks who are deploying this in the wild. There are likely some corner cases that we may have not yet uncovered and we’d like help from the community to find them. That said, this integration is running in production at Harness, which is a positive early signal for us.

### Will this be able to run on Meltano Cloud?

We’re actively exploring this as an option. If this is something you’re interested in, please reach out to us via the [Meltano Cloud Waitlist](https://meltano.com/cloud/) or on [Slack](https://meltano.com/slack).
