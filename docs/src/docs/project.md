---
description: At the core of the Meltano experience is your Meltano project, which represents the single source of truth regarding your ELT pipelines.
---

# Projects

<!-- The following is reproduced in docs/src/README.md#meltano-init -->

At the core of the Meltano experience is your Meltano project,
which represents the single source of truth regarding your ELT pipelines:
how data should be [integrated](/docs/integration.html) and [transformed](/docs/transforms.html),
how the pipelines should be [orchestrated](/docs/orchestration.html),
and how the various [plugins](#plugins) that make up your pipelines should be [configured](/docs/configuration.html).

Since a Meltano project is just a directory on your filesystem containing
text-based files, you can treat it like any other software development project
and benefit from DataOps best practices such as version control, code review,
and continuous integration and deployment (CI/CD).

You can initialize a new Meltano project using [`meltano init`](/docs/command-line-interface.html#init).

## `meltano.yml` project file

At a minimum, a Meltano project must contain a project file named `meltano.yml`,
which contains your project configuration and tells Meltano that a particular directory is a Meltano project.

The only required property is `version`, which currently always holds the value `1`.

### Configuration

At the root of `meltano.yml`, and usually at the top of the file, you will find project-specific configuration.

In a newly initialized project, only the [`send_anonymous_usage_stats` setting](/docs/settings.html#send-anonymous-usage-stats)
will be set.

To learn which settings are available, refer to the [Settings reference](/docs/settings.html).

### Plugins

Your project's [plugins](/docs/plugins.html#project-plugins),
typically [added to your project](/docs/plugin-management.html#adding-a-plugin-to-your-project)
using [`meltano add`](/docs/command-line-interface.html#add),
are defined under the `plugins` property, inside an array named after the [plugin type](/docs/plugins.html#types) (e.g. `extractors`, `loaders`).

Every plugin in your project needs to have:
1. a `name` that's unique among plugins of the same type,
2. a [base plugin description](/docs/plugins.html#project-plugins) describing the package in terms Meltano can understand, and
3. [configuration](/docs/configuration.html) that can be defined across [various layers](/docs/configuration.html#configuration-layers), including the definition's [`config` property](#plugin-configuration).

A base plugin description consists of the `pip_url`, `executable`, `capabilities`, and `settings` properties,
but not every plugin definition will specify these explicitly:

- An [**inheriting plugin definition**](#inheriting-plugin-definitions) has an **`inherit_from`** property and inherits its base plugin description from another plugin in your project or a [discoverable plugin](/docs/plugins.html#discoverable-plugins) identified by name.
- A [**custom plugin definition**](#custom-plugin-definitions) has a **`namespace`** property instead and explicitly defines its base plugin description.
- A [**shadowing plugin definition**](#shadowing-plugin-definitions) has neither property and implicitly inherits its base plugin description from the [discoverable plugin](/docs/plugins.html#discoverable-plugins) with the same **`name`**.

When inheriting a base plugin description, the plugin definition does not need to explicitly specify a `pip_url`
(the package's [`pip install`](https://pip.pypa.io/en/stable/reference/pip_install/#usage) argument),
but you may want to override the inherited value and set the property explicitly to [point at a (custom) fork](/docs/plugin-management.html#using-a-custom-fork-of-a-plugin) or to [pin a package to a specific version](/docs/plugin-management.html#using-a-custom-fork-of-a-plugin#pinning-a-plugin-to-a-specific-version).
When a plugin is added using `meltano add`, the `pip_url` is automatically repeated in the plugin definition for convenience.

#### Inheriting plugin definitions

A plugin defined with an `inherit_from` property inherits its [base plugin description](/docs/plugins.html#project-plugins) from another plugin identified by name. To find the matching plugin, other plugins in your project are considered first, followed by
[discoverable plugins](/docs/plugins.html#discoverable-plugins):

```yml{5,7}
plugins:
  extractors:
  - name: tap-postgres          # Shadows discoverable `tap-postgres` (see below)
  - name: tap-postgres--billing
    inherit_from: tap-postgres  # Inherits from project's `tap-postgres`
  - name: tap-bigquery--events
    inherit_from: tap-bigquery  # Inherits from discoverable `tap-bigquery`
```

When inheriting from another plugin in your project, its [configuration](/docs/configuration.html) is also inherited as if the values were defaults, which can then be overridden as appropriate:

```yml{10-12,15-18}
plugins:
  extractors:
  - name: tap-google-analytics
    variant: meltano
    config:
      key_file_location: client_secrets.json
      start_date: '2020-10-01T00:00:00Z'
  - name: tap-ga--view-foo
    inherit_from: tap-google-analytics
    config:
      # `key_file_location` and `start_date` are inherited
      view_id: 123456
  - name: tap-ga--view-bar
    inherit_from: tap-google-analytics
    config:
      # `key_file_location` is inherited
      start_date: '2020-12-01T00:00:00Z' # `start_date` is overridden
      view_id: 789012
```

Note that the presence of a [`variant` property](#variants) causes only discoverable plugins to be considered
(even if there is also a matching plugin in the project),
since only these can have multiple [variants](/docs/plugins.html#variants):

```yml{6,8-9}
plugins:
  loaders:
  - name: target-snowflake          # Shadows discoverable `target-snowflake` (see below)
    variant: datamill-co            # using variant `datamill-co`
  - name: target-snowflake--derived
    inherit_from: target-snowflake  # Inherits from project's `target-snowflake`
  - name: target-snowflake--transferwise
    inherit_from: target-snowflake  # Inherits from discoverable `target-snowflake`
    variant: transferwise           # using variant `transferwise`
```

To learn how to add an inheriting plugin to your project, refer to the [Plugin Management guide](/docs/plugin-management.html#plugin-inheritance).

#### Custom plugin definitions

A plugin defined with a `namespace` property (but no `inherit_from` property) is a [custom plugin](/docs/plugins.html#custom-plugins) that explicitly defines its [base plugin description](/docs/plugins.html#project-plugins):

```yaml{4-14}
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

To learn how to add a custom plugin to your project, refer to the [Plugin Management guide](/docs/plugin-management.html#custom-plugins).

#### Shadowing plugin definitions

A plugin defined without an `inherit_from` or `namespace` property implicitly inherits its [base plugin description](/docs/plugins.html#project-plugins) from the [discoverable plugin](/docs/plugins.html#discoverable-plugins) with the same `name`, as a form of [shadowing](https://en.wikipedia.org/wiki/Variable_shadowing):

```yaml{3}
plugins:
  extractors:
  - name: tap-gitlab
```

To learn how to add a discoverable plugin to your project, refer to the [Plugin Management guide](/docs/plugin-management.html#discoverable-plugins).

##### Variants

If multiple [variants](/docs/plugins.html#variants) of a discoverable plugin are available,
the `variant` property can be used to choose a specific one:

```yaml{4}
plugins:
  extractors:
  - name: tap-gitlab
    variant: meltano
```

If no `variant` is specified, the _original_ variant supported by Meltano is used.
Note that this is not necessarily the _default_ variant that is recommended to new users and would be used if the plugin were newly added to the project.

#### Plugin configuration

A plugin's [configuration](/docs/configuration.html) is stored under a `config` property.
Values for [plugin extras](/docs/configuration.html#plugin-extras) are stored among the plugin's other properties, outside of the `config` object:

```yaml{3-7}
extractors:
- name: tap-example
  config:
    # Configuration goes here!
    example_setting: value
  # Extras go here!
  example_extra: value
```
