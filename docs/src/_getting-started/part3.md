---
title: Part 3 - Transformations, ELT
description: Part 3 - If you're ready to get started with Meltano and run an EL[T] pipeline with a data source and destination of your choosing, you've come to the right place!
layout: doc
weight: 4
---


Let’s learn by example.

Throughout this tutorial, we’ll walk you through the creation of a end-to-end modern ELT stack.

In parts [1](/getting-started/part1) & [2](/getting-started/part2), we extracted data from GitHub and loaded it into a (local) PostgreSQL database. Now it is time to have more fun. We decide to load all attributes from the data we selected previously, and then build a model listing the different authors of commits to our repository.

That means, in this part we're going to unleash dbt [(data build tool)](https://www.getdbt.com/) onto our data to transform it into meaningful information. Don't worry, you don't need to know anything about dbt, this tutorial is self-contained. You do not need to install dbt yourself, it works as a Meltano plugin.

<div class="notification is-success">
    <p>If you're having trouble throughout this tutorial, you can always head over to the <a href="https://meltano.com/slack">Slack channel</a> to get help.</p>
</div>

## Select more source data
To get all the data from the GitHub commits, you can use the `meltano select` command:

```bash
meltano select tap-github commits "*"
```

This will add the following line to your project file:
```yaml
      extractors:
      - name: tap-github
        select:
        - commits.url # <== technically not necessary anymore, but no need to delete
        - commits.sha # <== technically not necessary anymore, but no need to delete
        - commits.* # <== new data.
```

You can test that the new data is extracted by using `meltano invoke`:

<div class="termy">
```console
$ meltano invoke tap-github
2022-09-22T07:36:52.985090Z [info     ] Environment 'dev' is active
{"type": "STATE", "value":  [...]}
INFO Starting sync of repository: sbalnojan/meltano-example-el
---> 100%
{"type": "SCHEMA", "stream": "commits", [...]

INFO METRIC: {"type": "timer", "metric":  [...]

{"type": "RECORD", "stream": "commits", "record": {"sha": "c771a832720c0f87b3ce53ac12bdcbf742df4e3d", "commit": {"author": {"name": "Horst", "email":
[...]
"sbalnojan/meltano-example-el"}, "time_extracted": "2022-09-22T07:37:06.289545Z"}

...[many more records]...

{"type": "STATE", "value": {"bookmarks": {"sbalnojan/meltano-example-el": {"commits": {"since": "2022-09-22T07:37:06.289545Z"}}}}}
´´´
</div>

Next, we add the dbt plugin to transform this data.

## Install and configure the postgres specific dbt transformer
dbt uses different [adapters](https://docs.getdbt.com/docs/supported-data-platforms) depending on the database/warehouse/platform you use. Meltano transformers match this pattern; in this case our transformer is `dbt-postgres`. As usual, you can use the `meltano add` command to add it to your project.

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
As you can see, this adds both the transformer as well as a [file bundle](/concepts/plugins#file-bundles) to your project. You can verify that this worked by viewing the newly populated directory `transform`.

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

## Add our source data to dbt
The EL pipeline run already added our source data into the schema `tap_github` as table `commits`. dbt will need to know where to locate this data. Let's add that to our dbt project:

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

Now we're able to reference the table using the keyword "source" as you can see next.

## Add a transformed model
Add a file called `authors.sql` to the folder `transform/models/tap_github` with the following contents:

```sql
{% raw %}
{{
  config(
    materialized='table'
  )
}}


with base as (select *
from {{ source('tap_github', 'commits') }}) {% endraw %}

select distinct (commit -> 'author' -> 'name') as authors from base
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

You can check the data inside the database using your favourite SQL editor. There should now be a table inside the `analytics` schema called `authors` populated with data.

## Run the complete pipeline

To check that everything works together as a pipeline, we clean out once more and run the whole ELT pipeline. Drop the tap_github.commits and the analytics.authors tables by running

```bash
docker exec meltano_postgres psql -U meltano -c 'DROP TABLE tap_github.commits; DROP TABLE analytics.authors;'
```

Run the final pipeline alltogether using the parameter `--full-refresh` to ignore the stored state:

<div class="termy">

```console
$ meltano run --full-refresh tap-github target-postgres dbt-postgres:run
[warning  ] Performing full refresh, ignoring state left behind by any previous runs.

 [info     ] INFO Starting sync of repository: sbalnojan/meltano-example-el
 <font color="red">[...]</font>
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

There we have it, a complete ELT pipeline.

## Next Steps

Next, head over to [Part 4, Data Mappings](/getting-started/part4).

<script src="/js/termynal.js"></script>
<script src="/js/termy_custom.js"></script>
