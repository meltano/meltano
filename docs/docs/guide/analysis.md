---
title: Analyze Data
description: Learn how to analyze data using Meltano and Superset.
layout: doc
sidebar_position: 7
---

Once you have your data cleaned up and ready for consumption, Meltano lets you easily install and configure best in class open source business intelligence tools like [Superset](https://superset.apache.org/).

With Superset you can connect to [most popular data warehouses](https://superset.apache.org/docs/databases/installing-database-drivers) and build [Charts and Dashboards](https://superset.apache.org/docs/creating-charts-dashboards/creating-your-first-dashboard) to visualize your data.

## Installing Superset

The Superset plugin requires Meltano version 2.0. If you’re on an older version, make sure you update Meltano first.

Change directories so that you are inside your Meltano project,
and then run the following command to add Superset
to your project and make it available to use via `meltano invoke`:

```bash
meltano add utility superset
```

Once you have Meltano running, you likely already have everything you need for Superset as well. If you do run into trouble installing Superset following the instructions below, check out the [OS Dependencies](https://superset.apache.org/docs/installation/installing-superset-from-scratch/#os-dependencies) section in the Superset documentation. Note that the rest of that guide is not relevant if you’re using Meltano to manage your Superset installation, initialization, and configuration.

## Configuring Superset

### Additional Dependencies

Superset does not ship bundled with connectivity to databases, except for SQLite, which is part of the Python standard library.
You’ll need to install the required packages for the database you want to use as your metadata database as well as the packages needed to connect to the databases you want to access through Superset.

You can find the list of supported databases and the appropriate PyPI (pip) packages in the [Supported Databases and Dependencies](https://superset.apache.org/docs/databases/installing-database-drivers/#supported-databases-and-dependencies) section in the Superset documentation.
These can then be added to your Meltano project by configuring a custom `pip_url` for the `superset` utility:

1. Find the `superset` plugin definition in your `meltano.yml` project file

2. Update the `pip_url` property to include the desired additional packages:

```yaml
utilities:
- name: superset
  variant: apache
  pip_url: apache-superset==1.5.0 snowflake-sqlalchemy
```

3. Re-install the plugin:

```bash
meltano install superset
```

### Secret Key

If you’re running Superset for the first time in a new environment, generate a new SECRET_KEY to increase security:

```bash
meltano config set superset SECRET_KEY $(openssl rand -base64 42)
```

### Admin User

Create an admin user to allow you to log into the UI:

```bash
meltano invoke superset:create-admin
# This is equivalent to `superset fab create-admin` in the Superset documentation
```

### Load Examples

Optionally, load some example data to play with:

```bash
meltano invoke superset:load-examples
# This is equivalent to `superset load_examples` in the Superset documentation
```

For more details and a full list of settings, see the [Superset plugin page](https://hub.meltano.com/utilities/superset) on MeltanoHub.

## Starting the Superset UI

Now that Superset is installed you've optionally set custom configurations, let's start the UI:

```bash
meltano invoke superset:ui
```

Superset will start up and by default be available at http://localhost:8088 in your browser and the backend database will be saved in `$MELTANO_PROJECT_ROOT/.meltano/utilities/superset/`.

## Using Superset

Once you have the Superset UI up and running the next steps are:

1. [Connect to your data source](https://superset.apache.org/docs/databases/db-connection-ui)
2. Import datasets from your data source
3. Create [Charts and Dashboards](https://superset.apache.org/docs/creating-charts-dashboards/creating-your-first-dashboard)
4. Explore data with [Superset's SQL Lab](https://superset.apache.org/docs/creating-charts-dashboards/exploring-data)

## Advanced Superset Configurations

For more details on advanced configurations using a [superset_config.py](https://superset.apache.org/docs/installation/configuring-superset) to override Meltano configurations, check out the Superset plugin page on [MeltanoHub](https://hub.meltano.com/utilities/superset#advanced-configuration).
