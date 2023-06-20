---
title: Cloud Command Line
description: Interact with Meltano Cloud projects from the command line.
layout: doc
weight: 5
---

<div class="notification is-info">
  <p><strong>Meltano Cloud is currently in Beta.</strong></p>
  <p>While in Beta, functionality is not guaranteed and subject to change. <br> If you're interested in using Meltano Cloud please join our <a href="https://meltano.com/cloud/">waitlist</a>.</p>
</div>

## `config`

The `config` command provides an interface for managing project configuration and secrets.
The `config` command supports the setting of environment variables via the `env` command group.

### `env`

Values set via this interface will be injected as Environment Variables into tasks run within the associated project.
Once `set`, values cannot be viewed.
If you are unsure of the current value of an env var, use the `set` command to set a known value.

The `list` subcommand provides an interface to see existing set env var keys:

```sh
meltano-cloud config env list --limit 5

TAP_GITHUB_AUTH_TOKEN
TAP_GITHUB_USER_AGENT
```

The `set` subcommand provides an interface to set new, or override existing, env var values.

```sh
meltano-cloud config env set --key TAP_GITHUB_AUTH_TOKEN --value 'my_super_secret_auth_token'
```

The `delete` subcommand provides an interface to delete env vars:

```sh
meltano-cloud config env delete TAP_GITHUB_AUTH_TOKEN
```

### Reserved Variables

