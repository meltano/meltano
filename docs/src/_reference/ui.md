---
title: Meltano UI
description: Learn how to manage and monitor your plugins and pipelines using Meltano UI
layout: doc
---

Meltano is optimized for usage through the [`meltano` CLI](/reference/command-line-interface)
and direct changes to the [`meltano.yml` project file](/reference/project#meltano-yml-project-file).

However, a web-based UI is also available for when you want to quickly check the
status and most recent logs of your project's [scheduled pipelines](/tutorials/orchestration),
or if you want to give less technical team members or clients the option to [configure](/reference/configuration) their
extractors, loaders, and pipelines themselves.

Various [settings](/reference/settings) are available that let you [configure the Meltano UI server](/reference/settings#meltano-ui-server), [enable and disable features](/reference/settings#meltano-ui-features), and [customize its appearance](/reference/settings#meltano-ui-customization).

## Current status

Basic functionality around [managing](/reference/plugin-management) and [configuring](/reference/configuration) [plugins](/reference/plugins) and monitoring [pipelines](/tutorials/orchestration) is available,
as is an experimental [Analysis](/tutorials/analysis) feature, but many (newer) features of the CLI do not yet have a UI equivalent.

Missing functionality and other improvements are being tracked in the ["Pipeline management and monitoring UI" epic](https://gitlab.com/groups/meltano/-/epics/78),
and [new issues and contributions](/getting-started/contributor-guide) from the community are more than welcome,
but the team is not currently [prioritizing](https://handbook.meltano.com/product/roadmap) improvements to the UI because of the heavy focus on the CLI.

## Usage during development

Start the Meltano UI web server using [`meltano ui`](/reference/command-line-interface#ui):

```bash
meltano ui
```

Unless [configured otherwise](/reference/settings#ui-bind-port), the UI will now be available at <http://localhost:5000>.

### Docker Compose

If you'd like to use [Docker Compose](https://docs.docker.com/compose/) to manage the Meltano UI application lifecycle,
you can add the appropriate `docker-compose.yml` file to your project by adding the
[`docker-compose` file bundle](https://gitlab.com/meltano/files-docker-compose):

```bash
# For these examples to work, ensure that
# Docker Compose has been installed
docker-compose --version

# Add Docker Compose files to your project
meltano add files docker-compose

# Start the `meltano-ui` service in the background
docker-compose up -d
```

Unless [configured otherwise](/reference/settings#ui-bind-port), the UI will now be available at <http://localhost:5000>.

For more details and instructions, refer to [README](https://gitlab.com/meltano/files-docker-compose/-/blob/master/bundle/README.md) contained in the file bundle.

## Deployment in production

To learn about deploying Meltano UI in production, refer to the ["Meltano UI" section](/getting-started/production#meltano-ui) of the [Deployment in Production guide](/getting-started/production).

## Screenshots

### Extractors

[![Extractors interface](images/ui/extractors.png)](images/ui/extractors.png)

### Extractor configuration

[![Extractor Configuration interface](images/ui/extractor-configuration.png)](images/ui/extractor-configuration.png)

### Loaders

[![Loaders interface](images/ui/loaders.png)](images/ui/loaders.png)

### Pipelines

[![Pipelines interface](images/ui/pipelines.png)](images/ui/pipelines.png)

### Pipeline creation

[![Pipeline Creation interface](images/ui/pipeline-creation.png)](images/ui/pipeline-creation.png)

### Pipeline run log

[![Extractors Run Log interface](images/ui/pipeline-run-log.png)](images/ui/pipeline-run-log.png)

### Explore and Dashboards

For more information on (and screenshots of) the Explore and Dashboard interfaces, refer to the [Data Analysis guide](/tutorials/analysis#explore-your-data).
