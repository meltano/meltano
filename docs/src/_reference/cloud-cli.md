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
