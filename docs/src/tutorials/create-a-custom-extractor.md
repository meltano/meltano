---
sidebar: auto
metaTitle: Meltano Tutorial - Create a Custom Extractor
description: Learn how to use Meltano to create a custom data extractor.
---

# Create a Custom Extractor

As much as we'd like to support all the data sources out there, we'll need your help to get there. If you find a data source that Meltano doesn't support right now, it might be time to get your hands dirty.

## How to Create an Extractor

The [Singer SDK](https://gitlab.com/meltano/singer-sdk)
makes it easier than ever to create new [extractors](/docs/plugins.html#extractors) for your own custom data sources.

::: tip
[Singer](https://singer.io) taps and targets are the mechanism Meltano uses to extract
 and load data. For more details about the Singer specification, please visit our
 [Singer Spec](/docs/singer-spec.html) documentation.
:::

## Create the Plugin's Package

1. As a first step, follow the [instructions](https://gitlab.com/meltano/singer-sdk/-/tree/main/cookiecutter/tap-template)
in the SDK documentation to create a new project from the provided cookiecutter template.
2. As you are developing, consult the [SDK Dev Guide](https://gitlab.com/meltano/singer-sdk/-/blob/main/docs/dev_guide.md) for developer documentation and the
[Code Samples](https://gitlab.com/meltano/singer-sdk/-/blob/main/docs/code_samples.md) page to find
reusable sample code.

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
      config:
        # Configured values:
        username: me@example.com
        start_date: '2021-01-01'
      settings:
        - name: username
        - name: password
          kind: password
        - name: start_date
          # Default value for the plugin:
          value: '2010-01-01T00:00:00Z'
  loaders:
    # your loaders here:
    - name: target-jsonl
      variant: andyh1203
      pip_url: target-jsonl
    # ...
```

::: tip
You can further customize the appearance of your custom extractor in [Meltano UI](/docs/ui.html) using the following options:

- `label`
- `logo_url`
- `description`
:::

Any time you manually add new plugins to `meltano.yml`, you will need to rerun the
[install](/docs/command-line-interface.html#install) command:

```bash
meltano install
```

If you get an error that your custom extractor is uninstallable try adding a `pip_url` variable to your `meltano.yml`:

```yml
# ...
plugins:
  extractors:
    # Insert a new entry:
    - name: tap-my-custom-source
      namespace: tap_my_custom_source
      # If you are developing locally this can be any pip_url
      # It won't be used when you use the invoke command
      pip_url: git+https://gitlab.com/meltano/tap-gitlab.git
      # Absolute path to local test script:
      executable: /path/to/tap-my-custom-source.sh
 ```    

### Plugin Settings

When creating a new plugin, you'll often have to expose some settings to the user so that Meltano can generate the correct configuration to run your plugin.

To properly expose and configure your settings, you'll need to define them:

- **name**: Identifier of this setting in the configuration.
  The name is the most important field of a setting, as it defines how the value will be passed down to the underlying component.
  Nesting can be represented using the `.` separator.

  - `foo` represents the `{ foo: VALUE }` in the output configuration.
  - `foo.a` represents the `{ foo: { a: VALUE } }` in the output configuration.
- **kind**: Represent the type of value this should be, (e.g. `password` for sensitive values or `date_iso8601` for dates).
- **value** (optional): Define a default value for the plugin's setting.

### Passing sensitive setting values

_**It is best practice not to store sensitive values directly in `meltano.yml`.**_

Note in our example above, we provided values directly for `username` and `start_date` but we did not enter a value
for password. This was to avoid storing sensitive credentials in clear text within our source code. Instead, make sure the setting `kind` is set to `password` and then
run [`meltano config <plugin> set password <value>`](https://meltano.com/docs/getting-started.html#configure-the-extractor). You can also set the matching environment variable for this
setting by running `export TAP_MY_CUSTOM_SOURCE_PASSWORD=<value>`.

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

You can also use [`meltano select`](https://meltano.com/docs/getting-started.html#select-entities-and-attributes-to-extract)
to parse your `catalog` and list all available entities and attributes:

```bash
meltano select --list --all
```

Now, run an ELT pipeline using your new tap:

```bash
meltano elt tap-my-custom-source target-sqlite
```

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

### Make it discoverable

Once you have your tap published to PyPi, consider
[making it discoverable](https://meltano.com/docs/contributor-guide.html#making-a-custom-plugin-discoverable)
for other users of Meltano.

### Updates for production use

Once your repo is installable with pip, you can reference this in your `meltano.yml` file with three quick steps:

1. Add a `pip_url` property to your `extractor` definition, for example `pip_url: tap-my-custom-source`.
   - _Alternatively, you can also install the latest from your git repo directly using this syntax:
     `pip_url: git+https://github.com/myusername/tap-my-custom-source@main`_
2. Replace `/path/to/tap-my-custom-source.sh` with just the executable name: `tap-my-custom-source`.
3. Rerun `meltano install` to use the version from pip in place of the local test version.

## References

- [Singer SDK](https://github.com/meltano/singer-sdk)
- [Singer Spec](/docs/singer-spec.html)
