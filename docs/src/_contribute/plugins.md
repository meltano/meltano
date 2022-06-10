---
title: Plugins
description: Meltano is open source software built by a growing team and a community of contributors.
layout: doc
weight: 10
---

## Discoverable plugins

[Discoverable plugins](/concepts/plugins#discoverable-plugins) that are supported out of the box are available in [Meltano Hub](https://hub.meltano.com).

### Making a custom plugin discoverable

If you've added a [custom plugin](/concepts/plugins#custom-plugins) (or [variant](/concepts/plugins#variants)) to your project that could be discoverable and supported out of the box for new users, please [contribute](https://github.com/meltano/hub/issues/new) its description to Meltano Hub to save the next user the hassle of setting up the custom plugin.
GitHub makes it easy to contribute changes without requiring you to leave your browser.

Discoverable plugin definitions in Meltano Hub have the a very similar format as [custom plugin definition](/concepts/project#custom-plugin-definitions) in your [`meltano.yml` project file](/concepts/project#meltano-yml-project-file), so a copy-paste is usually sufficient.
The format and further requirements are laid out in more detail below.

#### Plugin definitions

At a minimum, a plugin definition must have a `name` and a `namespace`, and at least one [variant definition](#variant-definitions) with a `pip_url` (its [`pip install`](https://pip.pypa.io/en/stable/reference/pip_install/#usage) argument).

It is recommended to add a `label`, `logo_url`, and `description` to the plugin definition, and `docs` and `repo` URLs to the variant definition(s).

Most of the time, variant definitions should also have a `settings` array with [setting definitions](#setting-definitions).

Additionally:

- `capabilities` should be specified for extractor variants,
- non-default variant executable names can be specified using `executable`, and
- default values for [plugin extras](/guide/configuration#plugin-extras) can be specified at the plugin definition level and further overridden at the variant definition level.

##### Variant definitions

If a plugin will only ever have a single [variant](/concepts/plugins#variants) (as is typically the case for all types except for extractors and loaders),
the variant definition can be embedded in the plugin definition (variant properties can be mixed in with plugin properties), and a variant name _should not_ be specified using a `variant` key.

If a plugin currently only has a single variant, but more might be added later (as is typically the case for extractors and loaders),
the variant definition can be embedded in the plugin definition, and a variant name _should_ be specified using the `variant` key, matching the organization name on GitHub/GitLab, e.g. `meltano`, `singer-io`, or `transferwise`.

If multiple variants of a plugin are available, the plugin definition should have a `variants` array where each entry represents a variant definition with its own `name`, again matching the organization name on GitHub/GitLab.
The first variant is considered the default, and the _original_ variant supported by Meltano should be marked with `original: true`.
Deprecated variants should be marked with `deprecated: true`.

##### Setting definitions

Each extractor (tap) and loader (target) variant in the `discovery.yml` has a `settings` property. Nested under this property are a variable amount of individual settings. In the Meltano UI these settings are parsed to generate a configuration form. To improve the UX of this form, each setting has a number of optional properties:

```yaml
- settings:
    - name: setting_name # Required (must match the connector setting name)
      aliases: [alternative_setting_name] # Optional (alternative names that can be used in `meltano.yml` and with `meltano config set`)
      label: Setting Name # Optional (human friendly text display of the setting name)
      value: "" # Optional (Use to set a default value)
      placeholder: Ex. format_like_this # Optional (Use to set the input's placeholder default)
      kind: string # Optional (Use for a first-class input control. Default is `string`, others are `integer`, `boolean`, `date_iso8601`, `password`, `options`, `file`, `array`, `object`, and `hidden`)
      description: Setting description # Optional (Use to provide inline context)
      tooltip: Here is some more info... # Optional (use to provide additional inline context)
      documentation: https://meltano.com/ # Optional (use to link to specific supplemental documentation)
      protected: true # Optional (use in combination with `value` to provide an uneditable default)
      env: SOME_API_KEY # Optional (use to delegate to an environment variable for overriding this setting's value)
      value_processor: nest_object # Optional (Modify value after loading it from source: env, meltano.yml, system database. Target type needs to match `kind`. Options: `nest_object`, `upcase_string`)
      value_post_processor: stringify # Optional (Modify loaded value before passing it to plugin. Target type does not need to match `kind`. Options: `stringify`)
```

###### Protected settings

Until role-based access control is implemented in Meltano, we need to prevent user editing of certain settings from the UI.

### Adopting a plugin

When the maintainer of the default [variant](/concepts/plugins#variants) of a discoverable plugin becomes unresponsive to issues and contributions filed by the community,
that plugin is considered up for adoption, which means that we are looking for a different variant of the plugin with a more engaged maintainer to become the new default.

This new variant can either be a fork of the original default variant, or an alternative implementation for the same source or destination, as long as it is actively maintained.

If you maintain or are aware of such a variant,
please add it to your Meltano project as a [custom plugin](/concepts/plugins#custom-plugins) and [make it discoverable](#making-a-custom-plugin-discoverable),
or [file an issue](https://github.com/meltano/meltano/issues/new) so that the Meltano core team can assist you.

As a plugin's primary maintainer, you do not have to spend a lot of time improving the plugin yourself.
In fact, attracting more users and getting the community involved is likely to recude your personal maintenance burden,
since you'll receive contributions with bug fixes and new features that you will only be expected to review, not build yourself.

### <a name="local-changes-to-discovery-yml"></a>Local changes to `discovery.yml`

When you need to make changes to `discovery.yml`, these changes are not automatically detected inside of the `meltano` repo during development. While there are a few ways to solve this problem, it is recommended to create a symbolic link in order ensure that changes made inside of the `meltano` repo appear inside the Meltano project you initialized and are testing on.

1. Get path for `discovery.yml` in the repo

- Example: `/Users/bencodezen/Projects/meltano/src/meltano/core/bundle/discovery.yml`

2. Open your Meltano project in your terminal

3. Create a symbolic link by running the following command:

```
ln -s $YOUR_DISCOVERY_YML_PATH
```

Now, when you run the `ls -l` command, you should see something like:

```
bencodezen  staff   72 Nov 19 09:19 discovery.yml -> /Users/bencodezen/Projects/meltano/src/meltano/core/bundle/discovery.yml
```

Now, you can see your changes in `discovery.yml` live in your project during development! 🎉

### `discovery.yml` version

Whenever new functionality is introduced that changes the schema of `discovery.yml` (the exact properties it supports and their types), the `version` in `src/meltano/core/bundle/discovery.yml` and the `VERSION` constant in `src/meltano/core/plugin_discovery_service.py` must be incremented, so that older instances of Meltano don't attempt to download and parse a `discovery.yml` its parser is not compatible with.

Changes to `discovery.yml` that only use existing properties do not constitute schema changes and do not require `version` to be incremented.

## Plugin Development

### <a name="taps-targets-development"></a>Taps & Targets Development

Watch ["How taps are built"](https://www.youtube.com/watch?v=aImidnW8nsU) for an explanation of how Singer taps (which form the basis for Meltano extractors) work, and what goes into building new ones or verifying and modifying existing ones for various types of APIs.

Then watch ["How transforms are built"](https://www.youtube.com/watch?v=QRaCSKQC_74) for an explanation of how DBT transforms work, and what goes into building new ones for new data sources.

#### For existing taps/targets

We should be good citizen about these, and use the default workflow to contribute. Most of these are on GitHub so:

1. Fork (using Meltano organization)
1. Add a [webhook](https://docs.gitlab.com/ee/ci/triggers/#triggering-a-pipeline-from-a-webhook) to trigger the `meltano/meltano` pipeline.
1. Modify and submits PRs
1. If there is resistance, fork as our tap (2)

##### How to test a tap?

We qualify taps with the capabilities it supports:

- properties: the tap uses the old `--properties` format for the catalog
- catalog: the tap uses the new `--catalog` format for the catalog
- discover: the tap supports catalog extraction
- state: the tap supports incremental extraction

###### Properties/Catalog

You should look at the tap's documentation to see which one is supported.

###### Discover

Try to run the tap with the `--discover` switch, which should output a catalog on STDOUT.

###### State

1. Try to run the tap connect and extract data first, watching for `STATE` messages.
1. Do two ELT run with `target-postgres`, then validate that:
   1. All the tables in the schema created have a PRIMARY KEY constraint. (this is important for incremental updates)
   1. There is no duplicates after multiple extractions

##### Troubleshooting

###### Tables are lacking primary keys

This might be a configuration issue with the catalog file that is sent to the tap. Take a look at the tap's documentation and look for custom metadata on the catalog.

#### For taps/targets we create

1. For tap development please use the [tap cookiecutter template](https://github.com/singer-io/singer-tap-template).
1. For target development please use the [target cookiecutter template](https://github.com/singer-io/singer-target-template).
1. Use a separate repo (meltano/target|tap-x) in GitHub
   e.g. Snowflake: https://gitlab.com/meltano/target-snowflake
1. Publish PyPI packages of these package (not for now)
1. We could mirror this repo on GitHub if we want (not for now)

### Transform & Models Development

When you need to expose data to the user through Meltano UI, this often will require updating the transforms and models. At a high level:

- **Transforms** will allow you to create the necessary PostgreSQL tables for users to query against
- **Models** will determine the structure of what is exposed on the UI side

#### Transforms

You can test local transforms in a project by adding them in a Meltano project's `transform` > `models` > `my_meltano_project` directory.

Every transform file is a SQL file that will determine how the table is created. Some caveats include:

- Rather than referring to the tables directly (i.e., `analytics.gitlab_issues`), the syntax uses `ref` to refer to tables
- When joining two tables together, `*` seems to crash dbt. Instead, you should explicitly define every column. For example:

```sql
users.user_id as user_id,
users.user_name as user_name,
issues.month_closed as month_closed,
issues.year_closed as year_closed,
```

Once you've created your transforms, you can run it with the following command:

```bash
# Replace your extractors / targets with the appropriate ones
meltano elt tap-gitlab target-postgres --transform only
```

### File Bundle Development

To create a file bundle plugin like <https://github.com/meltano/files-dbt>, follow these steps:

1. Create a new plugin repository named `files-<service/tool>` (e.g. `files-airflow` or `files-docker`).
1. Copy over `setup.py`, `README.md`, and `LICENSE` from <https://github.com/meltano/files-dbt> and edit these files as appropriate.
1. Create a `bundle` directory with an empty `__init__.py` file.
1. Add all desired directories and files to the `bundle` directory. All of these files will be copied over into the Meltano project directory when the file bundle is added to the project.
1. Add all file paths under `bundle` to the `package_data["bundle"]` array in `setup.py`
1. Push your new plugin repository to GitLab.com. Official file bundle plugins live at `https://github.com/meltano/files-...`.
1. Add an entry to `src/meltano/core/bundle/discovery.yml` under `files`. Set `name` and `pip_url` as appropriate, and if applicable, set `namespace` to the `namespace` of the plugin the file bundle is related to (e.g. `dbt`).
1. If any files are to be updated automatically when [`meltano upgrade`](/reference/command-line-interface#upgrade) is run, add an `update` object with `[file path]: True` entries for each file.
1. Success! You can now submit a pull request to Meltano containing the changes to `discovery.yml` (and an appropriate `CHANGELOG` item, of course).
