---
title: Part 4 - Transformations, E(t)LT
description: Part 4 - If you're ready to get started with Meltano and run an EL[T] pipeline with a data source and destination of your choosing, you've come to the right place!
layout: doc
weight: 4
---


Let’s learn by example.

Throughout this tutorial, we’ll walk you through the creation of a end-to-end modern E(t)LT stack.

In the previous parts, we set up a E(t)L pipeline, extracting data from GitHub, transforming it inline, and loading it into a local PostgreSQL database.

In this part, we're going to unleash dbt [(data build tool)](https://www.getdbt.com/) onto our data to transform it into meaningful information.

<div class="notification is-success">
    <p>If you're having trouble throughout this tutorial, you can always head over to the <a href="https://meltano.com/slack">Slack channel</a> to get help.</p>
</div>

## Install and configure the postgres specific dbt transformer
Dbt uses different [adapters](https://docs.getdbt.com/docs/supported-data-platforms) depending on the database/warehouse/platform you use. Meltano transformers match this pattern; in this case our transformer is `dbt-postgres`. As usual, you can use the `meltano add` command to add it to your project.

<div class="termy">

```console
$ meltano add transformer dbt-postgres
2022-09-22T11:32:35.601357Z [info     ] Environment 'dev' is active
Added transformer 'dbt-postgres' to your Meltano project
Variant:        dbt-labs (default)
Repository:     https://github.com/dbt-labs/dbt-core
Documentation:  https://docs.meltano.com/guide/transformation

Adding required file bundle 'files-dbt-postgres' to your Meltano project...
Variant:        meltano (default)
Repository:     https://github.com/meltano/files-dbt-postgres
Documentation:  https://hub.meltano.com/files/files-dbt-postgres

Installing transformer 'dbt-postgres'...
---> 100%
Installing file bundle 'files-dbt-postgres'..
---> 100%
Installed file bundle 'files-dbt-postgres'

Adding 'files-dbt-postgres' files to project...
Created transform/.gitignore (files-dbt-postgres)
Created transform/dbt_project (files-dbt-postgres).yml
Created transform/models/.gitkeep (files-dbt-postgres)
Created transform/profiles/postgres/profiles (files-dbt-postgres).yml

Installed transformer 'dbt-postgres'
Installed 2/2 plugins

To learn more about transformer 'dbt-postgres', visit https://docs.meltano.com/guide/transformation
To learn more about file bundle 'files-dbt-postgres', visit https://hub.meltano.com/files/files-dbt-postgres
```

</div>

<br />
As you can see, this adds both the transformer as well as a "file bundle" to your project. You can verify that this worked by viewing the newly populated directory `transform`.

## Configure dbt
Configure the dbt-postgres transformer to use the same configuration as our target-postgres loader using `meltano config`:

<div class="termy">
```console
$ meltano config dbt-postgres set host localhost
&ensp;&ensp;Transformer 'dbt-postgres' setting 'host' was set in `meltano.yml`: 'localhost'
$ meltano config dbt-postgres set port 5432
&ensp;&ensp;Transformer 'dbt-postgres' setting 'port' was set in `meltano.yml`: 5432
$ meltano config dbt-postgres set user meltano
&ensp;&ensp;Transformer 'dbt-postgres' setting 'user' was set in `meltano.yml`: 'meltano'
$ meltano config dbt-postgres set password password
&ensp;&ensp;Transformer 'dbt-postgres' setting 'password' was set in `.env`: 'password'
$ meltano config dbt-postgres set dbname postgres
&ensp;&ensp;Transformer 'dbt-postgres' setting 'dbname' was set in `meltano.yml`: 'postgres'
$ meltano config dbt-postgres set schema analytics
&ensp;&ensp;Transformer 'dbt-postgres' setting 'schema' was set in `meltano.yml`: 'analytics'
```
</div>

## Add our source data
The E(t)L pipeline run already added our source data into the schema `tap_github` as table `commits`. So let's add that to dbt to work with:

```bash
mkdir transform/models/tap_github
```

Add a file called `source.yml` into this directory with the following content:

```yaml
config-version: 2
version: 2
sources:
  - name: tap_github     # the name we want to reference this source by
    schema: tap_github   # the schema the raw data was loaded into
    tables:
      - name: commits
```

## Add a transformed model
Add a file called `authors.sql` to the folder `transform/models/tap_github` with the following contents:

```sql
{% raw %}
{{
  config(
    materialized='table'
  )
}}


WITH base AS (

  SELECT *
  FROM {{ source('tap_github', 'commits') }}
  
) {% endraw %}

SELECT 
  DISTINCT (commit -> 'author' -> 'name') AS authors 
FROM base
```

This model is configured to creating a table via the `materialized='table'` configuration. The keyword `source` is used in dbt to reference the source we just created. The actual model selects the distinct author names from the commits which are wrapped into a JSON blob.

## Run the transformation process
To create the actual table, we run the dbt model via `meltano invoke dbt-postgres:run`:

<div class="termy">

```console
$ meltano invoke dbt-postgres:run
2022-09-22T12:30:31.842691Z [info     ] Environment 'dev' is active
12:31:01  Running with dbt=1.1.2
12:31:02  Found 1 model, 0 tests, 0 snapshots, 0 analyses, 167 macros, 0 operations, 0 seed files, 1 source, 0 exposures, 0 metrics
12:31:02
12:31:03  Concurrency: 2 threads (target='dev')
12:31:03
12:31:03  1 of 1 START table model analytics.authors ..................................... [RUN]
---> 100%
12:31:03  1 of 1 OK created table model analytics.authors ................................ [SELECT 2 in 0.59s]
12:31:03
12:31:03  Finished running 1 table model in 1.56s.
12:31:03
12:31:03  Completed successfully
12:31:04
12:31:04  Done. PASS=1 WARN=0 ERROR=0 SKIP=0 TOTAL=1
#
```

</div>

You can check the data inside the database. There should now be a table inside the `analytics` schema called `authors` populated with data.

## Run the complete pipeline

To check that everything works together as a pipeline, we clean out once more and run the whole E(t)LT pipeline. Drop the tap_github.commits and the analytics.authors tables, clear the state using `meltano state clear dev:tap-github-to-target-postgres` and run the final pipeline alltogether:

<div class="termy">

```console
$ meltano run tap-github hide-github-mails target-postgres dbt-postgres:run
[warning  ] No state was found, complete import.
 [info     ] INFO Starting sync of repository: sbalnojan/meltano-example-el [...]
[info     ] INFO METRIC: {"type": "timer", "metric": "http_request_duration",[...]
[info     ] INFO METRIC: {"type": "counter", "metric": "record_count", "value": 21 [...]
[info     ] time=2022-09-22 12:42:57 name=target_postgres level=INFO message=Table '"commits"' [...]
[...]
---> 100%
[info     ] Incremental state has been updated at 2022-09-22 12:42:58.260520.
[info     ] Block run completed.           block_type=ExtractLoadBlocks err=None set_number=0 success=True
[info     ] 12:43:19  Running with dbt=1.1.2 cmd_type=command name=dbt-postgres stdio=stderr
[info     ] 12:43:20  Found 1 model, [...]
[info     ] 12:43:20                       cmd_type=command name=dbt-postgres stdio=stderr
[info     ] 12:43:20  Concurrency: 2 threads (target='dev') cmd_type=command name=dbt-postgres stdio=stderr
[info     ] 12:43:20                       cmd_type=command name=dbt-postgres stdio=stderr
[info     ] 12:43:20  1 of 1 START table model analytics.authors ..................................... [RUN] [...]
---> 100%
[info     ] 12:43:21  1 of 1 OK created table model analytics.authors .........[...]
[info     ] 12:43:21                       cmd_type=command name=dbt-postgres stdio=stderr
[info     ] 12:43:21  Finished running 1 table model in 1.34s. cmd_type=command name=dbt-postgres stdio=stderr
[info     ] 12:43:21                       cmd_type=command name=dbt-postgres stdio=stderr
[info     ] 12:43:21  Completed successfully cmd_type=command name=dbt-postgres stdio=stderr
info     ] 12:43:21                       cmd_type=command name=dbt-postgres stdio=stderr
[info     ] 12:43:21  Done. PASS=1 WARN=0 ERROR=0 SKIP=0 TOTAL=1 cmd_type=command name=dbt-postgres stdio=stderr
[info     ] Block run completed.           block_type=InvokerCommand err=None set_number=1 success=True
```

</div>

There we have it, a complete E(t)LT pipeline.

## Next Steps

Next, head over to [Part 5, inside the Getting Started Guide](/getting-started/#next-steps).

<script src="/js/termynal.js"></script>
<script src="/js/termy_custom.js"></script>
