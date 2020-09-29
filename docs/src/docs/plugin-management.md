---
description: Learn how to manage your Meltano project's plugins.
---

# Plugin Management

A [Meltano project](/docs/project.html)'s primary components are its [plugins](/docs/plugins.html),
that implement the various details of your ELT pipelines.

Your project's plugins are defined in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file), and [installed](#installing-your-project-s-plugins) inside the [`.meltano` directory](/docs/project.html#meltano-directory).
They can be managed using various [CLI commands](/docs/command-line-interface.html) as well as the [UI](/docs/ui.html).

## Adding extractors and loaders to your project

Like all types of plugins, extractors and loaders can be added to a Meltano project using [`meltano add`](/docs/command-line-interface.html#add).

[Discoverable plugins](/docs/plugins.html#discoverable-plugins) can be added by simply specifying their `type` and `name`, while adding a plugin that Meltano isn't familiar with yet requires adding the `--custom` flag.

To find out what plugins are discoverable and supported out of the box, you can use [`meltano discover`](/docs/command-line-interface.html#discover), with an optional pluralized `<type>` argument, e.g. `meltano discover extractors`.
You can also check out the lists of supported [extractors](/plugins/extractors/) and [loaders](/plugins/loaders/) on this website.

If the Singer tap or target you'd like to use with Meltano doesn't show up in any of these places, you're going to want to [add a custom plugin](/docs/command-line-interface.html#how-to-use-custom-plugins).

```bash
# List discoverable extractors and loaders
meltano discover extractors
meltano discover loaders

# Add a discoverable extractor or loader by name
meltano add extractor tap-salesforce
meltano add loader target-snowflake

# Add a custom extractor or loader
meltano add --custom extractor tap-covid-19
```

## Installing your project's plugins

Whenever you add a new plugin to a Meltano project using [`meltano add`](/docs/command-line-interface.html#add),
it will be installed into your project's [`.meltano` directory](/docs/project.html#meltano-directory) automatically.

However, since this directory is included in your project's `.gitignore` file
by default, you'll need to explicitly run [`meltano install`](/docs/command-line-interface.html#install)
before any other `meltano` commands whenever you clone or pull an existing Meltano project from version control,
to install (or update) all plugins specified in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file).

## Meltano UI

While Meltano is optimized for usage through the [`meltano` CLI](/docs/command-line-interface.html)
and direct changes to the [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file),
basic plugin management functionality is also available in [the UI](/docs/ui.html#extractors).
