---
description: Meltano is open source software built by an internal team at GitLab as well as the larger Meltano community.
---

# Contributor Guide

Meltano is built for and by its community, and we welcome your contributions to our [GitLab repository](https://gitlab.com/meltano/meltano),
which houses Meltano's
[core](https://gitlab.com/meltano/meltano/-/tree/master/src/meltano/core),
[CLI](https://gitlab.com/meltano/meltano/-/tree/master/src/meltano/cli),
[UI](https://gitlab.com/meltano/meltano/-/tree/master/src/webapp),
[UI API](https://gitlab.com/meltano/meltano/-/tree/master/src/meltano/api),
[these docs](https://gitlab.com/meltano/meltano/-/tree/master/docs/src), and
the [index of discoverable plugins](#discoverable-plugins),
which feeds the lists of [Sources](/plugins/extractors/) and [Destinations](/plugins/loaders/) that are supported out of the box.

## Where to start?

If you'd like to contribute, but you're not sure _what_, check out the list of open issues labeled [Accepting Merge Requests].
Any other improvements are welcome too, of course, so simply asking yourself "What about Meltano didn't work quite as smoothly as I would've liked?" is another good way to come up with ideas.

If an issue for your problem or suggested improvement doesn't exist yet on our [issue tracker](https://gitlab.com/meltano/meltano/-/issues),
please [file a new one](https://gitlab.com/meltano/meltano/-/issues/new) before submitting a [merge request](#merge-requests),
so that the team and community are aware of your plan and can help you figure out the best way to realize it.

### Metrics (anonymous usage data) tracking

As you contribute to Meltano, you may want to disable [metrics tracking](/docs/settings.html#send-anonymous-usage-stats) globally rather than by project. You can do this by setting the environment variable `MELTANO_DISABLE_TRACKING` to `True`:

```bash
# Add to `~/.bashrc`, `~/.zshrc`, etc, depending on the shell you use:
export MELTANO_DISABLE_TRACKING=True
```

## Prerequisites

In order to contribute to Meltano, you will need the following:

1. [Python 3.6.1+](https://www.python.org/downloads/). For more details about Python requirements, refer to the ["Requirements" section](/docs/installation.html#requirements) of the Installation instructions, that also apply here.
2. [Node 8.11.0+](https://nodejs.org/)
3. [Yarn](https://yarnpkg.com/)

## Setting Up Your Environment

```bash
# Clone the Meltano repo
git clone git@gitlab.com:meltano/meltano.git

# Change directory into the Meltano project
cd meltano

# Install the Poetry tool for managing dependencies and packaging
pip3 install poetry

# Install all the dependencies
poetry install

# Install the pre-commit hook
poetry run pre-commit install --install-hooks

# Bundle the Meltano UI into the `meltano` package
make bundle
```

Meltano is now installed and available at `meltano`, as long as you remain in your `meltano-development` virtual environment!

This means that you're ready to start Meltano CLI development. For API and UI development, read on.

## API Development

This section of the guide provides guidance on how to work with the Meltano API, which serves as the backend of Meltano and is built with the [Python framework: Flask](https://github.com/pallets/flask).

### Getting Setup

After all of your dependencies installed, we recommend opening a new window/tab in your terminal so you can run the following commands:

```bash
# Create a new Meltano project
meltano init $PROJECT_NAME

# Change directory into your newly created project
cd $PROJECT_NAME

# Start a development build of the Meltano API and a production build of Meltano UI
FLASK_ENV=development meltano ui
```

The development build of the Meltano API and a production build of the UI will now be available at <http://localhost:5000/>.

::: tip

To debug your Python code, here is the recommended way to validate / debug your code:

```python
# Purpose: Start a debugger
# Usage: Use as a one-line import / invocation for easier cleanup
import pdb; pdb.set_trace()
```

:::

## UI Development

In the event you are contributing to Meltano UI and want to work with all of the frontend tooling (i.e., hot module reloading, etc.), you will need to run the following commands:

```bash
# Create a new Meltano project
meltano init $PROJECT_NAME

# Change directory into your newly created project
cd $PROJECT_NAME

# Start the Meltano API and a production build of Meltano UI that you can ignore
meltano ui

# Open a new terminal tab and go to the directory you cloned meltano into
cd $WHEREVER_YOU_CLONED_MELTANO

# Install frontend infrastructure at the root directory
yarn setup

# Start local development environment
yarn serve
```

The development build of the Meltano UI will now be available at <http://localhost:8080/>.

A production build of the API will be available at <http://localhost:5000/> to support the UI, but you will not need to interact with this directly.

::: tip

If you're developing for the _Embed_ app (embeddable `iframe` for reports) you can toggle `MELTANO_EMBED`:

```bash
# Develop for the embed app
export MELTANO_EMBED=1

# Develop for the main app (this is the default)
export MELTANO_EMBED=0

# Start local development environment
yarn serve
```

:::

If you need to change the URL of your development environment, you can do this by updating your project's `.env` file with the following configuration:

```bash
# The URL where the web app will be located when working locally in development
# since it provides the redirect after authentication.
# Not require for production
export MELTANO_UI_URL = ""
```

## Discoverable plugins

[Discoverable plugins](/docs/plugins.html#discoverable-plugins) that are supported out of the box are defined in the `discovery.yml` manifest,
which can be found inside the Meltano repository at
[`src/meltano/core/bundle/discovery.yml`](https://gitlab.com/meltano/meltano/-/blob/master/src/meltano/core/bundle/discovery.yml).

### Making a custom plugin discoverable

If you've added a [custom plugin](/docs/plugins.html#custom-plugins) (or [variant](/docs/plugins.html#variants)) to your project that could be discoverable and supported out of the box for new users, please contribute its description to this file to save the next user the hassle of setting up the custom plugin.
The [GitLab Web IDE](https://docs.gitlab.com/ee/user/project/web_ide/) makes it very easy to contribute changes without requiring you to leave your browser.

Discoverable plugin definitions in `discovery.yml` have the same format as [custom plugin definition](/docs/project.html#custom-plugin-definitions) in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file), so a copy-paste is usually sufficient.
The format and further requirements are laid out in more detail below.

Besides the new definition in `discovery.yml`, a new discoverable plugin should be documented in the
[Sources](/plugins/extractors/) or [Destinations](/plugins/loaders/) section of this website,
which live inside the repository under
[`docs/src/plugins/extractors`](https://gitlab.com/meltano/meltano/-/tree/master/docs/src/plugins/extractors) and
[`docs/src/plugins/loaders`](https://gitlab.com/meltano/meltano/-/tree/master/docs/src/plugins/loaders).
However, it is _not_ required to include documentation when you contribute a new plugin definition to `discovery.yml`,
as members of the core team are happy to any missing docs themselves as part of the review process.

#### Plugin definitions

At a minimum, a plugin definition must have a `name` and a `namespace`, and at least one [variant definition](#variant-definitions) with a `pip_url` (its [`pip install`](https://pip.pypa.io/en/stable/reference/pip_install/#usage) argument).

It is recommended to add a `label`, `logo_url`, and `description` to the plugin definition, and `docs` and `repo` URLs to the variant definition(s).

Most of the time, variant definitions should also have a `settings` array with [setting definitions](#setting-definitions).

Additionally:
- `capabilities` should be specified for extractor variants,
- non-default variant executable names can be specified using `executable`, and
- default values for [plugin extras](/docs/configuration.html#plugin-extras) can be specified at the plugin definition level and further overridden at the variant definition level.

##### Variant definitions

If a plugin will only ever have a single [variant](/docs/plugins.html#variants) (as is typically the case for all types except for extractors and loaders),
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
      value: '' # Optional (Use to set a default value)
      placeholder: Ex. format_like_this # Optional (Use to set the input's placeholder default)
      kind: string # Optional (Use for a first-class input control. Default is `string`, others are `integer`, `boolean`, `date_iso8601`, `password`, `options`, `file`, `array`, `object`, and `hidden`)
      description: Setting description # Optional (Use to provide inline context)
      tooltip: Here is some more info... # Optional (use to provide additional inline context)
      documentation: https://meltano.com/ # Optional (use to link to specific supplemental documentation)
      protected: true # Optional (use in combination with `value` to provide an uneditable default)
      env: SOME_API_KEY # Optional (use to delegate to an environment variable for overriding this setting's value)
      env_aliases: [OTHER_ENV] # Optional (use to delegate alternative environment variables for overriding this setting's value)
      value_processor: nest_object # Optional (Modify value after loading it from source: env, meltano.yml, system database. Target type needs to match `kind`. Options: `nest_object`, `upcase_string`)
      value_post_processor: stringify # Optional (Modify loaded value before passing it to plugin. Target type does not need to match `kind`. Options: `stringify`)
```

###### Protected settings

Until role-based access control is implemented in Meltano, we need to prevent user editing of certain settings from the UI. View this [`tap-gitlab` environment variable setup example](/tutorials/gitlab-and-postgres.html#add-extractor) to learn how to work with this current limitation.

### Adopting a plugin

When the maintainer of the default [variant](/docs/plugins.html#variants) of a discoverable plugin becomes unresponsive to issues and contributions filed by the community,
that plugin is considered up for adoption, which means that we are looking for a different variant of the plugin with a more engaged maintainer to become the new default.

This new variant can either be a fork of the original default variant, or an alternative implementation for the same source or destination, as long as it is actively maintained.

If you maintain or are aware of such a variant,
please add it to your Meltano project as a [custom plugin](/docs/plugins.html#custom-plugins) and [make it discoverable](#making-a-custom-plugin-discoverable),
or [file an issue](/docs/getting-help.html#issue-tracker) so that the Meltano core team can assist you.

As a plugin's primary maintainer, you do not have to spend a lot of time improving the plugin yourself.
In fact, attracting more users and getting the community involved is likely to recude your personal maintenance burden,
since you'll receive contributions with bug fixes and new features that you will only be expected to review, not build yourself.

### Local changes to `discovery.yml`

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

### Taps & Targets Development

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
1. Use a separate repo (meltano/target|tap-x) in GitLab
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

#### Models

When updating the models that will appear in the UI, you can follow these steps:

1. Create [`table.m5o` file](/docs/architecture.html#table) that defines the UI columns that will appear on the UI
1. Update [`topic.m5o` file](/docs/architecture.html#topic) to include the newly created model table
1. Compile model repo with `python3 setup.py sdist`
1. Go to your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) and replace `pip_url` with the file path to the targz file created
1. Run `meltano install` to fetch new settings
1. Refresh browser and you should now see your changes in the UI

### Dashboard Development

To create a dashboard plugin like <https://gitlab.com/meltano/dashboard-google-analytics>, follow these steps:

1. Set up the extractor and model you are creating dashboard(s) and reports for in your local Meltano instance.
1. Start Meltano UI.
1. Use the UI to create the desired reports based on the model's designs. Name the reports appropriately, but don't include the extractor name or label.
1. Create one or more new dashboard and add the reports to it. If you're creating just one dashboard, name it after the extractor label (e.g. "Google Analytics", not `tap-google-analytics`). If you're creating multiple dashboards, add an appropriate subtitle after a colon (e.g. "Google Analytics: My Dashboard").
1. Create a new plugin repository named `dashboard-<data source>` (e.g. `dashboard-google-analytics`).
1. Copy over `setup.py`, `README.md`, and `LICENSE` from <https://gitlab.com/meltano/dashboard-google-analytics> and edit these files as appropriate.
1. Move your newly created dashboards and reports from your local Meltano project's `analyze/dashboards` and `analyze/reports` to `dashboards` and `reports` inside the new plugin repository.
1. Push your new plugin repository to GitLab.com. Official dashboard plugins live at `https://gitlab.com/meltano/dashboard-...`.
1. Add an entry to `src/meltano/core/bundle/discovery.yml` under `dashboards`. Set `namespace` to the `namespace` of the extractor and model plugins the dashboard(s) and reports are related to (e.g. `tap_google_analytics`), and set `name` and `pip_url` set as appropriate.
1. Delete the dashboard(s) and reports from your local Meltano project's `analyze` directory.
1. Ensure that your local Meltano instance uses the recently modified `discovery.yml` by following the steps under ["Local changes to discovery.yml](#local-changes-to-discovery-yml).
1. Run `meltano add --include-related extractor <extractor name>` to automatically install all plugins related to the extractor, including our new dashboard plugin. Related plugins are also installed automatically when installing an extractor using the UI, but we can't use that flow here because the extractor has already been installed.
1. Verify that the dashboard(s) and reports have automatically been added to your local Meltano project's `analyze` directory and show up under "Dashboards" in the UI.
1. Success! You can now submit a merge request to Meltano containing the changes to `discovery.yml` (and an appropriate `CHANGELOG` item, of course).

### File Bundle Development

To create a file bundle plugin like <https://gitlab.com/meltano/files-dbt>, follow these steps:

1. Create a new plugin repository named `files-<service/tool>` (e.g. `files-airflow` or `files-docker`).
1. Copy over `setup.py`, `README.md`, and `LICENSE` from <https://gitlab.com/meltano/files.dbt> and edit these files as appropriate.
1. Create a `bundle` directory with an empty `__init__.py` file.
1. Add all desired directories and files to the `bundle` directory. All of these files will be copied over into the Meltano project directory when the file bundle is added to the project.
1. Add all file paths under `bundle` to the `package_data["bundle"]` array in `setup.py`
1. Push your new plugin repository to GitLab.com. Official file bundle plugins live at `https://gitlab.com/meltano/files-...`.
1. Add an entry to `src/meltano/core/bundle/discovery.yml` under `files`. Set `name` and `pip_url` as appropriate, and if applicable, set `namespace` to the `namespace` of the plugin the file bundle is related to (e.g. `dbt`).
1. If any files are to be updated automatically when [`meltano upgrade`](/docs/command-line-interface.html#upgrade) is run, add an `update` object with `[file path]: True` entries for each file.
1. Success! You can now submit a merge request to Meltano containing the changes to `discovery.yml` (and an appropriate `CHANGELOG` item, of course).

## System Database

Meltano API and CLI are both supported by a database that is managed using Alembic migrations.

:::tip Note
[Alembic](https://alembic.sqlalchemy.org/en/latest/) is a full featured database migration working on top of SQLAlchemy.
:::

Migrations for the system database are located inside the `meltano.migrations` module.

To create a new migration, use the `alembic revision -m "message"` command, then edit the created file with the necessary database changes. Make sure to implement both `upgrade` and `downgrade`, so the migration is reversible, as this will be used in migration tests in the future.

Each migration should be isolated from the `meltano` module, so **don't import any model definition inside a migration**.

:::warning
Meltano doesn't currently support auto-generating migration from the models definition.
:::

To run the migrations, use `meltano upgrade` inside a Meltano project.

## Documentation

Meltano uses [VuePress](https://vuepress.vuejs.org/) to manage its documentation site. Some of the benefits it provides us includes:

- Enhanced Markdown authoring experience
- Automatic check for broken relative links

### Text

Follow the [Merge Requests](#merge-requests) and [Changelog](#changelog) portions of this contribution section for text-based documentation contributions.

### Images

When adding supporting visuals to documentation, adhere to:

- Use Chrome in "incognito mode" (we do this to have the same browser bar for consistency across screenshots)
- Screenshot the image at 16:9 aspect ratio with minimum 1280x720px
- Place `.png` screenshot in `src/docs/.vuepress/public/screenshots/` with a descriptive name

## Testing

### End-to-End Testing with Cypress

Our end-to-end tests are currently being built with [Cypress](https://www.cypress.io/).

#### How to Run Tests

1. Initialize a new meltano project with `meltano init $PROJECT_NAME`
1. Change directory into `$PROJECT_NAME`
1. Start up project with `meltano ui`
1. Clone Meltano repo
1. Open Meltano repo in Terminal
1. Run `yarn setup`
1. Run `yarn test:e2e`

This will kick off a Cypress application that will allow you to run tests as desired by clicking each test suite (which can be found in `/src/tests/e2e/specs/*.spec.js`)

![Preview of Cypres app running](/images/cypress-tests/cypTest-01.png)

::: tip INFO
In the near future, all tests can flow automatically; but there are some complications that require manual triggering due to an inability to read pipeline completion.
:::

## Code style

### Tools

Meltano uses the below tools to enforce consistent code style. Explore the [repo](https://gitlab.com/meltano/meltano/tree/master) to learn of the specific rules and settings of each.

Python:
- [isort](https://pycqa.github.io/isort/)
- [Black](https://github.com/ambv/black)
- [Flakehell](https://flakehell.readthedocs.io/)
- [wemake-python-styleguide](https://wemake-python-stylegui.de/en/latest/)
- [MyPy](https://mypy.readthedocs.io/en/stable/)

Flakehell is a wrapper for Flake8 and its various plugins, and wemake-python-styleguide is a plugin for Flake8 that offers an extensive set of opinionated rules that encourage clean and correct code.

MyPy is currently only executed as part of the build pipeline in order to avoid overwhelming developers with the complete list of violations. This allows for incremental and iterative improvement without requiring a concerted effort to fix all errors at once.

Javascript:
- [ESLint](https://eslint.org/docs/rules/)
- [ESLint Vue Plugin](https://github.com/vuejs/eslint-plugin-vue)
- [Prettier](https://prettier.io/)

You may use `make lint` to automatically lint all your code, or `make show_lint` if you only want to see what needs to change.

### Mantra

> A contributor should know the exact line-of-code to make a change based on convention

In the spirit of GitLab's "boring solutions" with the above tools and mantra, the codebase is additionally sorted as follows:

#### Imports

Javascript `import`s are sorted using the following pattern:

1. Code source location: third-party → local (separate each group with a single blank line)
1. Import scheme: Default imports → Partial imports
1. Name of the module, alphabetically: 'lodash' → 'vue'

::: tip
There should be only 2 blocks of imports with a single blank line between both blocks.
The first rule is used to separate both blocks.
:::

```js
import lodash from 'lodash'                  // 1: third-party, 2: default, 3: [l]odash
import Vue from 'vue'                        // 1: third-party, 2: default, 3: [v]ue
import { bar, foo } from 'alib'              // 1: third-party, 2: partial, 3: [a]lib
import { mapAction, mapState } from 'vuex'   // 1: third-party, 2: partial, 3: [v]uex
¶  // 1 blank line to split import groups
import Widget from '@/component/Widget'      // 1: local, 2: default, 3: @/[c]omponent/Widget
import poller from '@/utils/poller'          // 1: local, 2: default, 3: @/[u]tils/poller
import { Medal } from '@/component/globals'  // 1: local, 2: partial, 3: @/[c]omponent/globals
import { bar, thing } from '@/utils/utils'   // 1: local, 2: partial, 3: @/[u]tils/utils
¶
¶  // 2 blank lines to split the imports from the code
```

Python imports are sorted automatically using [`isort`](https://pycqa.github.io/isort/). This is executed as part of the `make lint` command, as well as during execution of the pre-commit hook.

#### Definitions

Object properties and methods are alphabetical where `Vuex` stores are the exception (`defaultState` -> `getters` -> `actions` -> `mutations`)

::: warning
We are looking to automate these rules in https://gitlab.com/meltano/meltano/issues/1609.
:::

:::warning Troubleshooting
When testing your contributions you may need to ensure that your various `__pycache__` directories are removed. This helps ensure that you are running the code you expect to be running.
:::

## UI/UX

### Visual Hierarchy

#### Depth

The below level hierarchy defines the back to front depth sorting of UI elements. Use it as a mental model to inform your UI decisions.

- Level 1 - Primary navigation, sub-navigation, and signage - _Grey_
- Level 2 - Primary task container(s) - _White w/Shadow_
- Level 3 - Dropdowns, dialogs, pop-overs, etc. - _White w/Shadow_
- Level 4 - Modals - _White w/Lightbox_
- Level 5 - Toasts - _White w/Shadow + Message Color_

#### Interactivity

Within each aforementioned depth level is an interactive color hierarchy that further organizes content while communicating an order of importance for interactive elements. This interactive color hierarchy subtly influences the user's attention and nudges their focus.

1. Primary - _`$interactive-primary`_
   - Core interactive elements (typically buttons) for achieving the primary task(s) in the UI
   - Fill - Most important
   - Stroke - Important
1. Secondary - _`$interactive-secondary`_
   - Supporting interactive elements (various controls) that assist the primary task(s) in the UI
   - Fill - Most important
     - Can be used for selected state (typically delegated to stroke) for grouped buttons (examples usage seen in Transform defaults)
   - Stroke - Important
     - Denotes the states of selected, active, and/or valid where grey represents the opposites unselected, inactive, and/or invalid
1. Tertiary - _Greyscale_
   - Typically white buttons and other useful controls that aren't core or are in support of the primary task(s) in the UI
1. Navigation - _`$interactive-navigation`_
   - Denotes navigation and sub-navigation interactive elements as distinct from primary and secondary task colors

After the primary, secondary, tertiary, or navigation decision is made, the button size decision is informed by:

1. Use the default button size
1. Use the `is-small` modifier if it is within a component that can have multiple instances

### Markup Hierarchy

There are three fundamental markup groups in the codebase. All three are technically VueJS single-file components but each have an intended use:

1. Views (top-level "pages" and "page containers" that map to parent routes)
2. Sub-views (nested "pages" of "page containers" that map to child routes)
3. Components (widgets that are potentially reusable across parent and child routes)

Here is a technical breakdown:

1. Views - navigation, signage, and sub-navigation
   - Navigation and breadcrumbs are adjacent to the main view
   - Use `<router-view-layout>` as root with only one child for the main view:
     1. `<div class="container view-body">`
        - Can expand based on task real-estate requirements via `is-fluid` class addition
   - Reside in the `src/views` directory
2. Sub-views - tasks
   - Use `<section>` as root (naturally assumes a parent of `<div class="container view-body">`) with one type of child:
     - One or more `<div class="columns">` each with their needed `<div class="column">` variations
   - Reside in feature directory (ex. `src/components/analyze/AnalyzeModels`)
3. Components - task helpers
   - Use Vue component best practices
   - Reside in feature or generic directory (ex. `src/components/analyze/ResultTable` and `src/components/generic/Dropdown`)

## Merge Requests

:::tip Searching for something to work on?
Start off by looking at our [~"Accepting Merge Requests"][accepting merge requests] label.

Keep in mind that this is only a suggestion: all improvements are welcome.
:::

Meltano uses an approval workflow for all merge requests.

1. Create your merge request
1. Assign the merge request to any Meltano maintainer for a review cycle
1. Once the review is done the reviewer may approve the merge request or send it back for further iteration
1. Once approved, the merge request can be merged by any Meltano maintainer

### Reviews

A contributor can ask for a review on any merge request, without this merge request being done and/or ready to merge.

Asking for a review is asking for feedback on the implementation, not approval of the merge request. It is also the perfect time to familiarize yourself with the code base. If you don’t understand why a certain code path would solve a particular problem, that should be sent as feedback: it most probably means the code is cryptic/complex or that the problem is bigger than anticipated.

Merge conflicts, failing tests and/or missing checkboxes should not be used as ground for sending back a merge request without feedback, unless specified by the reviewer.

## Changelog

Meltano uses [changelog-cli](https://github.com/mc706/changelog-cli) to populate the CHANGELOG.md

### Script

Use `changelog (new|change|fix|breaks) MESSAGE` to describe your current work in progress.

```bash
$ poetry run changelog new "add an amazing feature"
$ git add CHANGELOG.md
```

Make sure to add CHANGELOG entries to your merge requests.

## Tmuxinator

Tmuxinator is a way for you to efficiently manage multiple services when starting up Meltano.

### Why Tmuxinator?

In order to run applications, you need to run multiple sessions and have to do a lot of repetitive tasks (like sourcing your virtual environments). So we have created a way for you to start and track everything in its appropriate panes with a single command.

1. Start up Docker
1. Start Meltano API
1. Start the web app

It's a game changer for development and it's worth the effort!

### Requirements

1. [tmux](https://github.com/tmux/tmux) - Recommended to install with brew
1. [tmuxinator](https://github.com/tmuxinator/tmuxinator)

This config uses `$MELTANO_VENV` to source the virtual environment from. Set it to the correct directory before running tmuxinator.

### Instructions

1. Make sure you know what directory your virtual environment is. It is normally `.venv` by default.
1. Run the following commands. Keep in mind that the `.venv` in line 2 refers to your virtual environment directory in Step #1.

```bash
cd path/to/meltano
MELTANO_VENV=.venv tmuxinator local
```

### Resources

- [Tmux Cheat Sheet & Quick Reference](https://tmuxcheatsheet.com/)

[Accepting Merge Requests]: https://gitlab.com/groups/meltano/-/issues?label_name[]=Accepting%20Merge%20Requests
