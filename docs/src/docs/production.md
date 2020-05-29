---
metaTitle: How to deploy Meltano to production
description: Learn how to run Meltano pipelines in production
sidebarDepth: 2
---

# Deploying To Production

Once you've [set up a Meltano project](/#meltano-init) and
[run some pipelines](/#integration) on your local machine,
it'll be time to repeat this trick in production!

This page will help you figure out:

1. how to [get your Meltano project onto the production environment](#your-meltano-project),
2. how to [install Meltano](#installing-meltano),
3. how to [install your Meltano project's plugins](#installing-plugins),
4. where to [store your pipeline state and other metadata](#storing-metadata),
5. how to [manage your environment-specific and sensitive configuration](#managing-configuration), and finally
6. how to [run your pipelines](#running-pipelines).

## Your Meltano project

### Off of your local machine...

Since a Meltano project is just a directory on your filesystem containing
text-based files, you can treat it like any other software development project
and benefit from DevOps best practices such as version control, code review,
and continuous integration and delivery.

As such, getting your Meltano project onto the production environment starts
with getting it off of your local machine, and onto a (self-)hosted Git repository
platform like [GitLab](https://about.gitlab.com) or [GitHub](https://github.com).

By default, your Meltano project comes with a `.gitignore` file to ensure that
environment-specific and potentially sensitive configuration stored inside the
`.meltano` directory and `.env` file is not leaked accidentally. All other files
are recommended to be checked into the repository and shared between all users
and environments that may use the project.

### ... and onto the production environment

Once your Meltano project is in version control, getting it to your production
environment can take various shapes.

We recommend setting up a CI/CD pipeline to run automatically whenever
new changes are pushed to the `master` branch, that will connect with the
production environment and either directly push the project files, or trigger
some kind of mechanism to pull the latest changes from the repository.

A simpler (temporary?) approach would be to manually connect to the production
environment and pull the repository, right now while you're setting this up,
and/or later whenever changes are made.

If you're a fan of containers, an alternative approach would be to use a CI/CD
pipeline to build a project-specific Docker image and upload it to a registry.
This image can then be deployed onto a Kubernetes cluster, or used by a local
Docker installation on your production environment.
This direction is being explored in issues
[#2048](https://gitlab.com/meltano/meltano/-/issues/2048) and
[#2014](https://gitlab.com/meltano/meltano/-/issues/2014).

## Installing Meltano

Just like on your local machine, the most straightforward way to install Meltano
onto a production environment is to
[use `pip` to install the `meltano` package from PyPI](/docs/installation.html#local-installation).

If you add `meltano` (or `meltano==<version>`) to your project's `requirements.txt`
file, you can choose to automatically run `pip install -r requirements.txt` on your
production environment whenever the Meltano project is updated to ensure you're always
on the latest (or requested) version.

If you're a fan of containers, you can also choose to
[use the `meltano/meltano` image](/docs/installation.html#installing-on-docker),
whose entrypoint is the `meltano` command, as long as you mount your project at
`/project` whenever you run it or create a container.

An alternative approach would be to use a CI/CD pipeline to build a
project-specific Docker image based on the `meltano/meltano` image,
that would contain both the Meltano project files _and_ the Meltano installation.
This direction is being explored in issues
[#2048](https://gitlab.com/meltano/meltano/-/issues/2048) and
[#2014](https://gitlab.com/meltano/meltano/-/issues/2014).

## Installing plugins

Whenever you [add a new plugin](/#meltano-add) to a Meltano project, it will be
installed into your project's `.meltano` directory automatically.
However, since this directory is included in your project's `.gitignore` file
by default, you'll need to explicitly run [`meltano install`](/docs/command-line-interface.html#install)
before any other `meltano` commands whenever you clone or pull an existing Meltano project from version control,
to install (or update) all plugins specified in `meltano.yml`.

Thus, it is strongly recommended that you automatically run `meltano install` on your
production environment whenever the Meltano project is updated to ensure you're always
using the correct versions of plugins.

If you're a fan of containers, an alternative approach would be to use a CI/CD
pipeline to build a project-specific Docker image with all of the plugins pre-installed.
This direction is being explored in issues
[#2048](https://gitlab.com/meltano/meltano/-/issues/2048) and
[#2014](https://gitlab.com/meltano/meltano/-/issues/2014).

## Storing metadata

Meltano stores pipeline state and other metadata in a project-specific
[system database](/docs/environment-variables.html#system-database), which takes
the shape of a SQLite database stored inside the project at `.meltano/meltano.db`
by default. Like all files stored in the `.meltano` directory (which you'll remember
is included in your project's `.gitignore` file by default), the system database is
also environment-specific.

While SQLite is great for use during local development and testing since it
requires no external database to be set up, it has various limitations that make
it inappropriate for use in production. Since it's a simple file, it only supports
one concurrent connection, for example.

Thus, it is is strongly recommended that you use a PostgreSQL system database in
production instead. You can configure Meltano to use it by setting the
`MELTANO_DATABASE_URI` environment variable to a
[`postgresql://` URI](https://docs.sqlalchemy.org/en/13/core/engines.html#postgresql),
or by passing it to the `meltano` command in the `--database-uri` option.

If you're a fan of containers and are planning to use a CI/CD pipeline to build
a project-specific Docker image containing all of the Meltano project files
including the `.meltano` directory, you will _definitely_ want to use an external
system database, since changes to `.meltano/meltano.db` would not be persisted
outside the container.
This direction is being explored in issues
[#2048](https://gitlab.com/meltano/meltano/-/issues/2048) and
[#2014](https://gitlab.com/meltano/meltano/-/issues/2014).

## Managing configuration

All of your Meltano project's configuration that is _not_ environment-specific
or sensitive should be stored in its `meltano.yml` file and checked into version
control.

Configuration that _is_ environment-specific or sensitive is [most appropriately
stored using environment variables](https://12factor.net/config). How these can
be best administered will depend on your deployment strategy and destination.

If you'd like to store sensitive configuration in a secrets store, you can
consider using the [`chamber` CLI](https://github.com/segmentio/chamber), which
lets you store secrets in the
[AWS Systems Manager Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html)
that can then be exported as environment variables when
[executing an arbitrary command](https://github.com/segmentio/chamber#exec)
like `meltano`.

## Running pipelines

### `meltano elt`

If all of the above has been set up correctly, you should now be able to run
a pipeline using [`meltano elt`](/docs/command-line-interface.html#elt),
just like you did locally. Congratulations!

You can run the command using any mechanism capable of running executables,
whether that's `cron`, [Airflow's `BashOperator`](https://airflow.apache.org/docs/stable/howto/operator/bash.html),
or any of dozens of other orchestration tools.

### Airflow orchestrator

If you've added Airflow to your Meltano project as an [orchestrator](/#orchestration),
you can have it automatically run your project's [scheduled pipelines](/#orchestration)
by starting [its scheduler](https://airflow.apache.org/docs/stable/cli-ref.html#scheduler)
using `meltano invoke airflow scheduler`.

Similarly, you can start [its web interface](https://airflow.apache.org/docs/stable/cli-ref.html#webserver)
using `meltano invoke airflow webserver`.

However, do take into account Airflow's own 
[Best Practices on Deployment in Production](https://airflow.apache.org/docs/stable/best-practices.html#deployment-in-production). Specifically, you will want to configure Airflow to:

- [use a PostgreSQL (or MySQL) metadata database](https://airflow.apache.org/docs/stable/best-practices.html#database-backend)
  instead of the SQLite default ([sounds familiar?](#storing-metadata)) by
  setting the `AIRFLOW__CORE__SQL_ALCHEMY_CONN` environment variable to a
  [`postgresql://` URI](https://docs.sqlalchemy.org/en/13/core/engines.html#postgresql)
  (or [`mysql://` URI](https://docs.sqlalchemy.org/en/13/core/engines.html#mysql)),
  and to
- [use the `LocalExecutor`](https://airflow.apache.org/docs/stable/best-practices.html#multi-node-cluster)
  instead of the `SequentialExecutor` default by setting the `AIRFLOW__CORE__EXECUTOR`
  environment variable to `LocalExecutor`.