---
title: Meltano Cloud Command Line
description: Interact with Meltano Cloud projects from the command line.
layout: doc
weight: 6
---

## `login`

Logging into Meltano Cloud via the CLI stores a token locally which is used by the CLI to take actions that require authentication.

Logging in will open a browser tab where you may be asked to authenticate yourself using GitHub.

```sh
# Login to Meltano Cloud
meltano cloud login
```

## `logout`

Logging out of Meltano Cloud invalidates your login token, and deletes the local copy that was saved when `meltano cloud login` was run.

```sh
# Logout from Meltano Cloud
meltano cloud logout
```

## `project`

The `project` command provides an interface for Meltano Cloud projects.

The `list` subcommand shows all of the projects you have access to, and can use with other commands:

```sh
meltano cloud project list
╭───────────┬───────────────────────────────┬──────────────────────────────────────────────────────────╮
│  Default  │ Name                          │ Git Repository                                           │
├───────────┼───────────────────────────────┼──────────────────────────────────────────────────────────┤
│           │ Meltano Squared               │ https://github.com/meltano/squared.git                   │
│           │ MDS-in-a-box                  │ https://github.com/aaronsteers/meltano-demo-in-a-box.git │
╰───────────┴───────────────────────────────┴──────────────────────────────────────────────────────────╯
```

When you run the `login` command, if you only have a single project, it will be set as the default project to use for future commands. Otherwise, you will need to run `meltano cloud project use` to specify which Meltano Cloud project the other `meltano cloud` commands should operate on.

When `meltano cloud project use` is not provided any argument, it will list the available projects, and have you select one interactively using the arrow keys. To select a project as the default non-interactively, use the `--name` argument:

```sh
meltano cloud project use --name 'Meltano Squared'
Set 'Meltano Squared' as the default Meltano Cloud project for future commands
```

```sh
meltano cloud project list
╭───────────┬───────────────────────────────┬──────────────────────────────────────────────────────────╮
│  Default  │ Name                          │ Git Repository                                           │
├───────────┼───────────────────────────────┼──────────────────────────────────────────────────────────┤
│     X     │ Meltano Squared               │ https://github.com/meltano/squared.git                   │
│           │ MDS-in-a-box                  │ https://github.com/aaronsteers/meltano-demo-in-a-box.git │
╰───────────┴───────────────────────────────┴──────────────────────────────────────────────────────────╯
```

When specifying a project to use as the default for future command, its name must be exactly as shown when running `meltano cloud project list`. If there are spaces or special characters in the name, then it must be quoted.

## `history`

Display the history of executions for a project.

```sh
$ meltano cloud history --limit 3
╭──────────────────────────────────┬─────────────────┬──────────────┬─────────────────────┬──────────┬────────────╮
│ Execution ID                     │ Schedule Name   │ Deployment   │ Executed At (UTC)   │ Result   │ Duration   │
├──────────────────────────────────┼─────────────────┼──────────────┼─────────────────────┼──────────┼────────────┤
│ 15e1cbbde6b2424f86c04b237291d652 │ daily           │ sandbox      │ 2023-03-22 00:04:49 │ Success  │ 00:05:08   │
│ ad2b34087e7c4332a1398321552f2a82 │ daily           │ sandbox      │ 2023-03-22 00:03:23 │ Failed   │ 00:10:13   │
│ 695de7b041b445f5a46a7aac1d0879b9 │ daily           │ sandbox      │ 2023-03-21 15:44:55 │ Failed   │ 00:08:09   │
╰──────────────────────────────────┴─────────────────┴──────────────┴─────────────────────┴──────────┴────────────╯

# Display the last 12 hours of executions
$ meltano cloud history --lookback 12h

# Display the last week of executions
$ meltano cloud history --lookback 1w

# Display the last hour and a half of executions
$ meltano cloud history --lookback 1h30m
```

## `logs`

```sh
# Print logs for an execution
meltano cloud logs print --execution-id <execution_id>
```

## `schedule`

Prior to enabling or disabling a schedule, the project that schedule belongs to must be deployed.

Schedules are disabled when initially deployed, and must be enabled using the `enable` command.

Currently, updating a schedule requires a redeployment. In the future it will be possible to update a schedule without a redeployment.

```sh
# Enable a schedule
meltano cloud schedule enable --deployment <deployment name> --schedule <schedule name>

# Disable a schedule
meltano cloud schedule disable --deployment <deployment name> --schedule <schedule name>
```

Schedules can be listed using the `list` command:

```sh
meltano cloud schedule list
╭──────────────┬────────────┬──────────────────────┬──────────────┬───────────╮
│ Deployment   │ Schedule   │ Interval             │   Runs / Day │ Enabled   │
├──────────────┼────────────┼──────────────────────┼──────────────┼───────────┤
│ staging      │ schedule_1 │ 0 6 * * 1,3,5        │        < 1.0 │ False     │
│ staging      │ schedule_2 │ 0 */6 * * *          │          4.0 │ True      │
│ prod         │ schedule_3 │ 0 6 * * *            │          1.0 │ True      │
│ prod         │ schedule_4 │ 15,45 */2 * * 1,3,5  │         10.3 │ False     │
╰──────────────┴────────────┴──────────────────────┴──────────────┴───────────╯
```

```sh
meltano cloud schedule list --deployment prod
╭──────────────┬────────────┬──────────────────────┬──────────────┬───────────╮
│ Deployment   │ Schedule   │ Interval             │   Runs / Day │ Enabled   │
├──────────────┼────────────┼──────────────────────┼──────────────┼───────────┤
│ prod         │ schedule_3 │ 0 6 * * *            │          1.0 │ True      │
│ prod         │ schedule_4 │ 15,45 */2 * * 1,3,5  │         10.3 │ False     │
╰──────────────┴────────────┴──────────────────────┴──────────────┴───────────╯
```

Individual schedules can be more thoroughly described using the `describe` command:

```sh
meltano cloud schedule describe --deployment staging --schedule schedule_4 --num-upcoming 5
Deployment name: prod
Schedule name:   schedule_4
Interval:        15,45 */2 * * 1,3,5
Enabled:         True

Approximate starting date and time (UTC) of next 5 schedule runs:
2023-03-24 20:45
2023-03-24 22:15
2023-03-24 22:45
2023-03-27 00:15
2023-03-27 00:45
```

The `--only-upcoming` option can be used to have the command only output the upcoming scheduled run start dates and times:

```sh
meltano cloud schedule describe --deployment staging --schedule schedule_4 --num-upcoming 5 --only-upcoming
2023-03-24 20:45
2023-03-24 22:15
2023-03-24 22:45
2023-03-27 00:15
2023-03-27 00:45
```

If a schedule is disabled, it will never have any upcoming scheduled runs.
