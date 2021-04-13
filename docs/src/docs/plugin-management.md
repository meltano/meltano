---
description: Learn how to manage your Meltano project's plugins.
---

# Plugin Management

Meltano takes a modular approach to data engineering in general and EL(T) in particular,
where your [project](/docs/project.html) and pipelines are composed of [plugins](/docs/plugins.html) of [different types](#types), most notably
[**extractors**](#extractors) ([Singer](https://singer.io) taps),
[**loaders**](#loaders) ([Singer](https://singer.io) targets),
[**transformers**](#transformers) ([dbt](https://www.getdbt.com) and [dbt models](https://docs.getdbt.com/docs/building-a-dbt-project/building-models)), and
[**orchestrators**](#orchestrators) (currently [Airflow](https://airflow.apache.org/), with [Dagster](https://dagster.io/) [in development](https://gitlab.com/meltano/meltano/-/issues/2393)).

Your project's plugins are defined in your [`meltano.yml` project file](/docs/plugins.html),
and are [installed](#installing-your-project-s-plugins) inside the [`.meltano` directory](/docs/project-structure.html#meltano-directory).
They can be managed using various [CLI commands](/docs/command-line-interface.html) as well as the [UI](/docs/ui.html).

## Adding a plugin to your project

You can add a new [plugin](/docs/plugin-structure.html#project-plugins) to your project using [`meltano add`](/docs/command-line-interface.html#add), or
by directly modifying your [`meltano.yml` project file](/docs/plugins.html)
and [installing the new plugin](#installing-your-projects-plugins) using [`meltano install`](/docs/command-line-interface.html#install).

If you'd like to add a [discoverable plugin](/docs/plugin-structure.html#discoverable-plugins) that's supported by Meltano out of the box,
like one of the extractors and loaders listed on the [Sources](/plugins/extractors/) and [Destinations](/plugins/loaders/) pages,
refer to the ["Discoverable plugins" section](#discoverable-plugins) below.

Alternatively, if you'd like to add a [custom plugin](/docs/plugin-structure.html#custom-plugins) that Meltano isn't familiar with yet,
like an arbitrary Singer tap or target, refer to the ["Custom plugins" section](#custom-plugins).

Finally, if you'd like your new plugin to [inherit from an existing plugin](/docs/plugin-structure.html#plugin-inheritance) in your project,
so that it can reuse the same package but override (parts of) its configuration,
refer to the ["Plugin inheritance" section](#plugin-inheritance).

### Discoverable plugins

[Discoverable plugins](/docs/plugin-structure.html#discoverable-plugins) can be added to your project by simply providing
[`meltano add`](/docs/command-line-interface.html#add) with their [type](/docs/plugin-structure.html#types) and name:

```bash
meltano add <type> <name>

# For example:
meltano add extractor tap-gitlab
meltano add loader target-postgres
meltano add transformer dbt
meltano add orchestrator airflow
```

This will add a [shadowing plugin definition](/docs/plugin-structure.html#shadowing-plugin-definitions) to your [`meltano.yml` project file](/docs/plugins.html) under the `plugins` property, inside an array named after the plugin type:

```yml{3-5,7-9,11-12,14-15}
plugins:
  extractors:
  - name: tap-gitlab
    variant: meltano
    pip_url: git+https://gitlab.com/meltano/tap-gitlab.git
  loaders:
  - name: target-postgres
    variant: datamill-co
    pip_url: singer-target-postgres
  transformer:
  - name: dbt
    pip_url: dbt
  orchestrators:
  - name: airflow
    pip_url: apache-airflow
```

If multiple [variants](/docs/plugin-structure.html#variants) of the discoverable plugin are available,
the `variant` property is automatically set to the name of the default variant
(which is known to work well and recommended for new users),
so that your project is pinned to a specific package and its [base plugin description](/docs/plugin-structure.html#project-plugins).
If the `variant` property were omitted from the definition, Meltano would fall back on the _original_ supported variant instead, which does not necessarily match the default.

The package's `pip_url` (its [`pip install`](https://pip.pypa.io/en/stable/reference/pip_install/#usage) argument)
is repeated here for convenience, since you may want to update it to
[point at a (custom) fork](#using-a-custom-fork-of-a-plugin) or to [pin a package to a specific version](#pinning-a-plugin-to-a-specific-version).
If this property is omitted, it is inherited from the discoverable [base plugin description](/docs/plugin-structure.html#project-plugins) identified by the `name` (and `variant`) instead.

As mentioned above, directly adding a plugin to your [`meltano.yml` project file](/docs/plugins.html)
and [installing it](#installing-your-projects-plugins) using [`meltano install <type> <name>`](/docs/command-line-interface.html#install)
has the same effect as adding it using [`meltano add`](/docs/command-line-interface.html#add).

#### Variants

If multiple [variants](/docs/plugin-structure.html#variants) of a discoverable plugin are available,
you can choose a specific (non-default) variant using the `--variant` option on [`meltano add`](/docs/command-line-interface.html#add):

```bash
meltano add <type> <name> --variant <variant>

# For example:
meltano add loader target-postgres --variant=transferwise
```

As you might expect, this will be reflected in the `variant` and `pip_url` properties in your [`meltano.yml` project file](/docs/plugins.html):

```yml{4-5}
plugins:
  loaders:
  - name: target-postgres
    variant: transferwise
    pip_url: pipelinewise-target-postgres
```

If you'd like to use multiple variants of the same discoverable plugin in your project at the same time, refer to ["Multiple variants" under "Explicit inheritance"](#multiple-variants) below.

If you've already added one variant to your project and would like to switch to another, refer to the ["Switching from one variant to another" section](#switching-from-one-variant-to-another) below.

#### Explicit inheritance

In the examples we've considered so far, plugins in your project implicitly inherit their
[base plugin descriptions](/docs/plugin-structure.html#project-plugins) from discoverable plugins by reusing their names, which is known as [shadowing](/docs/plugin-structure.html#shadowing-plugin-definitions).

Alternatively, if you'd like to give the plugin a more descriptive name in your project,
you can use the `--inherit-from` (or `--as`) option on [`meltano add`](/docs/command-line-interface.html#add)
to explicitly inherit from the discoverable plugin instead:

```bash
meltano add <type> <name> --inherit-from <discoverable-name>
# Or equivalently:
meltano add <type> <discoverable-name> --as <name>

# For example:
meltano add extractor tap-postgres--billing --inherit-from tap-postgres
meltano add extractor tap-postgres --as tap-postgres--billing
```

The corresponding [inheriting plugin definition](/docs/plugin-structure.html#inheriting-plugin-definitions) in your [`meltano.yml` project file](/docs/plugins.html) will use `inherit_from`:

```yml{4}
plugins:
  extractors:
  - name: tap-postgres--billing
    inherit_from: tap-postgres
    variant: transferwise
    pip_url: pipelinewise-tap-postgres
```

Note that the `variant` and `pip_url` properties were populated automatically by `meltano add` as described above.

##### Multiple variants

If you'd like to use multiple [variants](#variants) of the same discoverable plugin in your project at the same time, this feature will also come in handy.

Since plugins in your project need to have unique names, a discoverable plugin can only be shadowed once,
but it can be inherited from multiple times, with each plugin free to choose its own variant:

```bash
meltano add loader target-snowflake --variant=transferwise --as target-snowflake--transferwise
meltano add loader target-snowflake --variant=meltano --as target-snowflake--meltano
```

Assuming a regular (shadowing) `target-snowflake` was added before using `meltano add loader target-snowflake`,
the resulting [inheriting plugin definitions](/docs/plugin-structure.html#inheriting-plugin-definitions) in [`meltano.yml` project file](/docs/plugins.html) will look as follows:

```yml{6-8,10-12}
plugins:
  loaders:
  - name: target-snowflake
    variant: datamill-co
    pip_url: target-snowflake
  - name: target-snowflake--transferwise
    inherit_from: target-snowflake
    variant: transferwise
    pip_url: pipelinewise-target-snowflake
  - name: target-snowflake--meltano
    inherit_from: target-snowflake
    variant: meltano
    pip_url: git+https://gitlab.com/meltano/target-snowflake.git
```

Note that the `--variant` option and `variant` property are crucial here:
since `inherit_from` can also be used to [inherit from another plugin in the project](#plugin-inheritance),
`inherit_from: target-snowflake` by itself would have resulted in the new plugin inheriting from the existing `target-snowflake` plugin (that uses the `datamill-co` variant) instead of the discoverable plugin we're looking for.

Had there been no `target-snowflake` plugin in the project yet,
`inherit_from: target-snowflake` would necessarily refer to the discoverable plugin,
but without a `variant` the _original_ variant would have been used rather than the default or a specific chosen one,
just like when shadowing with a `name` but no `variant`.

### Custom plugins

[Custom plugins](/docs/plugin-structure.html#custom-plugins) for packages that aren't [discoverable](#discoverable-plugins) yet,
like arbitrary Singer taps and targets,
can be added to your project using the `--custom` option on [`meltano add`](/docs/command-line-interface.html#add):

```bash
meltano add --custom <type> <name>

# For example:
meltano add --custom extractor tap-covid-19
meltano add --custom loader target-bigquery--custom

# If you're using Docker, don't forget to mount the project directory,
# and ensure that interactive mode is enabled so that Meltano can ask you
# additional questions about the plugin and get your answers over STDIN:
docker run --interactive -v $(pwd):/project -w /project meltano/meltano add --custom extractor tap-covid-19
```

Since Meltano doesn't have the [base plugin description](/docs/plugin-structure.html#project-plugins) for the package in question yet,
`meltano add --custom` will ask you to find and provide this metadata yourself:
(Note that more context is provided in the actual command prompts.)

```bash{6,10,12,14,17,20,23}
$ meltano add --custom extractor tap-covid-19
# Specify namespace, which will serve as the:
# - identifier to find related/compatible plugins
# - default database schema (`load_schema` extra)
#   for use by loaders that support a target schema
(namespace): tap_covid_19

# Specify `pip install` argument, for example:
# - PyPI package name:
(pip_url): tap-covid-19
# - Git repository URL:
(pip_url): git+https://github.com/singer-io/tap-covid-19.git
# - local directory, in editable/development mode:
(pip_url): -e extract/tap-covid-19

# Specify the package's executable name
(executable): tap-covid-19

# Specify supported Singer features (executable flags)
(capabilities): catalog,discover,state

# Specify supported settings (`config.json` keys)
(settings): api_token,user_agent,start_date
```

If you're adding a Singer tap or target that's listed on Singer's [index of taps](https://www.singer.io/#taps) or [targets](https://www.singer.io/#targets),
simply providing the package name as `pip_url` and `executable` usually suffices.
The plugin's `name` also typically matches the name of the package, but you are free to change it to be more descriptive.

If it's a tap or target you have developed or are developing yourself,
you'll want to set `pip_url` to either a [Git repository URL](https://pip.pypa.io/en/stable/reference/pip_install/#git) or local directory path.
If you add the `-e` flag ahead of the local path, the package will be installed in [editable mode](https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs).

To find out what `settings` a tap or target supports, reference the README in the repository and/or documentation.
If the `capabilities` a tap supports (executable flags like `--discover` and `--state`) are not described there,
you can try [one of these tricks](/docs/contributor-guide.html#how-to-test-a-tap) or refer directly to the source code.

This will add a [custom plugin definition](/docs/plugin-structure.html#custom-plugin-definitions) to your [`meltano.yml` project file](/docs/plugins.html) under the `plugins` property, inside an array named after the plugin type:

```yml{3-14}
plugins:
  extractors:
  - name: tap-covid-19
    namespace: tap_covid_19
    pip_url: tap-covid-19
    executable: tap-covid-19
    capabilities:
    - catalog
    - discover
    - state
    settings:
    - name: api_token
    - name: user_agent
    - name: start_date
```

The `pip_url`, `executable`, `capabilities`, and `settings` properties
constitute the plugin's [base plugin description](/docs/plugin-structure.html#project-plugins):
everything Meltano needs to know in order to be able to use the package as a plugin.

::: tip
Once you've got the plugin working in your project, please consider
[contributing its description](/docs/contributor-guide.html#discoverable-plugins)
to the [`discovery.yml` manifest](https://gitlab.com/meltano/meltano/-/blob/master/src/meltano/core/bundle/discovery.yml)
to make it discoverable and supported out of the box for new users!
:::

### Plugin inheritance

To add a new plugin to your project that [inherits from an existing plugin](/docs/plugin-structure.html#plugin-inheritance),
so that it can reuse the same package but override (parts of) its configuration,
you can use the `--inherit-from` option on [`meltano add`](/docs/command-line-interface.html#add):

```bash
meltano add <type> <name> --inherit-from <existing-name>

# For example:
meltano add extractor tap-ga--client-foo --inherit-from tap-google-analytics
meltano add extractor tap-ga--client-bar --inherit-from tap-google-analytics
meltano add extractor tap-ga--client-foo--project-baz --inherit-from tap-ga--client-foo
```

The corresponding [inheriting plugin definitions](/docs/plugin-structure.html#inheriting-plugin-definitions) in your [`meltano.yml` project file](/docs/plugins.html) will use `inherit_from`:

```yml{6-11}
plugins:
  extractors:
  - name: tap-google-analytics
    variant: meltano
    pip_url: git+https://gitlab.com/meltano/tap-google-analytics.git
  - name: tap-ga--client-foo
    inherit_from: tap-google-analytics
  - name: tap-ga--client-bar
    inherit_from: tap-google-analytics
  - name: tap-ga--client-foo--project-baz
    inherit_from: tap-ga--client-foo
```

Note that the `--inherit-from` option and `inherit_from` property can also be used to
[explicitly inherit from a discoverable plugin](#explicit-inheritance).

## Installing your project's plugins

Whenever you add a new plugin to a Meltano project using [`meltano add`](/docs/command-line-interface.html#add),
it will be installed into your project's [`.meltano` directory](/docs/project-structure.html#meltano-directory) automatically.

However, since this directory is included in your project's `.gitignore` file
by default, you'll need to explicitly run [`meltano install`](/docs/command-line-interface.html#install)
before any other `meltano` commands whenever you clone or pull an existing Meltano project from version control,
to install (or update) all plugins specified in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file).

To (re)install a specific plugin in your project, use [`meltano install <type> <name>`](/docs/command-line-interface.html#install), e.g. `meltano install extractor tap-gitlab`.

## Pinning a plugin to a specific version

When you [add a plugin to your project](#adding-a-plugin-to-your-project), the plugin definition's `pip_url` property
(the package's [`pip install`](https://pip.pypa.io/en/stable/reference/pip_install/#usage) argument)
in your [`meltano.yml` project file](/docs/plugins.html)
typically points at a [PyPI](https://pypi.org/) package or Git repository without specifying a specific version,
to ensure that you always get the latest and (presumably) greatest.

This makes sense when a plugin is installed for the first time, but can lead to unwelcome surprises down the line,
as your pipeline may break when a new version of the package is released that introduces a bug or changes its behavior in a backward-incompatible or otherwise undesireable way.

To ensure that [`meltano install`](/docs/command-line-interface.html#install) always installs the same version that was used when you originally got the pipeline working,
you can modify the plugin definition in your [`meltano.yml` project file](/docs/plugins.html) to include a version identifier in the `pip_url`.

The exact steps to determine the version and modify the `pip_url` will depend on whether you are installing a package from [PyPI](https://pypi.org/) or a Git repository:

### PyPI package

If the plugin's `pip_url` is set to a package name, e.g. `tap-shopify`, [`pip install`](https://pip.pypa.io/en/stable/reference/pip_install/#usage) will look for a package by that name on [PyPI](https://pypi.org/).

To pin the latest version:

1. Determine the latest version of the package by browsing to `https://pypi.org/project/<package>`, e.g. <https://pypi.org/project/tap-shopify>.

    At the time of writing, the latest version of `tap-shopify` is `1.2.6`.

1. Add an `==<version>` or `~=<version>` [version specifier](https://pip.pypa.io/en/stable/reference/pip_install/#requirement-specifiers) to the `pip_url`:

    ```yaml{5,8}
    # Before:
    pip_url: tap-shopify

    # After:
    pip_url: tap-shopify==1.2.6 # Always install version 1.2.6

    # Alternatively:
    pip_url: tap-shopify~=1.2.6 # Install 1.2.6 or a newer version in the 1.2.x range
    ```

### Git repository

If the plugin's `pip_url` is set to a `git+http(s)` URL, e.g. `git+https://gitlab.com/meltano/tap-gitlab.git` or `git+https://github.com/adswerve/target-bigquery.git`, [`pip install`](https://pip.pypa.io/en/stable/reference/pip_install/#usage) will look for a package in that repository.

To pin the latest version:

1. Determine the latest version of the package by browsing to the `https://` part of the repository URL, e.g. <https://gitlab.com/meltano/tap-gitlab> or <https://github.com/adswerve/target-bigquery>, and finding the latest Git tag.

    At the time of writing, the [latest tag](https://gitlab.com/meltano/tap-gitlab/-/tags) of <https://gitlab.com/meltano/tap-gitlab> is `v0.9.11`,
    and the [latest tag](https://github.com/adswerve/target-bigquery/tags) of <https://github.com/adswerve/target-bigquery> is`v0.10.2`.

    If no tags are available, you can also use the SHA of the latest commit, e.g.
    [`2657b89e8896face4ce320a03b8413bbc196cec9`](https://gitlab.com/meltano/tap-gitlab/-/commit/2657b89e8896face4ce320a03b8413bbc196cec9) or
    [`3df97b951b7eebdfa331a1ff570f1fe3487d632f`](https://github.com/adswerve/target-bigquery/commit/3df97b951b7eebdfa331a1ff570f1fe3487d632f).

1. Add an `@<tag>` or `@<sha>` [Git ref specifier](https://pip.pypa.io/en/stable/reference/pip_install/#git) to the `pip_url`:

    ```yaml{6-7,10-11}
    # Before:
    pip_url: git+https://gitlab.com/meltano/tap-gitlab.git
    pip_url: git+https://github.com/adswerve/target-bigquery.git

    # After:
    pip_url: git+https://gitlab.com/meltano/tap-gitlab.git@v0.9.11
    pip_url: git+https://github.com/adswerve/target-bigquery.git@v0.10.2

    # Alternatively:
    pip_url: git+https://gitlab.com/meltano/tap-gitlab.git@2657b89e8896face4ce320a03b8413bbc196cec9
    pip_url: git+https://github.com/adswerve/target-bigquery.git@3df97b951b7eebdfa331a1ff570f1fe3487d632f
    ```

## Installing plugins from a custom Python Package Index (PyPi)

If you need to fetch packages from a custom Python Package Index (PyPi), you can set the `PIP_INDEX_URL` environment variable to your custom URL before running `meltano install`.

In a `Dockerfile`, this would look like:

```dockerfile
ARG PIP_INDEX_URL=<your_custom_pypi_url>
RUN meltano install
```

## Removing a plugin from your project

Since the [`plugins` section](/docs/plugins.html) of your [`meltano.yml` project file](/docs/project.html) determines the plugins that make up your project, you can remove a plugin from your project by deleting its entry from this file.

Traces of the plugin may remain in the [`.meltano` directory](/docs/project-structure.html#meltano-directory) under `.meltano/<plugin type>/<plugin name>`, and in the `job` and `plugin_settings` tables in the [system database](/docs/project-structure.html#system-database). You are free to delete these files and rows manually.

::: tip Contribution idea

Do you think there should be a `meltano remove <type> <name>` [CLI command](/docs/command-line-interface.html) to mirror [`meltano add <type> <name>`](/docs/command-line-interface.html#add)?

There's an [issue](https://gitlab.com/meltano/meltano/-/issues/2353) for that, and we'll gladly accept a [contribution](/docs/contributor-guide.html)!

:::

## Using a custom fork of a plugin

If you've forked a plugin's repository and made changes to it, you can update your Meltano project to use your custom fork instead of the canonical source:

1. Modify the plugin definition's `pip_url` in the [`plugins` section](/docs/plugins.html) of your [`meltano.yml` project file](/docs/project.html) to point at your fork using a [`git+http(s)` URL](https://pip.pypa.io/en/stable/reference/pip_install/#git), with an optional branch or tag name:

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

1. Reinstall the plugin from the new `pip_url` using [`meltano install`](/docs/command-line-interface.html#install):

    ```bash
    meltano install <type> <name>

    # For example:
    meltano install extractor tap-gitlab
    ```

If your fork supports additional settings, you can set them as [custom settings](/docs/configuration.html#custom-settings).

## Switching from one variant to another

The default [variant](/docs/plugin-structure.html#variants) of a [discoverable plugin](/docs/plugin-structure.html#discoverable-plugins)
is recommended for new users, but may not always be a perfect fit for your use case.

If you've already added one variant to your project and would like to use another instead,
you can [add the new variant as a separate plugin](#multiple-variants) or switch your existing plugin over to the new variant:

1. Modify the plugin definition's `variant` and `pip_url` properties in the [`plugins` section](/docs/plugins.html) of your [`meltano.yml` project file](/docs/project.html):

    ```yml{12-13}
    # Before:
    plugins:
      loaders:
      - name: target-postgres
        variant: datamill-co
        pip_url: singer-target-postgres

    # After:
    plugins:
      loaders:
      - name: target-postgres
        variant: meltano
        pip_url: git+https://github.com/meltano/target-postgres.git # Optional
    ```

    If you don't know the new variant's `pip_url` (its [`pip install`](https://pip.pypa.io/en/stable/reference/pip_install/#usage) argument),
    you can remove this property entirely so that Meltano will fall back on the default.

1. Reinstall the plugin from the new `pip_url` using [`meltano install`](/docs/command-line-interface.html#install):

    ```bash
    meltano install <type> <name>

    # For example:
    meltano install loader target-postgres
    ```

1. View the current configuration using [`meltano config <name> list`](/docs/command-line-interface.html#config) to see if it is still valid:

    ```bash
    meltano config <name> list

    # For example:
    meltano config target-postgres list
    ```

    Because different variants often use different setting names,
    you will likely see some of the settings used by the old variant show up as
    [custom settings](/docs/configuration.html#custom-settings),
    indicating that they are not supported by the new variant,
    while settings that the new variant expects show up with a `None` or default value.

1. Assuming at least one setting did not carry over correctly from the old variant to the new variant,
    modify the plugin's configuration in your [`meltano.yml` project file](/docs/plugin-structure.html#plugin-configuration) to use the new setting names:

    ```yml{10-13}
    # Before:
    config:
      postgres_host: postgres.example.com
      postgres_port: 5432
      postgres_username: my_user
      postgres_database: my_database

    # After:
    config:
      host: postgres.example.com
      port: 5432
      user: my_user
      dbname: my_database
    ```

    If any of the old settings are stored in [places other than `meltano.yml`](/docs/configuration.html#configuration-layers),
    like a sensitive setting that may be stored in your project's [`.env` file](/docs/project-structure.html#env),
    you can unset the old setting and set the new one using [`meltano config`](/docs/command-line-interface.html#config):

    ```bash
    meltano config <name> unset <old_setting>
    meltano config <name> set <setting> <value>

    # For example:
    meltano config target-postgres unset postgres_password
    meltano config target-postgres set password my_password
    ```

    Keep doing this until `meltano config <name> list` shows a valid configuration for the new variant,
    without any of the old variant's settings remaining as [custom settings](/docs/configuration.html#custom-settings).

## Meltano UI

While Meltano is optimized for usage through the [`meltano` CLI](/docs/command-line-interface.html)
and direct changes to the [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file),
basic plugin management functionality is also available in [the UI](/docs/ui.html#extractors).
