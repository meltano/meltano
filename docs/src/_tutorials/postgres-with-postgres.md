---
title: Meltano Tutorial - Postgres Extractor with Postgres Loader
description: Learn how to use Meltano to load data from postgres, then analyze it without modifying the raw data.
layout: doc
weight: 2
---

This is a tutorial on how to run `tap-postgres` with `target-postgres` in Meltano.

## Intro

`tap-postgres` is not currently officially supported by Meltano, so you have to add it as a custom tap. For more details, check the [documentation on adding a custom extractor](/tutorials/custom-extractor).

## Project Initialization

Let's start by initializing a new Meltano Project and add the supported loader `target-postgres`:

```
meltano init tap-postgres
cd tap-postgres
meltano add loader target-postgres
```

## Adding a Custom Extractor

Next step is to add `tap-postgres` as a [custom extractor](/tutorials/custom-extractor). We'll use the [tap-postgres provided by the Singer.io community](https://github.com/singer-io/tap-postgres/) and fix its version to `0.0.61`, which has been tested and runs without issues with Meltano:

```bash
meltano add --custom extractor tap-postgres

(namespace): tap_postgres
(pip_url): tap-postgres==0.0.61
(executable): tap-postgres
(capabilities): discover,properties,state
(settings): dbname,host,password,port,user
```

We should then update `meltano.yml` and add the configuration parameters this tap needs in order to run:

**meltano.yml**

```yaml
plugins:
  extractors:
  - capabilities:
    - discover
    - properties
    - state
    executable: tap-postgres
    name: tap-postgres
    namespace: tap_postgres
    pip_url: tap-postgres==0.0.61
    settings:
      - name: dbname
        env: TAP_PG_DATABASE
      - name: host
        env: TAP_PG_ADDRESS
      - name: password
        env: TAP_PG_PASSWORD
      - name: port
        env: TAP_PG_PORT
      - name: user
        env: TAP_PG_USERNAME
    config:
      default_replication_method: FULL_TABLE
      include_schemas_in_destination_stream_name: true
  loaders:
 ... ... ...
```

And finally create a .env file in your project directory (i.e. tap-postgres). We are going to add the proper settings for the source and the target databases. The `TAP_PG_*` variables are used by the Tap (i.e. they define the source DB where the data are extracted from), while the `PG_*` variables are used by the Target (i.e. they define the target DB where the data will be loaded at)

**.env**

```bash
export TAP_PG_DATABASE=my_source_db
export TAP_PG_ADDRESS=localhost
export TAP_PG_PORT=5432
export TAP_PG_USERNAME=source_username
export TAP_PG_PASSWORD=source_password

export PG_DATABASE=my_target_db
export PG_PASSWORD=target_password
export PG_USERNAME=target_username
export PG_ADDRESS=localhost
export PG_PORT=5432
```

Let's make sure that everything has been set correctly:

```bash
meltano config tap-postgres

  {'default_replication_method': 'FULL_TABLE', 'include_schemas_in_destination_stream_name': True, 'dbname': 'my_source_db', 'host': 'localhost', 'password': '***', 'port': '5432', 'user': '***'}

meltano config target-postgres

  {'user': '***', 'password': '***', 'host': 'localhost', 'port': '5432', 'dbname': 'my_target_db'}
```

## Filtering out data

This step is required if you don't want to export everything from the source db. You can skip it if you just want to export all tables.

We can use `meltano select` to select which entities will be exported by the Tap from the Source DB. You can find more info on how meltano select works on [the Meltano cli commands Documentation](/reference/command-line-interface#select).

In the case of `tap-postgres`, the names of the Entities (or streams as they are called in the Singer.io Specification) are the same as the table names in the Source DB, prefixed by the DB name and the schema they are defined into: `{DB NAME}-{SCHEMA NAME}-{TABLE NAME}`.

For example, assume that you want to export the `users` table and selected attributes from the `issues` table that reside in the `tap_gitlab` schema in `warehouse` DB. The following `meltano select` commands will only export those two tables and data for the selected attributes:

```bash
meltano select tap-postgres "warehouse-tap_gitlab-users" "*"
meltano select tap-postgres "warehouse-tap_gitlab-issues" "id"
meltano select tap-postgres "warehouse-tap_gitlab-issues" "project_id"
meltano select tap-postgres "warehouse-tap_gitlab-issues" "author_id"
meltano select tap-postgres "warehouse-tap_gitlab-issues" "assignee_id"
meltano select tap-postgres "warehouse-tap_gitlab-issues" "title"
meltano select tap-postgres "warehouse-tap_gitlab-issues" "state"
```

Finally, you can use `meltano select <tap_name> --list` command to make sure that everything has been set correctly:

```bash
meltano select tap-postgres --list

Enabled patterns:
  warehouse-tap_gitlab-issues.title
  warehouse-tap_gitlab-issues.id
  warehouse-tap_gitlab-issues.project_id
  warehouse-tap_gitlab-issues.state
  warehouse-tap_gitlab-issues.assignee_id
  warehouse-tap_gitlab-issues.author_id
  warehouse-tap_gitlab-users.*

Selected attributes:
  [selected ] warehouse-tap_gitlab-issues.title
  [automatic] warehouse-tap_gitlab-issues.id
  [selected ] warehouse-tap_gitlab-issues.assignee_id
  [selected ] warehouse-tap_gitlab-issues.state
  [selected ] warehouse-tap_gitlab-issues.project_id
  [selected ] warehouse-tap_gitlab-issues.author_id
  [automatic] warehouse-tap_gitlab-users.id
  [selected ] warehouse-tap_gitlab-users.username
  [selected ] warehouse-tap_gitlab-users.avatar_url
  [selected ] warehouse-tap_gitlab-users.web_url
  [selected ] warehouse-tap_gitlab-users.name
  [selected ] warehouse-tap_gitlab-users.state
```

### Figuring out the names of the streams

In case you are not sure what the names of the streams are, you can use `meltano invoke` to run `tap-postgres` in isolation and generate a catalog file:

```bash
meltano invoke tap-postgres --discover > .meltano/run/tap-postgres/tap.properties.json
```

You can then check that file and decide which Streams (tables in this case) should be exported and use their `tap_stream_id` property when running `meltano select`.

## Run Meltano ELT

Finally run `meltano elt` to export all the selected Entities and load them to the schema of the target DB defined by the custom tap's namespace (`tap-postgres` in this example)

```bash
meltano elt tap-postgres target-postgres
```
