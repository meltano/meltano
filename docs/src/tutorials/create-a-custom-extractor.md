---
sidebar: auto
metaTitle: Meltano Tutorial - Create a Custom Extractor
description: Learn how to use Meltano to create a custom data extractor.
lastUpdatedSignificantly: 2020-01-20
---

# Create a Custom Extractor

As much as we'd like to support all the data sources out there, we'll need your help to get there. If you find a data source that Meltano doesn't support right now, it might be time to get your hands dirty.

We aim to make Meltano as thin as possible on top of the components it abstracts, so adding a new plugin should be straightforward.

If you think a new extractor is popular or useful enough for others, you can:

- Contribute it back so everyone can benefit!
- [Submit a "New Extractor Request"](https://gitlab.com/meltano/meltano/issues/new?issue[title]=New%20Extractor%20Request&issuable_template=feature_proposal)

## How to Create an Extractor

First things first, you'll need a data source to integrate: in this example, let's say we want to create a tap to fetch data from `GitLab`.

::: warning Heads-up!
If you are looking to integrate GitLab's data into your warehouse, please use the existing [`tap-gitlab`](/plugins/extractors/gitlab.html) rather than your own.
:::

## Create the Plugin's Package

Meltano uses [Singer](https://singer.io) taps and targets to extract and load data. For more details about the Singer specification, please visit [https://github.com/singer-io/getting-started](https://github.com/singer-io/getting-started)

::: tip
[cookiecutter](https://cookiecutter.readthedocs.io/en/latest/) is a python tool to scaffold projects quickly from an existing template.
:::

```bash
pip3 install cookiecutter
cookiecutter gh:singer-io/singer-tap-template
> project_name: tap-gitlab-custom
```

## Add the Plugin to Your Meltano Project (--custom)

Now that your plugin is part of your Meltano project, you need to add your plugin configuration in the `meltano.yml`'s plugin definition.

::: tip
Using `-e` in the `pip_url` will install the plugin as editable so any change you make is readily available.
:::

```bash
meltano add --custom extractor tap-gitlab-custom
# If you're running Meltano using Docker, ensure you run `docker run` with `--interactive` to allow `namespace` etc to be set:
# docker run --interactive -v $(pwd):/project -w /project meltano/meltano add --custom extractor tap-gitlab-custom

(namespace): tap_gitlab_custom
(pip_url): -e tap-gitlab-custom
(executable): tap-gitlab-custom
(capabilities): catalog,discover,state
(settings): username,password,start_date
```

Meltano exposes each plugin configuration in the plugin definition, located in the [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file).

::: tip
Meltano manages converting the plugin's configuration to the appropriate definition for the plugin. You can find the generated file in `.meltano/run/tap-gitlab-custom/tap.config.json`.
:::

Looking at the `tap-gitlab-custom` definition, we should see the following:

**meltano.yml**

```yaml
plugins:
  extractors:
    - capabilities:
      - catalog
      - discover
      - state
      executable: tap-gitlab-custom
      name: tap-gitlab-custom
      namespace: gitlab
      pip_url: -e tap-gitlab-custom
      settings:
        - name: username
        - name: password
        - name: start_date
```

Let's include some additional settings properties:

**meltano.yml**

```yaml
plugins:
  extractors:
    - capabilities:
      - catalog
      - discover
      - state
      executable: tap-gitlab-custom
      name: tap-gitlab-custom
      namespace: gitlab
      pip_url: -e tap-gitlab-custom
      settings:
        - name: username
        - name: password
          kind: password
        - name: start_date
          value: '2015-09-21T04:00:00Z'
```

You can further customize the appearance of your custom extractor in Meltano UI using the following options:

- `label`
- `logo_url`
- `description`

### Plugin Setting

When creating a new plugin, you'll often have to expose some settings to the user so that Meltano can generate the correct configuration to run your plugin.

To expose such a setting, you'll need to define it as such

- **name**: Identifier of this setting in the configuration.
  The name is the most important field of a setting, as it defines how the value will be passed down to the underlying component.
  Nesting can be represented using the `.` separator.

  - `foo` represents the `{ foo: VALUE }` in the output configuration.
  - `foo.a` represents the `{ foo: { a: VALUE } }` in the output configuration.

- **kind**: Represent the type of value this should be, (e.g. `password` or `date_iso8601`).

::: warning WIP
We are currently working on defining the complete list of setting's kind. See [issue (#739)](https://gitlab.com/meltano/meltano/issues/739) for more details.
:::

- **env** (optional): Define the environment variable name used to set this value at runtime. _Defaults to `NAMESPACE_NAME`_.
- **value** (optional): Define the default value for this variable. It should also be used as a placeholder for UX purposes.

Once the settings are exposed, you can use any of the following to set the proper values (in order of precedence):

- Environment variables
- `config` section in the plugin
- Meltano UI
- `value` of the setting's definition

## Interacting with your new plugin

Now that your plugin is installed and configured, you are ready to interact with it using Meltano.

Use `meltano invoke` to run your plugin in isolation:

```bash
meltano invoke tap-gitlab-custom --discover
```

If your custom tap doesn't support discovery mode, this may raise an error, but you will have verified that it was installed correctly and can be invoked through Meltano.

Assuming your custom tap supports discovery mode and advertises the `discover` capability,
use `meltano select` to parse your `catalog` and list all available entities and attributes:

```bash
meltano select --list --all tap-gitlab-custom
```

Now, run an ELT pipeline using your new tap:

```bash
meltano elt tap-gitlab-custom target-sqlite
```

## References

- [Singer specification](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md#singer-specification)
- [tap-gitlab](https://gitlab.com/meltano/tap-gitlab)
- [target-sqlite](https://gitlab.com/meltano/target-sqlite)
- [cookiecutter](https://github.com/audreyr/cookiecutter)
- [singer-tap-template](https://github.com/singer-io/singer-tap-template)
