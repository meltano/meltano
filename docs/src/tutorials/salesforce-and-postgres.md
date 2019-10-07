---
sidebar: auto
---

# Tutorial: Salesforce API + Postgres

This is the Salesforce API and Postgres database tutorial. It guides you through data extraction from your Salesforce account, loading extracted entities to a Postgres DB, transforming the raw data, and analyzing the results.

## Prerequisites

- Meltano's minimum and [optional requirements](/docs/installation.html#requirements) installed
- Docker started

## Initialize Your Project

To get started, navigate to a directory, in your terminal, where you want your Meltano project to be installed and run the following commands:

::: tip Remember
Run `source venv/bin/activate` to leverage the `meltano` installed in your virtual environment (`venv`) if you haven't already.
:::

Initialize a new project with a folder called sfdc-project

```bash
meltano init sfdc-project
```

Change directory into your new sfdc-project project

```bash
cd sfdc-project
```

Start docker postgres instance

```bash
docker-compose up -d warehouse_db
```

Let's see what extractors and loaders are available

```bash
meltano discover all
```

Add tap-salesforce - to `select` which Salesforce entities will be extracted before running the meltano `elt` command and set the credentials for your Salesforce instance

```bash
meltano add extractor tap-salesforce
```

Add target-postgres - to set the credentials for your Postgres DB

```bash
meltano add loader target-postgres
```

## Set Your Credentials

Create a .env file in your project directory (i.e. sfdc-project) with the SFDC and Postgres DB credentials.

**.env**

```
export PG_PASSWORD=warehouse
export PG_USERNAME=warehouse
export PG_ADDRESS=localhost
export PG_PORT=5502
export PG_DATABASE=warehouse

export TAP_SALESFORCE_URL=
export TAP_SALESFORCE_USERNAME=''
export TAP_SALESFORCE_PASSWORD=''
export TAP_SALESFORCE_SECURITY_TOKEN=''
export TAP_SALESFORCE_CLIENT_ID='secret_client_id'

export TAP_SALESFORCE_START_DATE='2019-03-01T00:00:00Z'
```

You can leave `TAP_SALESFORCE_URL` and `TAP_SALESFORCE_CLIENT_ID` as they are in the example above, but you have to set `TAP_SALESFORCE_USERNAME`, `TAP_SALESFORCE_PASSWORD` and `TAP_SALESFORCE_SECURITY_TOKEN` and `TAP_SALESFORCE_START_DATE` according to your instance and preferences.

## Select The Entities to Export from Salesforce

A Salesforce account may have more than 100 different entities. In order to see the list of available entities, please run

```bash
meltano select tap-salesforce --list --all
```

In this tutorial, we are going to work with a couple of the most common ones and show you how to [select](/docs/command-line-interface.html#select) entities to extract from a specific API: Account, Contact, Lead, User, Opportunity and Opportunity History:

```bash
meltano select tap-salesforce "User" "*"
meltano select tap-salesforce "Account" "*"
meltano select tap-salesforce "Lead" "*"
meltano select tap-salesforce "Opportunity" "*"
meltano select tap-salesforce "OpportunityHistory" "*"
meltano select tap-salesforce "Contact" "*"
```

## Run ELT (extract, load, transform)

Run the full Extract > Load > Transform pipeline:

```bash
meltano elt tap-salesforce target-postgres --transform run
```

Depending on your Account, the aforementioned command may take from a couple minutes to a couple hours. That's why we propose to set the `TAP_SALESFORCE_START_DATE` not too far in the past for your first test.

You could also extract and load the data and then run the transformations at a later point (examples below):

Only run the Extract and Load steps:

```bash
meltano elt tap-salesforce target-postgres
```

Only run the Transform Step:

```bash
meltano elt tap-salesforce target-postgres --transform only
```

The transform step uses the dbt [transforms](/docs/transforms.html) defined by [Mavatar's Salesforce dbt package](https://gitlab.com/meltano/dbt-tap-salesforce).
When `meltano elt tap-salesforce target-postgres --transform run` is executed, both default and custom dbt transformations in the transform/ directory (a folder created upon project initilization) are being performed.

In order to visualize the data with existing transformations in the UI, the final step would be to add models:

Add existing models:

```bash
meltano add model model-salesforce
```

### Setup incremental ELT

Per default, Meltano will pull all data in the ELT process. This behavior is perfect to get started because of its simplicity. However, some datasets are too big to query as a whole: the solution is incremental ELT.

Incremental ELT will persist the extraction cursor (named `state`) to make sure any subsequent ELT only pull the data that changed **after** this cursor. This feature is currently implemented by the extractors and is pretty simple to setup in your Meltano project.

:::warning
Support for incremental ELT varies from extractor to extractor.
:::

To enable it, Meltano must know which cursor to use for the ELT, which is set using the `--job_id` parameter on the `meltano elt` command.
Alternatively, one can use the `MELTANO_JOB_ID` environmental variable. For each subsequent `ELT`, Meltano will look for a previous cursor to start from.

The first run will create a cursor state:

```bash
meltano elt --job_id=gitlab tap-gitlab target-postgres
```

Subsequent runs will start from this cursor:

```bash
meltano elt --job_id=gitlab tap-gitlab target-postgres
```

:::warning
Schedules currently only support the `MELTANO_JOB_ID` environment variable, which need to be set manually in the **meltano.yml**.

```yaml
schedules:
  - name: gitlab_postgres
    …
    env:
      MELTANO_JOB_ID=gitlab
```

:::

## Interact with Your Data in The Web App

In order to start the UI, where you can interact with the transformed data, please go back to your terminal and execute the following command:

This will start a local web server at [http://localhost:5000](http://localhost:5000)

```bash
meltano ui
```

When you visit the URL, you will be using the default connection to Meltano's SQLite database. In order to allow the UI to access your postgres DB instance, please follow the steps below:

1. Navigate to the Postgres Loader Configuration (Configuration > Loaders > target-postgres > Configure)
2. Enter connection settings

- Name = `postgres_db` (important to use that name if you are following the tutorial)
- Dialect = `PostgresSQl`
- Host = `localhost`
- Port = `5502`
- Database, Username, Password = `warehouse`
- Schema = `tap_salesforce` (or whatever the namespace of the tap is, by default the name of the tap with underscores instead of `-`s)

3. Click "Save Connection"

You can now query and explore the extracted data:

- Navigate to `Analyze` > `sf opportunity history joined` (under SFDC in the drop-down)
- Toggle Columns and Aggregates buttons to generate the SQL query.
- Click the Run button to query the transformed tables in the `analytics` schema.
- Check the Results or Open the Charts accordion and explore the data.
