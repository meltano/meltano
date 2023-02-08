---
title: Part 2 - Loading Data, EL
description: Part 2 - If you're ready to get started with Meltano and run an EL[T] pipeline with a data source and destination of your choosing, you've come to the right place!
layout: doc
weight: 4
---


Let’s learn by example.

Throughout this tutorial, we’ll walk you through the creation of a end-to-end modern ELT stack.

In  [part 1](/getting-started/part1), we extracted data from GitHub and are now ready to load the data into a PostgreSQL database.

<div class="notification is-success">
    <p>If you're having trouble throughout this tutorial, you can always head over to the <a href="https://meltano.com/slack">Slack channel</a> to get help.</p>
</div>

## Getting your target ready
We're going to load our data into a dockerized PostgreSQL database running on your laptop. View the [docker docs](https://docs.docker.com/get-docker/) if you don't yet have docker installed. To launch a local PostgreSQL container, you just need to run:

```bash
$ docker run -p 5432:5432 -e POSTGRES_USER=meltano -e POSTGRES_PASSWORD=password -d postgres
```
<br />
<div class="termy">

```bash
$ docker run -p 5432:5432 -e POSTGRES_USER=meltano -e POSTGRES_PASSWORD=password --name meltano_postgres -d postgres

504e2b416874dd6a5db3fe6dd3ff63f1d42095bbc4e87314f1f708f69c8188de
$ docker container ls
    CONTAINER ID   IMAGE      COMMAND                  CREATED         STATUS         PORTS                    NAMES
    504e2b416874   postgres   "docker-entrypoint.s…"   3 seconds ago   Up 3 seconds   0.0.0.0:5432->5432/tcp   kind_rosalind
```
</div>
<br />
The container will need a few seconds to initialize. You can test the connection with your favorite SQL tool using connection data:
- host: localhost
- port: 5432
- database: postgres
- user: meltano
- password: password

## Add the postgres loader
Add the postgres loader using the `meltano add loader target-postgres --variant=meltanolabs` command.

<div class="termy">

```console
$ meltano add loader target-postgres --variant=meltanolabs
Added loader 'target-postgres' to your Meltano project
Variant:        meltanolabs (default)
Repository:     https://github.com/MeltanoLabs/target-postgres
Documentation:  https://hub.meltano.com/loaders/target-postgres--meltanolabs

Installing loader 'target-postgres'...
---> 100%

Installed loader 'target-postgres'

To learn more about loader 'target-postgres', visit https://hub.meltano.com/loaders/target-postgres--meltanolabs
```
</div>
<br />

Use the ```meltano invoke target-postgres --help``` command to test that the installation worked.
<div class="termy">

```console
$ meltano invoke target-postgres --help
usage: target-postgres [-h] [-c CONFIG]

optional arguments:
-h, --help            show this help message and exit
-c CONFIG, --config CONFIG Config file
```
</div>

## Configure the target-postgres loader
To configure the plugin, look at the options by running ```meltano config target-postgres list```:


<div class="termy">

```console
$ meltano config target-postgres list

[...]
host [env: TARGET_POSTGRES_HOST] current value: 'postgres' (from `meltano.yml`)
&ensp;&ensp;Host: Hostname for postgres instance. Note if sqlalchemy_url is set this will be ignored.
port [env: TARGET_POSTGRES_PORT] current value: None (default)
&ensp;&ensp;Port: The port on which postgres is awaiting connection. Note if sqlalchemy_url is set this will be ignored. Defaults to 5432
user [env: TARGET_POSTGRES_USER] current value: 'meltano' (from `meltano.yml`)
 &ensp;&ensp;User: User name used to authenticate. Note if sqlalchemy_url is set this will be ignored.
password [env: TARGET_POSTGRES_PASSWORD] current value: None (default)
&ensp;&ensp;Password: Password used to authenticate. Note if sqlalchemy_url is set this will be ignored.
database [env: TARGET_POSTGRES_DATABASE] current value: 'postgres' (from `meltano.yml`)
&ensp;&ensp;Database: Database name. Note if sqlalchemy_url is set this will be ignored.
[...]
add_metadata_columns [env: TARGET_POSTGRES_ADD_METADATA_COLUMNS] current value: False (default)
&ensp;&ensp;Add Metadata Columns: Useful if you want to load multiple streams from one tap to multiple Postgres schemas.
[...]

To learn more about loader 'target-postgres' and its settings, visit https://hub.meltano.com/loaders/target-postgres
```
</div>
<br />
Fill in the details for these four attributes, and set add_metadata_columns to True by using the `meltano config target-postgres set ATTRIBUTE VALUE` command:

 <div class="termy">

