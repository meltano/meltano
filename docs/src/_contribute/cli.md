---
title: CLI Development
description: Contribute to the Meltano CLI.
layout: doc
weight: 10
hidden: true
---

This section of the guide provides guidance on how to work with the Meltano CLI, which serves as the primary user interface of Meltano,
and is built with the [Python package: click](https://click.palletsprojects.com/en/8.1.x/).

## Getting Set Up

See the prerequisite section for instructions on how to set up a development environment and dependencies.

## CLI Design Guidelines

The `meltano` CLI is the primary interface for interacting with Meltano. It's often the first introduction to meltano
that a users experiences when browsing the docs or experimenting with the CLI. As such, we aim to provide a clear and
consistent interface that is easy to use. This guide aims to codify the design guidelines for the CLI so that
contributors can easily update or extend the CLI with new features, commands, options, and enhancements.

This document is somewhat aspirational and a work in progress. Portions of the CLI may violate the design and style
guidelines, but we aim to update the CLI overtime to ensure that it is as consistent as possible.

### Consistent definition of Groups, Commands, Sub-commands, Arguments, and Options

Groups, Commands, Sub-commands, Arguments, Options, and Flags often have slightly different meanings for users. So are
defined as follows for use in `meltano`.

- Group is a group of commands that are related to a specific area of the CLI, typically a specific meltano feature.
  For example, the `meltano schedule` feature-group contains commands related to managing Meltano schedules.
- command/sub_command are used to perform specific tasks or used to group a set of command around a specific feature
  or task. Sub-commands take the form of parameters, but require additional arguments or options themselves.
- Arguments are positional parameters that are passed to a command. Arguments do not require additional options or
  arguments - otherwise they would be considered a sub-command.
- Options (switch, option flags, or flags) are options that alter the behavior (e.g. `--dry-run/--verbose`) or named
  input options (e.g. `--tasks=`). They come in two forms. A long form: `--option-name`, and a short form: `-o`.

Given a command like `meltano job set JOB_NAME --tasks=[<task>...]`:

- `meltano` is the global click command group for Meltano. This is the main entry point to the CLI. When we refer to global options this is the level we refer to.
- `job` is the click command group for the `job` command. This is the main command group for the `job` command. This is typically the top level for a Meltano feature.
- `set` is a `sub-command` of the `job` command.
- `JOB_NAME` is an `argument` of the `set` sub-command.
- `--tasks` is named `option` of the `set` sub-command.

For a technical explanation of how commands and groups work see https://click.palletsprojects.com/en/8.0.x/commands/

### Use of short and long options

For options you expect to be used frequently or for options with excessively long names, you may include both the long
AND short variation of the option. For example `--help` and `-h`, `--force` and `-f`. However, you should avoid using
the short form if it is ambiguous or is likely to overlap with another option in the same global command group. For
example avoid using `-t` as a short form for `--tasks` as it may be confused with a hypothetical `--test` option.

Note that in documentation like guides and walkthrough the long form is always preferred. The short version alone should
never be used in documentation.


### Desired verb/command linkage and structure

1. Organize in a command group around a feature below the top level where possible.
2. Coalesce commands that operate on the same resource of a feature as a group of sub-commands.
3. Use transitive verbs like `remove`, `set`, `list`, `get` as sub-commands to perform work within a group where appropriate.

```
meltano <feature-group> add <something>
meltano <feature-group> delete <something>
meltano <feature-group> get <something>
```

#### Standardized verbs

- Use `add` and `remove` to create or remove a construct like "schedule" or "job"
- Use `set` to override or update a construct after creation as in `meltano jobs JOB_NAME set`
- Use `get`, `set`, `list`, `clear` for operating on variable like artifacts like "state" and "secrets"
- Use `list` to enumerate items as in `meltano job list`
- Use `describe` to show details about an item


### Global vs argument level flag casing

When creating global flags, default to upper case letters for short options, and lower case letter for argument level
options. Unless a common industry convention already exists to use the lower case variation.

Defaulting global short flags to upper case letters can help prevent ambiguity should a collision between a global flag
and an argument level option occur. e.g.

```
meltano [-L/--log-level LEVEL] SOME_COMMAND [-l/--last-thing]
```

The caveat to this is *common* and *expected* global short options. For example `-h` and `--help`.

### Reusing short options

Avoid reusing a short option if at all possible to avoid potential confusion. An example where short flag should not be
reused:

```
# ambiguous use that should be avoided
meltano somecommand run SOME_TASK [-t/--test SOME_TEST]
meltano somecommand set [-t/--task SOME_TASK]
```

In scenario's like this you have three paths.

1. Choose a sensible alternate when its unlikely to cause confusion with OTHER options e.g. `-k/--task` and `-t/--test`.
2. Dropping the use of the short flag of the option you feel will be used less frequently AND the short flag is unlikely
to cause confusion. This is a great path if the long flag is already terse.
3. Drop the use of the short flag all together. If these flags aren't used frequently, this is a sensible default choice.

### Expected output formats

Default to human-readable plain text output for most commands by default. In cases where you expect users to also want
to programmatically consume the output, you should allow the user to specify the output format via the `--format` option.

The `--format` option should still default to `text` unless the user explicitly specifies a format. The two primary
formats are:

- `text`: human-readable plain text output.
- `json`: JSON output.

In the future we may add support for other formats (e.g. `yaml`).

### Expected help and usage

Feature groups should have fully documented help and usage, that contains at least basic invocation examples. And link
to the CLI documentation for that specific feature group for more details.

```
Usage: meltano job [OPTIONS] COMMAND [ARGS]...

  Manage jobs.

  Example usage:

      # This help
      meltano job --help
      # List all jobs in JSON format
      meltano job list --format json
      # List a named job
      meltano job list [JOB_NAME]

      # Create a new job with a single task representing a single run command.
      meltano job add NAME --tasks 'tap mapper target command:arg1'

      # Create a new job with multiple tasks each representing a run command.
      # The list of tasks must be yaml formatted and consist of a list of strings, list of string lists, or mix of both.
      meltano job add NAME --tasks '["tap mapper target", "tap2 target2", ...]'
      meltano job add NAME --tasks '[["tap target dbt:run", "tap2 target2", ...], ...]'

      # Remove a named job
      meltano job remove NAME

 Read more at https://docs.meltano.com/reference/command-line-interface#jobs

Options:
  --database-uri TEXT  System database URI.
  --help               Show this message and exit.

Commands:
  add     Add a new job with tasks.
  list    List job(s).
  remove  Remove a job.
  set     Update an existing jobs tasks
```

### Help style guidelines

#### Required items

For required items such as commands and arguments, use text without brackets or braces. In the following examples, all
words and arguments are required:

```
meltano run JOB_NAME
meltano invoke PLUGIN_NAME
meltano schedule list
meltano schedule remove SCHEDULE_NAME
```

#### Optional items

Use square brackets around an optional items. If there's more than one optional item, enclose each item in
its own set of square brackets. In the following example the `--log-level` and `--dump` are optional, while PLUGIN_NAME
is required:

```
meltano [--log-level=LEVEL] invoke [--dump=config] PLUGIN_NAME
```

#### Mutually exclusive items

Use curly braces (`{}`) to indicate that the user must choose one—and only one—of the items inside the braces. Use
PIPES (`|`) to separate the items:

```
meltano schedule {list|remove}
```

#### Repeating items

Use three trailing dots and no spaces (`...`) to indicate that the user can specify multiple values for the items:

```
meltano run BLOCKS ...
meltano install [] [PLUGIN_NAME] ...
```

#### Short and Long Options

For official documentation such as walkthroughs and guides use the long form of the flag. For example:

```
meltano --environment=PROD
```

In help output and general examples default to the long form or provide combined examples of the short and long form:

```bash
meltano [-E/--environment ENVIRONMENT]
```

### Placeholders and angle brackets

When writing help output it is often useful to provide examples that utilize placeholders. In complex cases where you're
trying to illustrate how a user might use feature, it is often useful to use actual tap/target/mapping names to illustrate
intent. But most commonly, especially for simple examples use common terms e.g. `TAP` rather than `extractor` or `tap-something`.

We also have significant historic use of angle brackets as placeholders for user input in our documentation (and also
help out). Which often looks like:

```
meltano elt <tap_name> <target_name>
```

In the context of something like a more conversational guide or other online docs this does help indicate that we expect the user to supply this input. However, our current use in help output is often ambigous when it comes to indicating whether this is a required item or optional item. So moving forward if you use this form in CLI help out you should still follow the documented conventions for indicating whether something is required:

```
# TAP and TARGET are upper case since they are required inputs
meltano run <TAP_NAME> <TARGET_NAME>

# MAPPER1 is wrapped in [] since its optional and a series
meltano <TAP> [MAPPER1 ...] <TARGET>
```

### Phrasing guidelines for command Deprecation and Preview commands

Prefer the term "deprecated" over "obsolete". Commands that are deprecated should be marked as such in help text and
in the meltano documentation. Deprecated commands should also explicitly emit a notice when they are used indicating
their deprecation. Where appropriate the notice and help text should indicate the replacement command, or link to
further information. If known, you should also document in what version you expect a command to be fully removed.

Prefer the term "preview" over "beta". Commands that enable a preview feature should be marked as such in help text and
in the meltano documentation. Where possible if not in the help output, then at least in the documentation, you should also
document when the command is expected to graduate from preview status, and what if any shortcomings, defects, or missing
functionality it currently has.
