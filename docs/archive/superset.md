# Using Superset with Meltano

Follow the directions below to use [Apache Superset](https://superset.incubator.apache.org/index.html) with Meltano's ELT runtime and data warehouse capabilities. The directions are grouped into three areas:

1. Meltano Setup
1. Superset Setup
1. Superset with Meltano

## Meltano Setup

### With Docker

- Follow the [Meltano installation instructions](/docs/#introduction)
    - exclude the last `meltano www` command

### Without Docker
- Coming soon

## Superset Setup

Follow the [Superset Installation & Configuration](https://superset.incubator.apache.org/installation.html#installation-configuration) directions taking special note of the below installation dependencies.

1. installation dependencies
    - `python3`
        - `pip3`
        - `pyvenv`
        - `setuptools`
    - [`cryptography` python library](https://superset.incubator.apache.org/installation.html#os-dependencies)
1. [install and initialize Superset](https://superset.incubator.apache.org/installation.html#superset-installation-and-initialization)
    - exclude the `superset load_examples` command
    - take note of the credentials you create as you'll need them to sign in during the next step
1. view Superset in the browser at [http://localhost:8088/](http://localhost:8088/) and sign in

## Superset with Meltano

1. Ensure you followed the above [Meltano Setup](#meltano-setup) and [Superset Setup](#superset-setup) directions before proceeding
1. Navigate to Sources -> Databases and click "Add a new record"
1. Name the database and then in the *SQLAlchemy URI* textfield enter `postgresql+psycopg2://warehouse:warehouse@localhost:5502/warehouse` before clicking "Save"
    - These settings source from [`docker-compose.yml`](https://gitlab.com/meltano/meltano/blob/master/docker-compose.yml)
    - You can first click "Test Connection" to ensure Superset can connect to the data warehouse
1. Navigate to Sources -> Tables and click "Add a new record", enter the settings below, and then click "Save"
    - Database: Pick the database you named in the previous step
    - Schema: `gitlab`
    - Table Name: `region`
        - You can navigate to the SQL Lab page to explore table names
1. Click on the table link (gitlab.region) of your recently created table to see the default `count(*)` metric in action

From here you can further customize database connections, queries, filters, and other settings.