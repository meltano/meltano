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
A non-default [variant](/docs/plugins.html#docs) can be selected using the `--variant` option.

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

# Add a specific variant of a discoverable extractor loader
meltano add extractor tap-salesforce --variant=singer-io
meltano add loader target-snowflake --variant=transferwise

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

## Removing plugins from your project

Since the [`plugins` section](/docs/project.html#plugins) of your [`meltano.yml` project file](/docs/project.html) determines the plugins that make up your project, you can remove a plugin from your project by deleting its entry from this file.

Traces of the plugin may remain in the [`.meltano` directory](/docs/project.html#meltano-directory) under `.meltano/<plugin type>/<plugin name>`, and in the `job` and `plugin_settings` tables in the [system database](/docs/project.html#system-database). You are free to delete these files and rows manually.

::: tip Contribution idea

Do you think there should be a `meltano remove <type> <name>` [CLI command](/docs/command-line-interface.html) to mirror [`meltano add <type> <name>`](/docs/command-line-interface.html#add)?

There's an [issue](https://gitlab.com/meltano/meltano/-/issues/2353) for that, and we'll gladly accept a [contribution](/docs/contributor-guide.html)!

:::

## Using a custom fork of a plugin

If you've forked a plugin's repository and made changes to it, you can update your Meltano project to use your custom fork instead of the canonical source:

1. Modify the plugin definition's `pip_url` in the [`plugins` section](/docs/project.html#plugins) of your [`meltano.yml` project file](/docs/project.html) to point at your fork using a [`git+http(s)` URL](https://pip.pypa.io/en/stable/reference/pip_install/#git), with an optional branch or tag name:

    ```yaml{5-6}
    plugins:
      extractors:
      - name: tap-gitlab
        variant: meltano
        pip_url: git+https://gitlab.com/meltano/tap-gitlab.git
        # pip_url: git+https://gitlab.com/meltano/tap-gitlab.git@ref-name
    ```

    If your plugin source is stored in a private repository, you have two options:

    - Continue to authenticate over HTTP(S), and store your credentials in a [`.netrc` file](https://ec.haxx.se/usingcurl/usingcurl-netrc#the-netrc-file-format) in your home directory:

      ```bash
      machine <hostname> # e.g. gitlab.com or github.com
      login <username>
      password <personal-access-token-or-password>
      ```

    - Authenticate using SSH instead, and specify a `git+ssh` URL:

      ```yaml
      pip_url: git+ssh://git@gitlab.com/meltano/tap-gitlab.git
      ```

1. Re-install the plugin from the new `pip_url` using [`meltano install`](/docs/command-line-interface.html#install):

    ```bash
    meltano install <type> <name>

    # For example:
    meltano install extractor tap-gitlab
    ```

If your fork supports additional settings, you can set them as [custom settings](/docs/configuration.html#custom-settings).

## Meltano UI

While Meltano is optimized for usage through the [`meltano` CLI](/docs/command-line-interface.html)
and direct changes to the [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file),
basic plugin management functionality is also available in [the UI](/docs/ui.html#extractors).
