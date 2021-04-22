---
sidebar: auto
metaTitle: Meltano Tutorial - Create a Custom Extractor
description: Learn how to use Meltano to create a custom data extractor.
lastUpdatedSignificantly: 2021-04-22
---

# Create a Custom Extractor

As much as we'd like to support all the data sources out there, we'll need your help to get there. If you find a data source that Meltano doesn't support right now, it might be time to get your hands dirty.


## How to Create an Extractor

The [Singer SDK](https://gitlab.com/meltano/singer-sdk#user-content-singer-sdk-a-framework-for-building-singer-taps)
makes it easier than ever to create new taps for your own custom data sources. For more information
on creating a tap, see the [SDK Dev Guide](https://gitlab.com/meltano/singer-sdk/-/blob/main/docs/dev_guide.md).

::: tip
[Singer](https://singer.io) taps and targets are the mechanism Meltano uses to extract
 and load data. For more details about the Singer specification, please visit our
 [Singer Spec](https://meltano.com/docs/singer-spec.html) documentation.
:::

## Create the Plugin's Package

As a first step, follow the [instructions](https://gitlab.com/meltano/singer-sdk/-/tree/main/cookiecutter/tap-template)
in the SDK documentation to create a new project from the provided cookie cutter template.

::: tip
[cookiecutter](https://cookiecutter.readthedocs.io/en/latest/) is a python tool to scaffold projects quickly from an existing template.
:::

## Add the Plugin to Your Meltano Project

Meltano exposes each plugin configuration in the plugin definition, located in the [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file).

To test the plugin as part of your Meltano project, you will need to add your plugin configuration in the `meltano.yml` file for your project.

In your existing `meltano.yml`:

```yml
# ...
plugins:
  extractors:
    # Insert a new entry:
    - name: tap-my-custom-source
      namespace: tap_my_custom_source
      # Absolute path to local test script:
      executable: /path/to/tap-my-custom-source.sh
      capabilities:
        - state
        - catalog
        - discover
      settings:
        - name: username
          value: me@here.com
        - name: password
          kind: password
        - name: start_date
          value: '2015-09-21T04:00:00Z'
  loaders:
    # your loaders here:
    - name: target-jsonl
      variant: andyh1203
      pip_url: target-jsonl
    # ...
```

::: tip
You can further customize the appearance of your custom extractor in Meltano UI using the following options:

- `label`
- `logo_url`
- `description`
:::

Any time you manually add new plugins to `meltano.yml`, it's a good idea to rerun the install command:

```bash
meltano install
```

### Plugin Settings

When creating a new plugin, you'll often have to expose some settings to the user so that Meltano can generate the correct configuration to run your plugin.

To expose such a setting, you'll need to define it as such

- **name**: Identifier of this setting in the configuration.
  The name is the most important field of a setting, as it defines how the value will be passed down to the underlying component.
  Nesting can be represented using the `.` separator.

  - `foo` represents the `{ foo: VALUE }` in the output configuration.
  - `foo.a` represents the `{ foo: { a: VALUE } }` in the output configuration.

- **kind**: Represent the type of value this should be, (e.g. `password` or `date_iso8601`).
- **value** (optional): Define the default value for this variable. It should also be used as a placeholder for UX purposes.
- **env** (optional): Define the environment variable name used to set this value at runtime. _Defaults to `<NAMESPACE>_<SETTING_NAME>` in all-caps_.

### Passing sensitive setting values

_**It is best practice not to store sensitive values directly in `meltano.yml`.**_

Note in our example above, we provided values directly for `username` and `start_date` but we did not enter a value
for password. This was intentional, to avoid storing sensitive credentials in clear text within our source code. Instead, set the environment variable for this setting by running `export TAP_MY_CUSTOM_SOURCE_PASSWORD=MyPass1234!`
before invoking the plugin with Meltano.

You may use any of the following to configure setting values (in order of precedence):

- Environment variables
- `config` section in the plugin
- Meltano UI
- `value` of the setting's definition

## Interacting with your new plugin

Now that your plugin is installed and configured, you are ready to interact with it using Meltano.

Use `meltano invoke` to run your plugin in isolation:

```bash
meltano invoke tap-my-custom-source --discover
```

You can also use `meltano select` to parse your `catalog` and list all available entities and attributes:

```bash
meltano select --list --all
```

Now, run an ELT pipeline using your new tap:

```bash
meltano elt tap-my-custom-source target-sqlite
```

::: tip
Meltano manages converting the plugin's configuration to the appropriate definition for the plugin. You can find the generated file in `.meltano/run/tap-my-custom-source/tap.config.json`.
:::

## Publishing to the world

Once you've built your tap and it is providing you the data you need, we hope you will consider
sharing it with the world! We often find that community
members who benefit from your tap also may contribute back their own improvements in
the form of pull requests.

### Publish to PyPi

If you've built your tap using the SDK, you can take advantage of the streamlined
[`poetry publish`](https://python-poetry.org/docs/cli/#publish) command to publish
your tap directly to PyPi.

1. Create an account with [PyPi](https://pypi.org).
2. Create a PyPi API token for use in automated publishing. (Optional but recommended.)
3. Run `poetry --build publish` from within your repo to build and push your latest version
   to the PyPi servers.

### Test a `pip` install

We recommend using pipx to avoid dependency conflicts:

```bash
pip3 install pipx
pipx ensurepath
python -m pipx install tap-my-custom-source
```

After restarting your terminal, this should also work without the `python -m` prefix:

```bash
pipx install tap-my-custom-source
```

Or if you don't want to use pipx:

```bash
pip3 install tap-my-custom-source
```

If you have gotten this far... _**Congrats!** You are now a proud Singer tap developer!_

### Updates for production use

Once your repo is installable with pip, you can reference this in your `meltano.yml` file with three quick steps:

1. Add a `pip_url` property to your `extractor` definition, for example `pip_url: tap-my-custom-source`.
   - _Alternatively, you can also install the latest from your git repo directly using this syntax:
     `pip_url: git+https://github.com/myusername/tap-my-custom-source@main`_
2. Replace `/path/to/tap-my-custom-source.sh` with just the executable name: `tap-my-custom-source`.
3. Rerun `meltano install` to use the version from pip in place of the local test version.

## References

- [Singer SDK](https://github.com/meltano/singer-sdk)
- [Singer Spec](https://meltano.com/docs/singer-spec.html)
