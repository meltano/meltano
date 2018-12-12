---
sidebar: Meltano CLI
---

- `meltano init [project name]`: Create an empty meltano project.
- {: #meltano-add}`meltano add [extractor | loader] [name_of_plugin]`: Adds extractor or loader to your **meltano.yml** file and installs in `.meltano` directory with `venvs`, `dbt` and `pip`.
- `meltano install`: Installs all the dependencies of your project based on the **meltano.yml** file.
- `meltano discover all`: list available extractors and loaders:
  - `meltano discover extractors`: list only available extractors
  - `meltano discover loaders`: list only available loaders
- `meltano extract [name of extractor] --to [name of loader]`: Extract data to a loader and optionally transform the data
- `meltano transform [name of transformation] --warehouse [name of warehouse]`: \*\*
- `meltano elt <job_id> --extractor <extractor> --loader <loader> [--dry]`: Extract, Load, and Transform the data.
- `meltano invoke <plugin_name> PLUGIN_ARGS...`: Invoke the plugin manually.
- `meltano select [--list] [--all] <tap_name> [ENTITIES_PATTERN] [ATTRIBUTE_PATTERN]`: Manage the selected entities/attribute for a specific tap.

## meltano select

> Note: not all tap support this feature; tap needs to support the --discover switch.
> You can use `meltano invoke tap-... --discover` to see if the tap supports it.

Use this command to add select patterns to a specific extractor in your Meltano project.

### Select Pattern

Meltano select patterns are inspired by the glob syntax you might find in your operation system.

  - `*`: matches any sequence of characters
  - `?`: matches one character
  - `[abc]`: matches either `a`, `b`, or `c`
  - `[!abc]`: matches any character **but** `a`, `b`, or `c`

#### Examples

> Note: depending on your shell, you might have to escape the special characters in the select pattern.

```bash
$ meltano select tap-carbon-intensity '*' 'name*'
```

This will cause all streams to select any attributes starting with `name`.

```bash
$ meltano select tap-carbon-intensity 'region'
```

This will cause the `region` stream, along with all its attributes to be selected.

### --exclude

Using the exclude switch will cause Meltano to exclude any attributes that match the filter.

> Note: the exclusion has precedence over the inclusion. If an attribute is excluded, there
> is no way to include it back without removing the exclusion select pattern first.

#### Examples

```bash
$ meltano select --exclude tap-carbon-intensity '*' 'longitude'
$ meltano select --exclude tap-carbon-intensity '*' 'latitude'
```

This will cause meltano to exlude any `longitude` and `latitude` attribute from all stream.

### --list

Using the `--list` switch will cause meltano to list the current selected tap attributes.

> Note: the `--all` can be used to show all the tap attributes, along with their selection status.
