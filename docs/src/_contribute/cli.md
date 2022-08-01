---
title: CLI Development
description: Contribute to the Meltano CLI.
layout: doc
weight: 10
---

This section of the guide provides guidance on how to work with the Meltano CLI, which serves as primary UX of Meltano and is built with the [Python package: click](https://click.palletsprojects.com/en/8.1.x/).

## Getting Set Up

See the prerequisite section for instructions on how to set up a development environment and dependencies.

## CLI Design Guidelines

The `meltano` CLI is the primary interface for interacting with Meltano. It's often the first introduction to meltano
that a users when browsing the docs or experimenting with the CLI. As such, we aim to provide a clear and consistent interface that is easy to use.
This guide aims to codify the design guidelines for the CLI so that contributors can easily update or extend
the CLI with new features, commands, options, and enhancements.

This document is somewhat aspirational, and portions of the CLI may violate the design and style guidelines, but we aim to
update the CLI overtime to ensure that it is as consistent as possible.

### Consistent definition of Groups, Commands, Sub-commands, Arguments, and Options

Groups, Commands, Sub-commands, Arguments, Options, and Flags often have slightly different meanings for users. So are
defined as follows for use in `meltano`.

- Group is a group of commands that are related to a specific area of the CLI, typically a specific meltano feature.
  For example, the `meltano schedule` feature group contains commands related to managing Meltano schedules.
- command/sub_command are used to perform a specific tasks or used to group a set of command around a specific feature
  or task. Sub-commands often take the form of parameters, but require additional arguments or options.
- Arguments are positional parameters that are passed to a command. Arguments do not require additional options or
  arguments - otherwise they would be considered a sub-command.
- Options (switch, option flags, or flags) are options that alter the behavior (e.g. `--dry-run/--verbose`) or named
  input options (e.g. `--tasks=`). They come in two forms. A long form: `--option-name`, and a short form: `-o`.

Given a command like `meltano job set <job_name> --tasks=[<task>...]`:

- `meltano` is the global click command group for Meltano. This is the main entry point to the CLI. When we refer to global options this is the level we refer to.
- `job` is the click command group for the `job` command. This is the main command group for the `job` command. This is typically the top level for a Meltano feature.
- `set` is a `sub-command` of the `job` command.
- `<job_name>` is an `argument` of the `set` sub-command.
- `--tasks` is named `option` of the `set` sub-command.

For a technical explanation of how commands and groups work see https://click.palletsprojects.com/en/8.0.x/commands/

### Use of short and long options

The options you expect to be used most frequently should always include both the long AND short variation of the option.
For example `--help` and `-h`, `--tasks` and `-t`, `--force` and `-f`.


### Desired verb/command linkage and structure

1. Organize in a command group around a feature below the top level where possible.
2. Coalesce commands that operate on the same resource of a feature as a group of sub-commands.
3. Use transitive verbs like `delete`, `set`, `list`, `get` as sub-commands perform work within a group where appropriate.

```
meltano <feature-group> add <something>
meltano <feature-group> delete <something>
meltano <feature-group> get <something>
```

### Abbreviations

For excessively long options, especially in cases where not short flag is provided or a commonly used abbreviation is present
you should allow the use of the abbreviation as a documented alias:

```
meltano --env=production
meltano --environment=production
```

### Global vs argument level flag casing

When creating global flags, use upper case letters for short options, and lower case letter for argument level options.
This can further help prevent ambiguity should a collision between a global flag and an argument level option occur. e.g.

```
meltano -L/--log-level <level> some-command -l/--last-thing
```

The caveat to this is *common* and *expected* global short options. For example `-h` and `--help`.

### Reusing short options

You may need to reuse a short option, but you should limit this to a single meaning per command group.
Hypothetical example:

```
# ok to reuse short flag

meltano test -t run-specific-test
meltano invoke somejob -t invoke-some-TASK
```

### Expected output formats

Default to human-readable plain text output for most commands by default. In cases where you expect users to also want
to programmatically consume the output, you should allow the user to specify the output format via the `--format` option.

The `--format` option should still default to `text` unless the user explicitly specifies a format. The two primary
formats are:

- `text`: human-readable plain text output.
- `json`: JSON output.

In the future we may add support for other formats (e.g. `yaml`).

### Expected help and usage

### Help style guidelines

### Phrasing guidelines for command Deprecation and Preview commands

Prefer the term "deprecated" over "obsolete". Commands that are deprecated should be marked as such in help text and
in the meltano documentation. Deprecated commands should also explicitly emit a notice when they are used indicating their deprecation.
Where appropriate the notice and help text should indicate the replacement command, or link to further information.

Prefer the term "preview" over "beta". Commands that enable a preview feature should be marked as such in help text and
in the meltano documentation.
