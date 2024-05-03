---
title: Deployment in Production
description: Learn how to deploy your ELT pipelines in production.
layout: doc
sidebar_position: 9
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Once you've [set up a Meltano project](/concepts/project) and
[run some pipelines](/guide/integration) on your local machine,
it'll be time to repeat this trick in production!

This page will help you figure out:

1. how to [get your Meltano project onto the production environment](#your-meltano-project),
2. how to [install Meltano](#installing-meltano),
3. how to [install your Meltano project's plugins](#installing-plugins),
4. where to [store your pipeline state and other metadata](#storing-metadata),
5. where to [store your pipeline logs](#storing-logs),
6. how to [manage your environment-specific and sensitive configuration](#managing-configuration), and finally
7. how to [run your pipelines](#running-pipelines).

If you're [containerizing your Meltano project](/guide/containerization),
you can skip steps 1 through 3 and refer primarily to the "Containerized Meltano project" subsections on this page.

## Managed Hosting Options

Would you rather not be responsible for deploying your Meltano project and managing it in production?

[Meltano Cloud](https://meltano.com/cloud) is currently in Public Beta and will enter General Availability in Q3 2023. [Sign up](https://meltano.com/cloud) to receive more information and reduce your self-management burden.

In the mean time, consider running your Meltano pipelines using a managed Airflow service like [Astronomer](https://www.astronomer.io/), [Google Cloud Composer](https://cloud.google.com/composer/), or [Amazon MWAA](https://docs.aws.amazon.com/mwaa).

## Your Meltano project

### Off of your local machine...

Since a Meltano project is just a directory on your filesystem containing
text-based files, you can treat it like any other software development project
and benefit from DataOps best practices such as version control, code review,
and continuous integration and deployment (CI/CD).

As such, getting your Meltano project onto the production environment starts
with getting it off of your local machine, and onto a (self-)hosted Git repository
platform like [GitLab](https://about.gitlab.com) or [GitHub](https://github.com).

By default, your Meltano project comes with a `.gitignore` file to ensure that
environment-specific and potentially sensitive configuration stored inside the
[`.meltano` directory](/concepts/project#meltano-directory) and [`.env` file](/concepts/project#env) is not leaked accidentally. All other files
are recommended to be checked into the repository and shared between all users
and environments that may use the project.

### ... and onto the production environment

Once your Meltano project is in version control, getting it to your production
environment can take various shapes.

In general, we recommend setting up a CI/CD pipeline to run automatically whenever
new changes are pushed to your repository's default branch, that will connect with the
production environment and either directly push the project files, or trigger
some kind of mechanism to pull the latest changes from the repository.

A simpler (temporary?) approach would be to manually connect to the production
environment and pull the repository, right now while you're setting this up,
and/or later whenever changes are made.

### Containerized Meltano project

If you're [containerizing your Meltano project](/guide/containerization),
your project-specific Docker image will already contain all of your project files.

## Installing Meltano

Just like on your local machine, the most straightforward way to install Meltano
onto a production environment is to
[use `pip` to install the `meltano` package from PyPI](/getting-started/installation#local-installation).

If you add `meltano` (or `meltano==<version>`) to your project's `requirements.txt`
file, you can choose to automatically run `pip install -r requirements.txt` on your
production environment whenever your Meltano project is updated to ensure you're always
on the latest (or requested) version.

### Containerized Meltano project

If you're [containerizing your Meltano project](/guide/containerization),
your project-specific Docker image will already contain a Meltano installation
since it's built from the [`meltano/meltano`](https://hub.docker.com/r/meltano/meltano) base image.

## Installing plugins

Whenever you [add a new plugin](/reference/command-line-interface#add) to a Meltano project, it will be
installed into your project's [`.meltano` directory](/concepts/project#meltano-directory) automatically.
However, since this directory is included in your project's `.gitignore` file
by default, you'll need to explicitly run [`meltano install`](/reference/command-line-interface#install)
before any other `meltano` commands whenever you clone or pull an existing Meltano project from version control,
to install (or update) all plugins specified in your [`meltano.yml` project file](/concepts/project#meltano-yml-project-file).

Thus, it is strongly recommended that you automatically run `meltano install` on your
production environment whenever your Meltano project is updated to ensure you're always
using the correct versions of plugins.

### Containerized Meltano project

If you're [containerizing your Meltano project](/guide/containerization),
your project-specific Docker image will already contain all of your project's plugins
since `meltano install` is a step in its build process.

## Storing metadata

Meltano stores various types of metadata in a project-specific
[system database](/concepts/project#system-database), that takes
the shape of a SQLite database stored inside the project at `.meltano/meltano.db`
by default. Like all files stored in the [`.meltano` directory](/concepts/project#meltano-directory)
(which you'll remember is included in your project's `.gitignore` file by default), the system database is
also environment-specific.

While SQLite is great for use during local development and testing since it
requires no external database to be set up, it has various limitations that make
it inappropriate for use in production. Since it's a simple file, it only supports
one concurrent connection, for example.

Thus, it is is strongly recommended that you use a PostgreSQL system database in
production instead. You can configure Meltano to use it using the
[`database_uri` setting](/reference/settings#database-uri).

### Containerized Meltano project

If you're [containerizing your Meltano project](/guide/containerization),
you will _definitely_ want to use an external system database, since changes to
`.meltano/meltano.db` would not be persisted outside the container.

## Storing logs

Meltano stores all output generated by [`meltano run`](/reference/command-line-interface#run) and [`meltano elt`](/reference/command-line-interface#elt) in `.meltano/logs/elt/{state_id}/{run_id}/elt.log`,
where `state_id` refers to the value autogenerated by `run`, provided to `elt` via the `--state_id` flag, or the name of a [scheduled pipeline](/guide/orchestration), and `run_id` is an autogenerated UUID.

If you'd like to store these logs elsewhere, you can symlink the `.meltano/logs` or `.meltano/logs/elt` directory to a location of your choice.

### Containerized Meltano project

If you're [containerizing your Meltano project](/guide/containerization),
these logs will not be persisted outside the container [running your pipelines](#running-pipelines)
unless you exfiltrate them by [mounting a volume](https://docs.docker.com/engine/reference/commandline/run/#mount-volume--v---read-only)
inside the container at `/project/.meltano/logs/elt`.

## Managing configuration

All of your Meltano project's configuration that is _not_ environment-specific
or sensitive should be stored in its [`meltano.yml` project file](/concepts/project#meltano-yml-project-file) and checked into version
control.

Configuration that _is_ environment-specific or sensitive is [most appropriately
managed using environment variables](/guide/configuration#configuring-settings). [Meltano Environments](/concepts/environments) can be used to better manage configuration between different deployment environments. How these can
be best administered will depend on your deployment strategy and destination.

If you'd like to store sensitive configuration in a secrets store, you can
consider using the [`chamber` CLI](https://github.com/segmentio/chamber), which
lets you store secrets in the
[AWS Systems Manager Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html)
that can then be exported as environment variables when
[executing an arbitrary command](https://github.com/segmentio/chamber#exec)
like `meltano`.

### Containerized Meltano project

If you're [containerizing your Meltano project](/guide/containerization),
you will want to manage sensitive configuration using the mechanism provided
by your container runner, e.g.
[Docker Secrets](https://docs.docker.com/engine/swarm/secrets/) or
[Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/).

## Running pipelines

### `meltano run`

If all of the above has been set up correctly, you should now be able to run
a pipeline using [`meltano run`](/reference/command-line-interface#run),
just like you did locally. Congratulations!

You can run the command using any mechanism capable of running executables,
whether that's [`cron`](https://hub.meltano.com/utilities/cron/), [Airflow's `BashOperator`](https://airflow.apache.org/docs/apache-airflow/1.10.14/howto/operator/bash.html),
or any of dozens of other orchestration tools.

### Airflow orchestrator

If you've added Airflow to your Meltano project as an [orchestrator utility](/guide/orchestration),
you can have it automatically run your project's [scheduled pipelines](/guide/orchestration)
by starting [its scheduler](https://airflow.apache.org/docs/apache-airflow/1.10.14/scheduler.html)
using `meltano invoke airflow scheduler`.

Similarly, you can start [its web interface](https://airflow.apache.org/docs/apache-airflow/1.10.14/cli-ref.html#webserver)
using `meltano invoke airflow webserver`.

However, do take into account Airflow's own
[Deployment in Production Best Practices](https://airflow.apache.org/docs/apache-airflow/1.10.14/best-practices.html#deployment-in-production).
Specifically, you will want to configure Airflow to:

- [use the `LocalExecutor`](https://airflow.apache.org/docs/apache-airflow/1.10.14/best-practices.html#multi-node-cluster)
  instead of the `SequentialExecutor` default by setting the `core.executor` setting
  (or `AIRFLOW__CORE__EXECUTOR` environment variable) to `LocalExecutor`:

  <Tabs className="meltano-tabs" queryString="meltano-tabs">
    <TabItem className="meltano-tab-content" value="meltano config" label="meltano config" default>

  ```bash
  meltano config airflow set core.executor LocalExecutor
  ```

    </TabItem>
    <TabItem className="meltano-tab-content" value="env" label="env" default>

  ```bash
  export AIRFLOW__CORE__EXECUTOR=LocalExecutor
  ```

    </TabItem>
  </Tabs>

- [use a PostgreSQL metadata database](https://airflow.apache.org/docs/apache-airflow/1.10.14/best-practices.html#database-backend)
  instead of the SQLite default ([sounds familiar?](#storing-metadata)) by setting the `core.sql_alchemy_conn` setting
  (or `AIRFLOW__CORE__SQL_ALCHEMY_CONN` environment variable) to a [`postgresql://` URI](https://docs.sqlalchemy.org/en/13/core/engines.html#postgresql):

  <Tabs className="meltano-tabs" queryString="meltano-tabs">
    <TabItem className="meltano-tab-content" value="meltano config" label="meltano config" default>

  ```bash
  meltano config airflow set core.sql_alchemy_conn postgresql://<username>:<password>@<host>:<port>/<database>
  ```

    </TabItem>
    <TabItem className="meltano-tab-content" value="env" label="env" default>

  ```bash
  export AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql://<username>:<password>@<host>:<port>/<database>
  ```

    </TabItem>
  </Tabs>

  For this to work, the [`psycopg2` package](https://pypi.org/project/psycopg2/) will
  also need to be installed alongside [`apache-airflow`](https://pypi.org/project/apache-airflow/),
  which you can realize by adding `psycopg2` to `airflow`'s `pip_url` in your [`meltano.yml` project file](/concepts/project#meltano-yml-project-file) (e.g. `pip_url: psycopg2 apache-airflow`)
  and running [`meltano install utility airflow`](/reference/command-line-interface#install).

### Containerized Meltano project

If you're [containerizing your Meltano project](/guide/containerization),
the built image's [entrypoint](https://docs.docker.com/engine/reference/builder/#entrypoint)
will be [the `meltano` command](/reference/command-line-interface),
meaning that you can provide `meltano` subcommands and arguments like `elt ...` and `invoke airflow ...` directly to
[`docker run <image-name> ...`](https://docs.docker.com/engine/reference/commandline/run/)
as trailing arguments.
