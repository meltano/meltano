---
title: Meltano 4.0 Migration Guide
description: Migrate existing projects to Meltano 4.0
layout: doc
sidebar_position: 22
---

The following guide covers breaking changes and migration steps for Meltano version `4.0.0`.

## Breaking Changes

### Python 3.9 support dropped

Meltano 4.0 requires Python 3.10 or later. If you are still using Python 3.9, upgrade to Python 3.10, 3.11, 3.12, 3.13, or 3.14 before upgrading Meltano.

### Docker image changes

The `psycopg2` extra has been removed from Meltano's Docker images to reduce image size. If you need PostgreSQL support in Docker, install it explicitly:

```dockerfile
FROM meltano/meltano:latest
RUN uv pip install psycopg2-binary
```

Alternatively, use the `postgres` extra and the `postgresql+psycopg` URI scheme with psycopg3.

## Removed Deprecated Features

### Deprecated CLI flags and arguments

The following deprecated CLI options have been removed:

- `meltano lock --all` flag (use `meltano lock` without flags, as it locks all plugins by default)
- `meltano install - <plugin_name>` syntax (use `meltano install <plugin_name>`)
- Plugin type positional argument in various commands (use `--plugin-type` option instead)

Update your scripts and workflows to use the new syntax before upgrading.

### Console output changes

The default console logger now displays fewer keys to reduce visual clutter. If you rely on specific keys being displayed, you can customize the output format using [custom logging configuration](/guide/logging#configuring-logging).

### Config command argument order

The order of positional arguments for `meltano config` subcommands has changed. The plugin name now comes before the setting name:

```bash
# Old
meltano config set <setting> <plugin_name> <value>

# New
meltano config set <plugin_name> <setting> <value>
```

This change makes the command more intuitive and consistent with other Meltano commands.

### Plugin logger naming

Plugin subprocess loggers have been renamed from `meltano.runner.<plugin_name>` to `meltano.plugins.<stream>.<type>.<name>`, where `<stream>` is either `stdout` or `stderr`. This separates standard output and error streams into distinct loggers.

If you have custom logging configurations that filter on logger names, update them to use the new naming scheme:

```yaml
# Old
loggers:
  meltano.runner.tap-github:
    level: INFO

# New
loggers:
  meltano.plugins.stdout.extractor.tap-github:
    level: INFO
```

### Schedule `start_date` removed

The `start_date` attribute has been removed from schedule definitions in `meltano.yml`. This attribute was unused by Meltano and should be removed from your schedule configurations.

## Platform-dependent log location

Meltano now stores logs in a platform-appropriate location following OS conventions. On macOS, logs are stored in `~/Library/Logs/Meltano`. On Linux, they're in `~/.local/state/meltano/logs`. Use the `meltano logs` command to view job logs easily.

### Auto-lock plugin definitions

Plugin definitions are now automatically locked when you add or update plugins, ensuring reproducible deployments without manual `meltano lock` invocations.

## Migration Checklist

1. Verify you're running Python 3.10 or later
2. Update any custom logging configurations to use new logger names
3. Remove `start_date` from schedule definitions in `meltano.yml`
4. Update scripts using deprecated CLI syntax:
   - Replace `meltano lock --all` with `meltano lock`
   - Replace `meltano install - <plugin>` with `meltano install <plugin>`
   - Replace positional plugin type arguments with `--plugin-type`
5. Update `meltano config` commands to use new argument order
6. If using Docker with PostgreSQL, add explicit `psycopg2-binary` installation
7. Test your pipelines in a development environment before upgrading production

For a complete list of changes, see the [v4.0.0 changelog](https://github.com/meltano/meltano/releases/tag/v4.0.0).