See the [reserved variables](/cloud/platform#reserved-variables) docs for more details on variables that are reserved for use by Meltano Cloud.

## `deployment`

The `deployment` command provides an interface for managing [Meltano Cloud deployments](concepts#meltano-cloud-deployments) for your projects.

Create a new deployment interactively:

```sh
meltano-cloud deployment create
```

Create a new deployment non-interactively:

```sh
meltano-cloud deployment create --name 'my-dev-deployment' --environment 'dev' --git-rev 'develop'
```

The above example creates a new deployment named `my-dev-deployment` for the Meltano environment named `dev`, using the `develop` branch of the project's git repository. Note that the Meltano environment name must match what is in `meltano.yml`.

<div class="notification is-info">
  <p>If your deployment is failing you can try running <a href="/reference/command-line-interface#compile">`meltano compile`</a> to confirm that your configuration files are valid.
  Also double check that you have schedules configured, otherwise the deployment will throw and error.</p>
</div>

List deployments:

```sh
$ meltano-cloud deployment list
╭───────────┬──────────┬───────────────┬───────────────────┬────────────────────┬───────────────────────╮
│  Default  │ Name     │ Environment   │ Tracked Git Rev   │ Current Git Hash   │ Last Deployed (UTC)   │
├───────────┼──────────┼───────────────┼───────────────────┼────────────────────┼───────────────────────┤
│           │ prod     │ prod          │ main              │ 0fa3aab            │ 2023-05-30 16:52:44   │
│     X     │ staging  │ staging       │ main              │ a3268dd            │ 2023-05-31 11:14:34   │
│           │ 1234-xyz │ dev           │ feat/1234-xyz     │ d105f18            │ 2023-06-01 03:57:31   │
╰───────────┴──────────┴───────────────┴───────────────────┴────────────────────┴───────────────────────╯
```

Delete a deployment:

```sh
meltano-cloud deployment delete --name 'my-dev-deployment'
```

Use a deployment as the default deployment for other commands:

```sh
meltano-cloud deployment use --name 'my-dev-deployment'
```

Selecting a default deployment can also be done interactively:

```sh
meltano-cloud deployment use
```

Currently Meltano Cloud doesn't automatically sync updates to [schedules](/guide/orchestration#create-a-schedule) stored in your `meltano.yml` file or changes to your tracked branch.
If you've made a change to your schedules configuration or tracked branch and would like them to be re-deployed to Meltano Cloud you can run the following:

```sh
meltano-cloud deployment update --name prod
```

You can then confirm the deployment is on the correct revision of your tracked branch by running the following:

```sh
meltano-cloud deployment list
```

## `docs`

Opens the Meltano Cloud documentation in the system browser.

```sh
meltano-cloud docs
```

## `history`

Display the history of executions for a project.

```sh
$ meltano-cloud history --limit 3
╭──────────────────────────────────┬─────────────────┬──────────────┬─────────────────────┬──────────┬────────────╮
│ Execution ID                     │ Schedule Name   │ Deployment   │ Executed At (UTC)   │ Result   │ Duration   │
├──────────────────────────────────┼─────────────────┼──────────────┼─────────────────────┼──────────┼────────────┤
│ 15e1cbbde6b2424f86c04b237291d652 │ daily           │ sandbox      │ 2023-03-22 00:04:49 │ Success  │ 00:05:08   │
│ ad2b34087e7c4332a1398321552f2a82 │ daily           │ sandbox      │ 2023-03-22 00:03:23 │ Failed   │ 00:10:13   │
│ 695de7b041b445f5a46a7aac1d0879b9 │ daily           │ sandbox      │ 2023-03-21 15:44:55 │ Failed   │ 00:08:09   │
╰──────────────────────────────────┴─────────────────┴──────────────┴─────────────────────┴──────────┴────────────╯

# Display the last 12 hours of executions
$ meltano-cloud history --lookback 12h

# Display the last week of executions
$ meltano-cloud history --lookback 1w

# Display the last hour and a half of executions
$ meltano-cloud history --lookback 1h30m
```

## `login`

Logging into Meltano Cloud via the CLI stores a token locally which is used by the CLI to take actions that require authentication.

Logging in will open a browser tab where you may be asked to authenticate yourself using GitHub.

```sh
# Login to Meltano Cloud
meltano-cloud login
```

## `logout`

Logging out of Meltano Cloud invalidates your login token, and deletes the local copy that was saved when `meltano cloud login` was run.

```sh
# Logout from Meltano Cloud
meltano-cloud logout
```

## `logs`

```sh
# Print logs for an execution
meltano-cloud logs print --execution-id <execution_id>
```

## `project`

The `project` command provides an interface for Meltano Cloud projects.

The `list` subcommand shows all of the projects you have access to, and can use with other commands:

```sh
meltano-cloud project list
╭───────────┬───────────────────────────────┬──────────────────────────────────────────────────────────╮
│  Default  │ Name                          │ Git Repository                                           │
├───────────┼───────────────────────────────┼──────────────────────────────────────────────────────────┤
│           │ Meltano Squared               │ https://github.com/meltano/squared.git                   │
│           │ MDS-in-a-box                  │ https://github.com/aaronsteers/meltano-demo-in-a-box.git │
╰───────────┴───────────────────────────────┴──────────────────────────────────────────────────────────╯
```

When you run the `login` command, if you only have a single project, it will be set as the default project to use for future commands. Otherwise, you will need to run `meltano-cloud project use` to specify which Meltano Cloud project the other `meltano-cloud` commands should operate on.

When `meltano-cloud project use` is not provided any argument, it will list the available projects, and have you select one interactively using the arrow keys. To select a project as the default non-interactively, use the `--name` argument:

```sh
meltano-cloud project use --name 'Meltano Squared'
Set 'Meltano Squared' as the default Meltano Cloud project for future commands
```

```sh
meltano-cloud project list
╭───────────┬───────────────────────────────┬──────────────────────────────────────────────────────────╮
│  Default  │ Name                          │ Git Repository                                           │
├───────────┼───────────────────────────────┼──────────────────────────────────────────────────────────┤
│     X     │ Meltano Squared               │ https://github.com/meltano/squared.git                   │
│           │ MDS-in-a-box                  │ https://github.com/aaronsteers/meltano-demo-in-a-box.git │
╰───────────┴───────────────────────────────┴──────────────────────────────────────────────────────────╯
```

When specifying a project to use as the default for future command, its name must be exactly as shown when running `meltano-cloud project list`. If there are spaces or special characters in the name, then it must be quoted.

## `run`

Run a schedule immediately specifying the schedule name and deployment.

```sh
meltano-cloud run daily --deployment sandbox
Running a Meltano project in Meltano Cloud.
```

The running workload will appear in the `history` within 1-2 minutes.

## `schedule`

Prior to enabling or disabling a schedule, the project that schedule belongs to must be deployed.

Schedules are disabled when initially deployed, and must be enabled using the `enable` command.

Currently, updating a schedule requires a redeployment. In the future it will be possible to update a schedule without a redeployment.

```sh
# Enable a schedule
meltano-cloud schedule enable --deployment <deployment name> --schedule <schedule name>

# Disable a schedule
meltano-cloud schedule disable --deployment <deployment name> --schedule <schedule name>
```

Schedules can be listed using the `list` command:

```sh
meltano-cloud schedule list
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
meltano-cloud schedule list --deployment prod
╭──────────────┬────────────┬──────────────────────┬──────────────┬───────────╮
│ Deployment   │ Schedule   │ Interval             │   Runs / Day │ Enabled   │
├──────────────┼────────────┼──────────────────────┼──────────────┼───────────┤
│ prod         │ schedule_3 │ 0 6 * * *            │          1.0 │ True      │
│ prod         │ schedule_4 │ 15,45 */2 * * 1,3,5  │         10.3 │ False     │
╰──────────────┴────────────┴──────────────────────┴──────────────┴───────────╯
```

Individual schedules can be more thoroughly described using the `describe` command:

```sh
meltano-cloud schedule describe --deployment staging --schedule schedule_4 --num-upcoming 5
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
meltano-cloud schedule describe --deployment staging --schedule schedule_4 --num-upcoming 5 --only-upcoming
2023-03-24 20:45
2023-03-24 22:15
2023-03-24 22:45
2023-03-27 00:15
2023-03-27 00:45
```

If a schedule is disabled, it will never have any upcoming scheduled runs.
