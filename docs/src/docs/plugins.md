---
sidebarDepth: 2
---

# Available Plugins

## Extractors

Extractors are defined as the component that pulls data out of a data source, using the best integration for extracting bulk data.
Currently, Meltano supports [Singer.io](https://singer.io) taps as extractors.

### tap-zuora

<table>
  <tr>
    <th>Data Source</th>
    <td><a target="_blank" href="https://www.zuora.com/">https://www.zuora.com</a></td>
  </tr>
  <tr>
    <th>Repository</th>
    <td><a target="_blank" href="https://github.com/singer-io/tap-zuora">https://github.com/singerio/tap-zuora</a></td>
  </tr>
</table>

#### Default configuration

**.env**
```bash
ZUORA_USERNAME
ZUORA_PASSWORD
ZUORA_API_TOKEN   # preferred to ZUORA_PASSWORD
ZUORA_API_TYPE    # specifically 'REST' or 'AQuA'
ZUORA_PARTNER_ID  # optional, only for the 'AQuA` API type
ZUORA_START_DATE
ZUORA_SANDBOX     # specifically 'true' or 'false'
```

## Create your own

As much as we'd like to support all the data sources out there, we'll need your help to get there. If you find a data source that Meltano doesn't support right now, it might be time to get your hands dirty.

We aim to make Meltano as thin as possible on top of the components it abstracts, so adding a new plugin should be straightforward.

### How to create a tap

First things first, you'll need a data source to integrate: in this example, let's say we want to create a tap to fetch data from `GitLab`.

If you are looking to integrate GitLab's data into your warehouse, please use tap official [https://gitlab.com/meltano/tap-gitlab](tap-gitlab).
:::

### Create the plugin's package

Meltano uses [Singer](https://singer.io) taps and targets to extract and load data. For more details about the Singer specification, please visit [https://github.com/singer-io/getting-started](https://github.com/singer-io/getting-started)

::: tip
[cookiecutter](https://cookiecutter.readthedocs.io/en/latest/) is a python tool to scaffold projects quickly from an existing template.
:::

```bash
$ pip install cookiecutter
$ cookiecutter gh:singer-io/singer-tap-template
> project_name: tap-gitlab-custom
```

### Add the plugin to your Meltano project (--custom)

Now that your plugin is part of your Meltano project, you need to add your plugin configuration in the `meltano.yml`'s plugin definition.

::: tip
Using `-e` will install the plugin as editable so any change you make is readily available.
:::

```bash
# test
$ meltano add --custom extractor tap-gitlab-custom
...
> pip_url: -e tap-gitlab-custom
> executable: tap-gitlab-custom
```

Meltano exposes each plugin configuration in the plugin definition, located in the `meltano.yml` file.

::: tip
Meltano manages converting the `config` section to the appropriate definition for the plugin. You can find the generated file in `.meltano/run/tap-gitlab-custom/tap.config.json`.
:::

Looking at the `tap-gitlab-custom` definition, we should see the following (notice the `config` section is `null`):

**meltano.yml**
```yaml
plugins:
  extractors:
  - config: null
    executable: tap-gitlab-custom
    name: tap-gitlab-custom
    pip_url: -e tap-gitlab-custom
...
```

Let's include the default configuration for a sample tap:

**meltano.yml**
```yaml
plugins:
  extractors:
  - config: 
	  username: $GITLAB_USERNAME # supports env expansion
	  password: my_password
	  start_date: "2015-09-21T04:00:00Z"
    executable: tap-gitlab-custom
    name: tap-gitlab-custom
    pip_url: -e tap-gitlab-custom
...
```

::: warning
Due to an outstanding [bug (#521)](https://gitlab.com/meltano/meltano/issues/521) you must run `meltano install` after modifying the `config` section of a plugin.
:::

### Interacting with your new plugin

Now that your plugin is installed and configured, you are ready to interact with it using Meltano.

```
;; use `meltano invoke` to run your plugin in isolation
$ meltano invoke tap-gitlab-custom --discover

;; use `meltano select` to parse your `catalog`
$ meltano select --list tap-gitlab-custom '*' '*'

;; run an ELT using your new tap
$ meltano elt tap-gitlab-custom target-sqlite
```

### References

  - [Singer specification](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md#singer-specification)
  - [tap-gitlab](https://gitlab.com/meltano/tap-gitlab)
  - [target-sqlite](https://gitlab.com/meltano/target-sqlite)
  - [cookiecutter](https://github.com/audreyr/cookiecutter)
  - [singer-tap-template](https://github.com/singer-io/singer-tap-template)
