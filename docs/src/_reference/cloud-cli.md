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
meltano cloud schedule --deployment <deployment name> enable <schedule name>

# Disable a schedule
meltano cloud schedule --deployment <deployment name> disable <schedule name>
```