```console
$ meltano config target-postgres set user meltano
&ensp;&ensp;Loader 'target-postgres' setting 'user' was set in `meltano.yml`: 'meltano'
$ meltano config target-postgres set password password
&ensp;&ensp;Loader 'target-postgres' setting 'password' was set in `.env`: 'password'
$ meltano config target-postgres set database postgres
&ensp;&ensp;Loader 'target-postgres' setting 'dbname' was set in `meltano.yml`: 'postgres'
$ meltano config target-postgres set add_metadata_columns True
&ensp;&ensp;Loader 'target-postgres' setting 'add_metadata_columns' was set in `meltano.yml`: True
$ meltano config target-postgres set host localhost
&ensp;&ensp;Loader 'target-postgres' setting 'host' was set in `meltano.yml`: localhost
```
</div>
<br />
This will add the non-sensitive configuration to your [`meltano.yml` project file](/concepts/project#plugin-configuration):

   ```yml
   plugins:
     loaders:
       - name: target-postgres
         variant: meltanolabs
         pip_url: git+https://github.com/MeltanoLabs/target-postgres.git
         config:
           user: meltano
           database: postgres
           add_metadata_columns: true
           host: localhost
   ```

Sensitive configuration information (such as `password`) will instead be stored in your project's [`.env` file](/concepts/project#env) so that it will not be checked into version control.

You can use `meltano config target-postgres` to check the configuration, including the default settings not visible in the project file.
 <div class="termy">

```console
$ meltano config target-postgres
{
&ensp;&ensp;&ensp;&ensp;"host": "postgres",
&ensp;&ensp;&ensp;&ensp;"user": "meltano",
&ensp;&ensp;&ensp;&ensp;"database": "postgres",
&ensp;&ensp;&ensp;&ensp;"add_metadata_columns": "True"
}
```
</div>

## Run your data integration (EL) pipeline

Now that [your Meltano project](#create-your-meltano-project), [extractor](#add-an-extractor-to-pull-data-from-a-source), and [loader](#add-a-loader-to-send-data-to-a-destination) are all set up, it's time to run your first data integration (EL) pipeline!

Run your newly added extractor and loader in a pipeline using [`meltano run`](/reference/command-line-interface#run):

<div class="termy">

```console
$ meltano run tap-github target-postgres
2022-09-20T13:16:13.885045Z [warning  ] No state was found, complete import.
2022-09-20T13:16:15.441183Z [info     ] INFO Starting sync of repository: [...]
2022-09-20T13:16:15.901789Z [info     ] INFO METRIC: {"type": "timer", "metric": "http_request_duration",[...]
---> 100%
2022-09-20T13:16:15.933874Z [info     ] INFO METRIC: {"type": "counter", "metric": "record_count", "value": 21,[...]
2022-09-20T13:16:16.435885Z [info     ] [...] message=Schema 'tap_github' does not exist. Creating... ...
2022-09-20T13:16:16.632945Z [info     ] ... message=Table '"commits"' does not exist. Creating...
2022-09-20T13:16:16.729076Z [info     ] ...message=Loading 21 rows into 'tap_github."commits"' ...
---> 100%
2022-09-20T13:16:16.864812Z [info     ] ...Loading into tap_github."commits": {"inserts": 21, "updates": 0, "size_bytes": 4641} ...
2022-09-20T13:16:16.885846Z [info     ] Incremental state has been updated at 2022-09-20 13:16:16.885259.
2022-09-20T13:16:16.960093Z [info     ] Block run completed.           ....
```
</div>
<br />
If everything was configured correctly, you should now see your data flow from your source into your destination!

## Next Steps

Next, head over to [Part 3, to add inline transformations to your ingestion process](/getting-started/part3).

<script src="/js/termynal.js"></script>
<script src="/js/termy_custom.js"></script>
