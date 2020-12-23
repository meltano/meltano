---
description: Learn how to manage and monitor your plugins and pipelines using Meltano UI
---

# Meltano UI

In line with [our current focus](/docs/#focus) on data engineers comfortable with CLIs and version control,
Meltano is optimized for usage through the [`meltano` CLI](/docs/command-line-interface.html)
and direct changes to the [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file).

However, a web-based UI is also available for when you want to quickly check the
status and most recent logs of your project's [scheduled pipelines](/orchestration.html),
or if you want to give less technical team members or clients the option to [configure](/docs/configuration.html) their
extractors, loaders, and pipelines themselves.

Various [settings](/docs/settings.html) are available that let you [configure the Meltano UI server](/docs/settings.html#meltano-ui-server), [enable and disable features](/docs/settings.html#meltano-ui-features), and [customize its appearance](/docs/settings.html#meltano-ui-customization).

## Current status

Basic functionality around [managing](/docs/plugin-management.html) and [configuring](/docs/configuring.html) [plugins](/docs/plugins.html) and monitoring [pipelines](/docs/orchestration.html) is available,
as is an experimental [Analysis](/docs/analysis.html) feature, but many (newer) features of the CLI do not yet have a UI equivalent.

Missing functionality and other improvements are being tracked in the ["Pipeline management and monitoring UI" epic](https://gitlab.com/groups/meltano/-/epics/78),
and [new issues and contributions](/docs/contributor-guide.html) from the community are more than welcome,
but the team is not currently [prioritizing](/docs/#roadmap) improvements to the UI because of the heavy focus on the CLI.

## Usage during development

Start the Meltano UI web server using [`meltano ui`](/docs/command-line-interface.html#ui):

```bash
meltano ui
```

Unless [configured otherwise](/docs/settings.html#ui-bind-port), the UI will now be available at <http://localhost:5000>.

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

Unless [configured otherwise](/docs/settings.html#ui-bind-port), the UI will now be available at <http://localhost:5000>.

For more details and instructions, refer to [README](https://gitlab.com/meltano/files-docker-compose/-/blob/master/bundle/README.md) contained in the file bundle.

## Deployment in production

To learn about deploying Meltano UI in production, refer to the ["Meltano UI" section](/docs/production.html#meltano-ui) of the [Deployment in Production guide](/docs/production.html).

## Screenshots

### Extractors

[![Extractors interface](/images/meltano-ui/extractors.png)](/images/meltano-ui/extractors.png)

### Extractor configuration

[![Extractor Configuration interface](/images/meltano-ui/extractor-configuration.png)](/images/meltano-ui/extractor-configuration.png)

### Loaders

[![Loaders interface](/images/meltano-ui/loaders.png)](/images/meltano-ui/loaders.png)

### Pipelines

[![Pipelines interface](/images/meltano-ui/pipelines.png)](/images/meltano-ui/pipelines.png)

### Pipeline creation

[![Pipeline Creation interface](/images/meltano-ui/pipeline-creation.png)](/images/meltano-ui/pipeline-creation.png)

### Pipeline run log

[![Extractors Run Log interface](/images/meltano-ui/pipeline-run-log.png)](/images/meltano-ui/pipeline-run-log.png)

### Explore and Dashboards

For more information on (and screenshots of) the Explore and Dashboard interfaces, refer to the [Data Analysis guide](/docs/analysis.html#explore-your-data).
