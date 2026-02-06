---
title: How to use DataHub with Meltano
description: Learn how to use your DataHub and integrate the ingestion of data into it right into your Meltano pipelines.

layout: doc
sidebar_position: 11
---

Meltano supports multiple [utilities](/concepts/plugins#utilities), one of them is the [DataHub utility](https://hub.meltano.com/utilities/datahub). It provides an integration for the metadata platform called DataHub. You can find the reference at both the [utility-datahub level](https://github.com/z3z1ma/files-datahub/tree/main/bundle/utilities/datahub) as well as the [file-bundle-datahub level](https://github.com/z3z1ma/files-datahub).

This guide explains how to use the datahub utility either with a local running instance, or with a remotely running instance. It will explain how to setup the utility, configure datahub sources and how to run ingestions.

We assume you have some familiarity with DataHub and Meltano.

Have your [DataHub GMS](https://datahubproject.io/docs/what/gms/) url and auth token ready for the setup. Or do the local setup described below.

## High-level Overview

The components needed to get DataHub & Meltano to work together are:

- A DataHub GMS (use the local one below or your running instance)
- The DataHub CLI used to ingest metadata & send it to the GMS (installed into the Meltano project using the utility)
- Meltano as infrastructure, linking components together
- One ingestion recipe for each source you want to ingest (a dbt recipe is provided by the DataHub Meltano utility)

## Running a local DataHub

If you're just testing out DataHub & Meltano, you can start a local DataHub GMS.

To get started with the local version, [install datahub](https://datahubproject.io/docs/quickstart) & then run the `datahub docker quickstart` command to launch the docker-compose cluster. After that you're all set up (you don't need to ingest sample data, as suggested by the quickstart prompt.)

By default, the UI will be located at [http://localhost:9002/](http://localhost:9002/).

We provide a [sandbox version of this Meltano setup](https://github.com/sbalnojan/meltano-example-eltm) configured to point to a local DataHub.

The GMS Url for your local version defaults to [http://localhost:8080](http://localhost:8080) unless you change it.

## Installing the Utility

Before installing the utility, take a look at the [DataHub modules](https://datahubproject.io/docs/generated/ingestion/sources/postgres) you will need. DataHub modules are for instance places (called sources) like PostgreSQL or AWS S3 you want to retrieve metadata from.

For this example we choose:

- s3, becasuse we have CSV files hosted in AWS S3
- postgres, because we have data inside a PostgreSQL database
- and dbt, because we use a dbt transformer to build models.

To install the utility you can either define it in the [meltano.yml](/concepts/project#meltanoyml-project-file) file or use the command line to add it. For the command line, use

`meltano add utility datahub[s3,postgres,dbt]`

. This will prepopulate your [meltano.yml](/concepts/project#meltanoyml-project-file) with the plugin as follows:

```
 utilities:
  - name: datahub
    variant: datahub-project[s3,postgres,dbt]
    pip_url: acryl-datahub
    config:
      gms_host:
      gms_auth:
```

Alternatively, you can use this part of the YAML and run

`meltano install`

## Configure the Meltano Utility

Configuring the Utility by setting the GMS endpoint for the datahub CLI running inside the Meltano project. If [DataHubs metadata service authentification](https://datahubproject.io/docs/authentication/introducing-metadata-service-authentication/) is turned off, you just need to configure the gms_host attribute:

```
 utilities:
  - name: datahub
    variant: datahub-project
    pip_url: acryl-datahub[s3,postgres,dbt]
    config:
      gms_host: http://localhost:8080
```

or alternatively run the equivalent CLI command
`meltano config set datahub gms_host http://localhost:8080`

. If you have MSA turned on, you will need an access token, and configure the `gms_auth` attribute as well:

```
 utilities:
  - name: datahub
    variant: datahub-project
    pip_url: acryl-datahub
    config:
      gms_host: http://localhost/gms/api
      gms_auth: myToken
```

Alternatively, run

`meltano config set datahub gms_auth myToken`

## Setting Recipes

You need one so-called [recipe](https://datahubproject.io/docs/metadata-ingestion/#recipes) for each source you want to ingest metadata from. You can browse the catalog there to write your own recipes for all possible sources.

They are written in YAML and stored as `*.dhub.yml` files.

The meltano utility comes with one [preconfigured recipe for dbt](https://github.com/z3z1ma/files-datahub/blob/main/bundle/utilities/datahub/dbt.dhub.yml). You will need to adapt the `platform` parameter inside this recipe.

```
source:
  type: "dbt"
  config:
    # Coordinates
    manifest_path: ${MELTANO_PROJECT_ROOT}/.meltano/transformers/dbt/target/manifest.json
    catalog_path: ${MELTANO_PROJECT_ROOT}/.meltano/transformers/dbt/target/catalog.json
    sources_path: ${MELTANO_PROJECT_ROOT}/.meltano/transformers/dbt/target/sources.json

    # TODO: Change me to the appropriate platform, ie. bigquery, postgres, etc.
    # https://github.com/datahub-project/datahub/blob/master/metadata-service/war/src/main/resources/boot/data_platforms.json
    target_platform: "CHANGE ME"
sink:
  type: datahub-rest
  config:
    server: ${DATAHUB_GMS_HOST}
    token: ${DATAHUB_GMS_TOKEN}
```

The dbt recipe is placed inside the `${MELTANO_PROJECT_ROOT}/utilities/datahub/` but you can place the recipes anywhere.

A sample AWS S3 ingestion recipe looks like this:

```
source:
  type: s3
  config:
    path_specs:
      -
        include: "s3://test/*.csv"

    aws_config:
      aws_access_key_id: XXX
      aws_secret_access_key: XXX
      aws_region: us-east-1
      aws_endpoint_url: http://host.docker.internal:5005 #mock, replace with yours!
    env: "PROD"
    profiling:
      enabled: false
```

A sample PostgreSQL ingestion recipe looks like this:

```
source:
  type: postgres
  config:
    # Coordinates
    host_port: host.docker.internal:5432
    database: demo

    # Credentials
    username: admin
    password: password
```

## Run the ingestion

To run the ingestion, you use the following command:

`meltano invoke datahub ingest -c YOURRECIPE.dhub.yaml`

for example for S3 and PostgreSQL you would call:

`meltano invoke datahub ingest -c s3recipe.dhub.yaml`

and

` meltano invoke datahub ingest -c postgresrecipe.dhub.yaml`

To run the dbt ingestion, you can use the following meltano command:

`meltano invoke datahub :dbt-ingest`

_Note: For the dbt ingestion to work, you need to have run the source freshness command as well as the docs generate command from dbt beforehand. If you haven't yet, run:_

`meltano invoke dbt-postgres:docs-generate` and
` meltano invoke dbt-postgres:freshness`

## More Resources

There's an example repository linked to this How To [Meltano Toy Projects: DataHub & Meltano](https://github.com/sbalnojan/meltano-example-eltm).

Be sure to read the two Readme's inside the file bundle located:

- [Meltano DataHub File Bundle README.md](https://github.com/z3z1ma/files-datahub/tree/main/bundle/utilities/datahub)
- [Meltano DataHub Utility README.md](https://github.com/z3z1ma/files-datahub)
