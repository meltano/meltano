---
sidebarDepth: 1
---

# Advanced Tutorials

Now that you know how to create a new project, we recommend checking out our [Carbon Emissions tutorial](/docs/tutorial.html#starter-carbon-emissions) to explore what Meltano is capable of. If you are feeling more adventurous, feel free to skip it and move on!

<TutorialTable />

## Starter - Carbon Emissions

This is the [Carbon Intensity API](https://carbon-intensity.github.io/api-definitions/) (carbon emissions/footprint) and SQLite tutorial. This datasource was chosen as it is public, free, and does not require credentials to access. It guides you through data extraction from the Carbon Intensity API, loading extracted entities to a SQLite database, and analyzing the results.

:::tip
This tutorial is perfect if your goal is to get Meltano up and running as quickly as possible.
:::

### Prerequisites

- Meltano's [minimum requirements](./installation.html#requirements) installed

### Initialize Your Project

Navigate to the directory in your terminal where you want your Meltano project to be installed. Then run the following commands:

::: tip Remember
Run `source venv/bin/activate` to leverage the `meltano` installed in your virtual environment (`venv`) if you haven't already.
:::

Initialize a new project with a folder called carbon:

```bash
meltano init carbon
```

Change directory into your new carbon project:
```bash
cd carbon
```

Let's see what extractors and loaders are available
```bash
meltano discover all
```

Run the extractor (tap) and loader (target)
```bash
meltano elt tap-carbon-intensity target-sqlite
```

Ensure Meltano UI will know how to use data from ELT:
```bash
meltano add model model-carbon-intensity-sqlite
```

Congratulations! You have just extracted all the data from the Carbon Intensity API and loaded it into your local SQLite database.

:::tip
Meltano extracts data from various sources like Salesforce, Zendesk, and Google Analytics and then loads that data into the database of your choice. You can use community extractors and loaders or write your own too.

Meltano's ELT pipeline empowers you to aggregate data from various sources and then gather insights from them using Meltano UI with its automatic SQL generation.
:::

### Analyze with Meltano UI

Now that your data is extracted and loaded, it is ready to be analyzed. Time to start up the web app! Go back into your terminal and run the following command:

```bash
meltano ui
```

This will start a local web server at [http://localhost:5000](http://localhost:5000).

When you visit the URL, you should see:

![Meltano UI with Carbon API initial loading screen](/screenshots/meltano-ui-carbon-tutorial-output.png)

:::warning Troubleshooting
Having issues with Meltano? Help us help you. Here is a [pre-baked form to streamline us doing so](https://gitlab.com/meltano/meltano/issues/new?issue%5Bassignee_id%5D=&issue%5Bmilestone_id%5D=&issuable_template=bugs).
:::

---
#### Analyze

With Meltano UI up and running, we can automatically generate queries with as little as a single click and then explore the query results:

- In the top navigation, hover over `Analyze` and click on **Region**
- Under the `Region` section on the left navigation:
  - Toggle *at least one* aggregate button to generate SQL
  - Toggle any number of column buttons to generate SQL
  - Click the **Run Query** button in the upper right to query using the generated SQL
- Open the Charts accordion to visualize the data!

![Screenshot of Meltano UI with Carbon API charts](/screenshots/carbon-ui-charts.png)

## Intermediate - Salesforce

This is the Salesforce API and Postgres database tutorial. It guides you through data extraction from your Salesforce account, loading extracted entities to a Postgres DB, transforming the raw data, and analyzing the results.

### Prerequisites

- Meltano's minimum and [optional requirements](./installation.html#requirements) installed
- Docker started

### Initialize Your Project

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

### Set Your Credentials
Update the .env file in your project directory (i.e. sfdc-project) with the SFDC and Postgres DB credentials.

```
FLASK_ENV=development

PG_PASSWORD=warehouse
PG_USERNAME=warehouse
PG_ADDRESS=localhost
PG_SCHEMA=analytics
PG_PORT=5502
PG_DATABASE=warehouse

SFDC_URL=
SFDC_USERNAME=''
SFDC_PASSWORD=''
SFDC_SECURITY_TOKEN=''
SFDC_CLIENT_ID='secret_client_id'

SFDC_START_DATE='2019-03-01T00:00:00Z'
```

You can leave `SFDC_URL` and `SFDC_CLIENT_ID` as they are in the example above, but you have to set `SFDC_USERNAME`, `SFDC_PASSWORD` and `SFDC_SECURITY_TOKEN` and `SFDC_START_DATE` according to your instance and preferences.

### Select The Entities to Export from Salesforce

A Salesforce account may have more than 100 different entities. In order to see the list of available entities, please run

```bash
meltano select tap-salesforce --list --all
```

In this tutorial, we are going to work with a couple of the most common ones and show you how to [select](/docs/meltano-cli.html#select) entities to extract from a specific API: Account, Contact, Lead, User, Opportunity and Opportunity History:

```bash
meltano select tap-salesforce "User" "*"
meltano select tap-salesforce "Account" "*"
meltano select tap-salesforce "Lead" "*"
meltano select tap-salesforce "Opportunity" "*"
meltano select tap-salesforce "OpportunityHistory" "*"
meltano select tap-salesforce "Contact" "*"
```

### Run ELT (extract, load, transform)

Run the full Extract > Load > Transform pipeline:

```bash
meltano elt tap-salesforce target-postgres --transform run
```

Depending on your Account, the aforementioned command may take from a couple minutes to a couple hours. That's why we propose to set the `SFDC_START_DATE` not too far in the past for your first test.

You could also extract and load the data and then run the transformations at a later point (examples below):

Only run the Extract and Load steps:
```bash
meltano elt tap-salesforce target-postgres
```

Only run the Transform Step:
```bash
meltano elt tap-salesforce target-postgres --transform only
```

The transform step uses the dbt [transforms](/docs/meltano-cli.html#transforms) defined by [Mavatar's Salesforce dbt package](https://gitlab.com/meltano/dbt-tap-salesforce).
When `meltano elt tap-salesforce target-postgres --transform run` is executed, both default and custom dbt transformations in the transform/ directory (a folder created upon project initilization) are being performed.

In order to visualize the data with existing transformations in the UI, the final step would be to add models:

Add existing models:
```bash 
meltano add model model-salesforce
```

#### Setup incremental ELT

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

### Interact with Your Data in The Web App

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
  - Schema = `analytics`
3. Click "Save Connection"

You can now query and explore the extracted data:

- Navigate to `Analyze` > `sf opportunity history joined` (under SFDC in the drop-down)
- Toggle Columns and Aggregates buttons to generate the SQL query.
- Click the Run button to query the transformed tables in the `analytics` schema.
- Check the Results or Open the Charts accordion and explore the data.

## Intermediate - GitLab

The GitLab API and Postgres database tutorial guides you through data extraction from your GitLab account, loading extracted entities to a Postgres DB, transforming the raw data, and analyzing the results. [Check it out here](/docs/tutorials/tap-gitlab.html).

## Advanced - Create a Custom Extractor

As much as we'd like to support all the data sources out there, we'll need your help to get there. If you find a data source that Meltano doesn't support right now, it might be time to get your hands dirty.

We aim to make Meltano as thin as possible on top of the components it abstracts, so adding a new plugin should be straightforward.

### How to Create a Extractor

First things first, you'll need a data source to integrate: in this example, let's say we want to create a tap to fetch data from `GitLab`.

::: warning Heads-up!
If you are looking to integrate GitLab's data into your warehouse, please use tap official [https://gitlab.com/meltano/tap-gitlab](tap-gitlab).
:::

### Create the Plugin's Package

Meltano uses [Singer](https://singer.io) taps and targets to extract and load data. For more details about the Singer specification, please visit [https://github.com/singer-io/getting-started](https://github.com/singer-io/getting-started)

::: tip
[cookiecutter](https://cookiecutter.readthedocs.io/en/latest/) is a python tool to scaffold projects quickly from an existing template.
:::

```bash
pip install cookiecutter
cookiecutter gh:singer-io/singer-tap-template
> project_name: tap-gitlab-custom
```

### Add the Plugin to Your Meltano Project (--custom)

Now that your plugin is part of your Meltano project, you need to add your plugin configuration in the `meltano.yml`'s plugin definition.

::: tip
Using `-e` will install the plugin as editable so any change you make is readily available.
:::

```bash
meltano add --custom extractor tap-gitlab-custom
...
> namespace: gitlab 
> pip_url: -e tap-gitlab-custom
> executable: tap-gitlab-custom
```

Meltano exposes each plugin configuration in the plugin definition, located in the `meltano.yml` file.

::: tip
Meltano manages converting the plugin's configuration to the appropriate definition for the plugin. You can find the generated file in `.meltano/run/tap-gitlab-custom/tap.config.json`.
:::

Looking at the `tap-gitlab-custom` definition, we should see the following (notice the `settings` section is missing):

**meltano.yml**
```yaml
plugins:
  extractors:
  - executable: tap-gitlab-custom
    name: tap-gitlab-custom
    namespace: gitlab
    pip_url: -e tap-gitlab-custom
...
```

Let's include the default configuration for a sample tap:

**meltano.yml**
```yaml
plugins:
  extractors:
  - executable: tap-gitlab-custom
    name: tap-gitlab-custom
    namespace: gitlab
    pip_url: -e tap-gitlab-custom
    settings:
    - name: username
    - name: password
      kind: password
    - name: start_date
      value: "2015-09-21T04:00:00Z"
...
```

#### Plugin Setting

When creating a new plugin, you'll often have to expose some settings to the user so that Meltano can generate the correct configuration to run your plugin.

To expose such a setting, you'll need to define it as such

 - **name**: Identifier of this setting in the configuration.  
 The name is the most important field of a setting, as it defines how the value will be passed down to the underlying component.  
 Nesting can be represented using the `.` separator.  

    - `foo` represents the `{ foo: VALUE }` in the output configuration.  
    - `foo.a` represents the `{ foo: { a: VALUE } }` in the output configuration.  

  - **kind**: Represent the type of value this should be, (e.g. `password` or `date_iso8601`). 
  
::: warning WIP
We are currently working on defining the complete list of setting's kind. See [issue (#739)](https://gitlab.com/meltano/meltano/issues/739) for more details.
:::

  - **env** (optional): Define the environment variable name used to set this value at runtime. *Defaults to `NAMESPACE_NAME`*.
  - **value** (optional): Define the default value for this variable. It should also be used as a placeholder for UX purposes.


Once the settings are exposed, you can use any of the following to set the proper values (in order of precedence):

  - Environment variables
  - `config` section in the plugin
  - Meltano UI 
  - `value` of the setting's definition

::: warning
Due to an outstanding [bug (#521)](https://gitlab.com/meltano/meltano/issues/521) you must run `meltano install` after modifying the `settings` section of a plugin.
:::

### Interacting with your new plugin

Now that your plugin is installed and configured, you are ready to interact with it using Meltano.

use `meltano invoke` to run your plugin in isolation:
```bash 
meltano invoke tap-gitlab-custom --discover
```

Use `meltano select` to parse your `catalog`:
```bash
meltano select --list tap-gitlab-custom '*' '*'
```
 
Run an ELT using your new tap:
```bash
meltano elt tap-gitlab-custom target-sqlite
```

### References

  - [Singer specification](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md#singer-specification)
  - [tap-gitlab](https://gitlab.com/meltano/tap-gitlab)
  - [target-sqlite](https://gitlab.com/meltano/target-sqlite)
  - [cookiecutter](https://github.com/audreyr/cookiecutter)
  - [singer-tap-template](https://github.com/singer-io/singer-tap-template)


## Advanced - Adding Custom Transformations and Models

### Prerequisites

- Meltano's minimum and [optional requirements](./installation.html#requirements) installed
- Docker started
- Meltano SalesForce [project](./tutorial.html#initialize-your-project-2) is initialized and [credentials](./tutorial.html#set-your-credentials) set.
- Meltano SalesForce [entities](./tutorial.html#select-the-entities-to-export-from-salesforce) are selected. 

We assume that you have also run the [ELT steps](./tutorial.html#run-elt-extract-load-transform) in the SalesForce tutorial.
Nothwithstanding, you can follow this tutorial in order to create entirely new transformations and run the whole ELT process in the end.

### Context

As an example, let's create transformations, which will allow us to look at closed opportunities (i.e. actual sales) by year, quarter and the following categorical dimensions:

- Size of the deal, i.e. Small (<5k$), Medium (5k$ - 25k$), Big (25k$ - 100k$), Jumbo (>100k$)
- Type of deal, i.e. New Business, Renewal, Add-On Business
- Client's location
- Client's industry
- Client's size, i.e. Small (<100 employees), Medium (100 - 999 employees), Large (1k - 20k employees), Strategic (>20k employees)

### Adding Custom Transforms

Let's create two additional tables:

- A table that includes won opportunities only and a custom category column for deal_size (opportunity_won.sql)
- A table that includes account categories, clients' countries, industries and a custom category column for company_size (account_category.sql).

These tables must be added as dbt models (`.sql` files) under the sfdc-project/transform/models/my_meltano_project/ directory or any of its subdirectories.

```bash
# opportunity_won.sql
with source as (
    
    -- Use the base sf_opportunity model defined by Meltano's 
    --  prepackaged tap_salesforce model
    select * from {{ref('sf_opportunity')}}

),

opportunity_won as (
    select
        -- Attributes directly fetched from the Opportunity Table
        opportunity_id,
        account_id,
        owner_id,

        opportunity_type,
        lead_source,

        amount,

        -- Additional Calculated Fields

        -- Add a deal size categorical dimension
        CASE WHEN
          amount :: DECIMAL < 5000
          THEN '1 - Small (<5k)'
        WHEN amount :: DECIMAL >= 5000 AND amount :: DECIMAL < 25000
          THEN '2 - Medium (5k - 25k)'
        WHEN amount :: DECIMAL >= 25000 AND amount :: DECIMAL < 100000
          THEN '3 - Big (25k - 100k)'
        WHEN amount :: DECIMAL >= 100000
          THEN '4 - Jumbo (>100k)'
        ELSE '5 - Unknown'
        END                         AS deal_size,

        -- Add Closed Date, Month, Quarter and Year columns
        CAST(closed_date AS DATE) as closed_date, 
        EXTRACT(MONTH FROM closed_date) closed_month,
        EXTRACT(QUARTER FROM closed_date) closed_quarter, 
        EXTRACT(YEAR FROM closed_date) closed_year  

    from source

    where is_won = true and is_closed = true
)

select * from opportunity_won
```

```bash
# account_category.sql
with source as (
    
    -- Use the base sf_opportunity model defined by Meltano's 
    --  prepackaged tap_salesforce model
    select * from {{ref('sf_account')}}

),

account_category as (

    select

        account_id,

        -- Set NULL values to 'Unknown'
        COALESCE(company_country, 'Unknown') as company_country,

        -- Set NULL values to 'Unknown'
        COALESCE(industry, 'Unknown') as industry,
        
        -- Add a company size categorical dimension
        CASE WHEN
          number_of_employees < 100
          THEN '1 - Small (<100)'
        WHEN number_of_employees >= 100 AND number_of_employees < 1000
          THEN '2 - Medium (100 - 999)'
        WHEN number_of_employees >= 1000 AND number_of_employees < 20000
          THEN '3 - Large (1k - 20k)'
        WHEN number_of_employees >= 20000
          THEN '4 - Strategic (>20k)'
        ELSE '5 - Unknown'
        END                         AS company_size

    from source
)

select * from account_category

```

In order to have the results of the transformations materialized in the analytics schema, we need to update sfdc-project/transform/dbt_project.yml. For more details on materialization options, please check dbt's documentation.

```bash
# Update `my_meltano_project: null` to `my_meltano_project: materialized: table`
models:
  my_meltano_project:
    materialized: table
  tap_salesforce:
    vars:
      livemode: false
      schema: '{{ env_var(''PG_SCHEMA'') }}'
```

We are now ready to run the required [ELT steps](./tutorial.html#run-elt-extract-load-transform) again.


Runs transformation step only
```bash
meltano elt tap-salesforce target-postgres --transform only
```
### Adding Custom Models

In order to access the newly transformed data in the UI, 2 additional types of files must be created:

- A table.m5o file, which defines the available columns and aggregates for each table
- A topic.m5o file, which represents the connections between tables, i.e. what they can be joined on.

These files must be added as [.m5o](./architecture.html#meltano-model) files under the sfdc-project/model/ directory.

```bash
# opportunity_won.table.m5o
{
  version = 1
  sql_table_name = opportunity_won
  name = opportunity_won
  columns {
    opportunity_id {
      primary_key = true
      hidden = true
      type = string
      sql = "{{table}}.opportunity_id"
    }
    owner_id {
      label = Owner ID (User)
      hidden = yes
      type = string
      sql = "{{TABLE}}.owner_id"
    }
    account_id {
      label = Account ID
      hidden = yes
      type = string
      sql = "{{TABLE}}.account_id"
    }
    opportunity_type {
      label = Oportunity Type
      description = Oportunity Type
      type = string
      sql = "{{table}}.opportunity_type"
    }
    lead_source {
      label = Lead Source
      description = Lead Source
      type = string
      sql = "{{table}}.lead_source"
    }
    deal_size {
      label = Deal Size
      description = Deal Size
      type = string
      sql = "{{table}}.deal_size"
    }
    closed_date {
      label = Closed Date
      description = Date the Opportunity Closed
      type = string
      sql = "{{table}}.closed_date"
    }
    closed_month {
      label = Closed Month
      description = Month the Opportunity Closed
      type = string
      sql = "{{table}}.closed_month"
    }
    closed_quarter {
      label = Closed Quarter
      description = Quarter the Opportunity Closed
      type = string
      sql = "{{table}}.closed_quarter"
    }
    closed_year {
      label = Closed Year
      description = Year the Opportunity Closed
      type = string
      sql = "{{table}}.closed_year"
    }
  }
  aggregates {
    total_opportunities {
      label = Total Opportunities
      description = Total Opportunities
      type = count
      sql = "{{table}}.opportunity_id"
    }
    total_amount {
      label = Total Amount
      description = Total Amount
      type = sum
      sql = "{{table}}.amount"
    }
    avg_amount {
      label = Average Amount
      description = Average Amount
      type = avg
      sql = "{{table}}.amount"
    }
  }
}
```

```bash
# account_category.table.m5o
{
  version = 1
  sql_table_name = account_category
  name = account_category
  columns {
    account_id {
      primary_key = true
      hidden = true
      type = string
      sql = "{{table}}.account_id"
    }
    company_country {
      label = Company Country
      description = Company Country
      type = string
      sql = "{{table}}.company_country"
    }
    company_size {
      label = Company Size
      description = Company Size
      type = string
      sql = "{{table}}.company_size"
    }
    industry {
      label = Industry
      description = Industry
      type = string
      sql = "{{table}}.industry"
    }
  }
}
```

```bash
# custom_sfdc.topic.m5o
{
  version = 1
  name = custom_sfdc
  connection = postgres_db
  label = Salesforce (Custom)
  designs {
    opportunity_won {
      label = Opportunities Won
      from = opportunity_won
      description = SFDC Opportunities Won
      joins {
        account_category {
          label = Opportunity
          sql_on = "opportunity_won.account_id = account_category.account_id"
          relationship = many_to_one
        }
      }
    }
  }
}

```

### Interact with Your Data in The Web App

[Interact with Your Data in The Web App](./tutorial.html#interact-with-your-data-in-the-web-app)


## Advanced - Using tap-postgres with Meltano

This is a tutorial on how to run `tap-postgres` with `target-postgres` in Meltano.

### Intro

`tap-postgres` is not currently officially supported by Meltano, so you have to add it as a custom tap. For more details, check the [documentation on adding a custom extractor](./tutorial.html#advanced-create-a-custom-extractor).

### Project Initialization 

Let's start by initializing a new Meltano Project and add the supported loader `target-postgres`:

```
meltano init tap-postgres
cd tap-postgres
meltano add loader target-postgres
```

### Adding a Custom Extractor

Next step is to add `tap-postgres` as a [custom extractor](./tutorial.html#advanced-create-a-custom-extractor). We'll use the [ tap-postgres provided by the Singer.io community](https://github.com/singer-io/tap-postgres/):

```bash
meltano add --custom extractor tap-postgres

  (namespace): tap-postgres
  (pip_url): tap-postgres
  (executable) [tap-postgres]: tap-postgres
```

We should then update `meltano.yml` and add the configuration parameters this tap needs in order to run:

**meltano.yml**
```yaml
plugins:
  connections:
  - name: sqlite
  - name: postgresql
  extractors:
  - executable: tap-postgres
    name: tap-postgres
    namespace: tap-postgres
    pip_url: tap-postgres
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
  - name: target-postgres
    pip_url: git+https://github.com/meltano/target-postgres.git
send_anonymous_usage_stats: false
version: 1.0
```

And finally update the project's `.env` to add the proper settings for the source and the target databases. The `TAP_PG_*` variables are used by the Tap (i.e. they define the source DB where the data are extracted from), while the `PG_*` variables are used by the Target (i.e. they define the target DB where the data will be loaded at)

**.env**
```bash
export FLASK_ENV=development

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
export PG_SCHEMA='test_tap_postgres'
```

Let's make sure that everything has been set correctly:

```bash
meltano config tap-postgres

  {'default_replication_method': 'FULL_TABLE', 'include_schemas_in_destination_stream_name': True, 'dbname': 'my_source_db', 'host': 'localhost', 'password': '***', 'port': '5432', 'user': '***'}

meltano config target-postgres

  {'user': '***', 'password': '***', 'host': 'localhost', 'port': '5432', 'dbname': 'my_target_db', 'schema': 'test_tap_postgres'}
```

### Filtering out data

This step is required if you don't want to export everything from the source db. You can skip it if you just want to export all tables.

We can use `meltano select` to select which entities will be exported by the Tap from the Source DB. You can find more info on how meltano select works on [the Meltano cli commands Documentation](./meltano-cli.html#select).

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

Selected properties:
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

#### Figuring out the names of the streams

In case you are not sure what the names of the streams are, you can use `meltano invoke` to run `tap-postgres` in isolation and generate a catalog file:

```bash
meltano invoke tap-postgres --discover > .meltano/run/tap-postgres/tap.properties.json
```

You can then check that file and decide which Streams (tables in this case) should be exported and use their `tap_stream_id` property when running `meltano select`.

### Run Meltano ELT

Finally run `meltano elt` to export all the selected Entities and load them to the schema of the target DB defined by `PG_SCHEMA` (`test_tap_postgres` in this example)

```bash
meltano elt tap-postgres target-postgres 
```

### Next Steps

If you want to add custom Transforms and explore the extracted data using Meltano UI, you should check the advanced tutorial on [Adding Custom Transformations and Models](./tutorial.html#advanced-adding-custom-transformations-and-models)


## Advanced - Loading CSV files to a Database

This tutorial explains how to load data stored in multiple CSV files to a Postgres Database and then use Custom Transforms and Models to combine them together and analyze the results.

We are going to use [tap-csv](https://gitlab.com/meltano/tap-csv) to extract the data from the CSV files and [target-postgres](https://github.com/meltano/target-postgres) to load the extracted data to Postgres.

### Prerequisites

- Meltano's minimum and [optional requirements](./installation.html#requirements) installed
- A Postgres Database installed and running
- Understanding how Transforms and Models work in Meltano and [how to add Custom Transforms and Models](./tutorial.html#advanced-adding-custom-transformations-and-models).

### Motivation and Running example

We have all the data for our very successful startup GitFlix, a git based video streaming service, in CSV files.

We export our user data from our CRM, the episode information from our CMS and the streaming data from our own custom streaming system.

It's time for us to move all our data to a Postgres Database, so that we can have everything together, run some advanced analysis and compare the results.

We have a pretty simple scenario: Users stream episodes from various TV series. 

For each user we have their name, age, their lifetime value to GitFlix (total subscriptions until today) and some additional data on how often they login to GitFlix and their total logins since they subscribed.

**[GitFlixUsers.csv](/files/GitFlixUsers.csv)**
```
 id |  name  | age | gender |  clv  | avg_logins | logins
----+--------+-----+--------+-------+------------+--------
  1 | John   |  23 | male   | 163.7 |  0.560009  | 123
  2 | George |  42 | male   | 287.3 |  1.232155  | 147
  3 | Mary   |  19 | female | 150.3 |  #DIV/0!   | 0
  4 | Kate   |  52 | female | 190.1 |  0.854654  | 156
  5 | Bill   |  35 | male   | 350.8 |  1.787454  | 205
  6 | Fiona  |  63 | female | 278.5 |  #DIV/0!   | 0
```

For episodes, we store their number (e.g. '304' for episode 4 of season 3), title, the TV series they belong to (e.g. 'Star Trek TNG'), the rating the episode got in IMDb and the expected ad revenue per minute on ad supported plans (the streaming wars have forced GitFlix to offer both a paid and an ad supported free subscription).

**[GitFlixEpisodes.csv](/files/GitFlixEpisodes.csv)**
```
 id | no  |        title        |  tv_series   | rating | ad_rev
----+-----+---------------------+--------------+--------+-----------
  1 | 101 | Pilot               | Breaking Bad |    8.9 | $2,438.13
  2 | 102 | Cat in the Bag...   | Breaking Bad |    8.7 | $1,718.42
  3 | 202 | Grilled             | Breaking Bad |    9.2 | $1,946.21
  4 | 101 | The National Anthem | Black Mirror |    7.9 | $1,198.24
  5 | 406 | Black Museum        | Black Mirror |    8.7 | $1,256.89
  6 | 104 | Old Cases           | The Wire     |    8.3 | $834.67
  7 | 306 | Homecoming          | The Wire     |    8.9 | $764.37
```

Finally, for each episode streamed by each user, we keep track how many minutes the user has streamed each day (not all users view the full length of all episodes at one sitting).

**[GitFlixStreams.csv](/files/GitFlixStreams.csv)**
```
 id | user_id | episode_id | minutes | day | month | year 
----+---------+------------+---------+-----+-------+------
  1 |       1 |          1 |      40 |  10 |     1 | 2019
  2 |       1 |          2 |      42 |  10 |     1 | 2019
  3 |       1 |          3 |      38 |  11 |     1 | 2019
  4 |       1 |          4 |      12 |  11 |     1 | 2019
  5 |       1 |          5 |      27 |  11 |     1 | 2019
  6 |       2 |          2 |      36 |  11 |     1 | 2019
  7 |       2 |          6 |      45 |  11 |     1 | 2019
  8 |       2 |          7 |      44 |  11 |     1 | 2019
  9 |       3 |          4 |      40 |  10 |     1 | 2019
 10 |       3 |          5 |      41 |  11 |     1 | 2019
 11 |       3 |          1 |      11 |  11 |     1 | 2019
 12 |       4 |          3 |      22 |  10 |     1 | 2019
 13 |       4 |          3 |      18 |  11 |     1 | 2019
 14 |       4 |          6 |      40 |  11 |     1 | 2019
 15 |       5 |          2 |      34 |  11 |     1 | 2019
 16 |       5 |          4 |      41 |  11 |     1 | 2019
 17 |       5 |          5 |      39 |  12 |     1 | 2019
 18 |       5 |          6 |      36 |  12 |     1 | 2019
 19 |       6 |          1 |      19 |  11 |     1 | 2019
 20 |       6 |          3 |      35 |  11 |     1 | 2019
 21 |       6 |          7 |      48 |  11 |     1 | 2019
 22 |       6 |          1 |      24 |  12 |     1 | 2019
```

We'll use Meltano to:

- Load the data to our Postgres DB.
- Use custom transforms to clean and normalize the data.
- Create a custom Meltano Model so that we can explore the transformed data and generate meaningful reports.

### Initialize Your Project

To get started, navigate to a directory, in your terminal, where you want your Meltano project to be installed and run the following commands:

::: tip Remember
Run `source venv/bin/activate` to leverage the `meltano` installed in your virtual environment (`venv`) if you haven't already.
:::

```bash
# Initialize a new project with a folder called csv-project
meltano init csv-project

# Change directory into your new csv-project project
cd csv-project
```

If you haven't already done so, download the example CSV files to your newly created project directory (i.e. csv-project):

- [GitFlixUsers.csv](/files/GitFlixUsers.csv)
- [GitFlixEpisodes.csv](/files/GitFlixEpisodes.csv)
- [GitFlixStreams.csv](/files/GitFlixStreams.csv)

::: tip Note on CSV files
Each input CSV file used with [tap-csv](https://gitlab.com/meltano/tap-csv) must be a traditionally-delimited CSV (commas separated columns, newlines indicate new rows, double quoted values) as defined by the defaults to the python csv library. The first row is the header defining the attribute name for that column and will result to a column of the same name in the database. You can check the downloaded files as an example of valid CSV files (they were generated by exporting Google Sheets to CSV).
:::

### Set Your Credentials

Update the .env file in your project directory (i.e. csv-project) with your Postgres DB credentials and the file you are going to use to describe the CSV files to be loaded.

**.env**
```bash
export FLASK_ENV=development

export PG_DATABASE=warehouse
export PG_PASSWORD=warehouse
export PG_USERNAME=warehouse
export PG_ADDRESS=localhost
export PG_PORT=5432

export PG_SCHEMA='csv_imports'

export TAP_CSV_FILES_DEFINITION="csv_files.json"
```

You should replace the example `warehouse` value as the name of the database, the user and password with your own Postgres credentials and change the address and port if the Postgres is not running locally and on the default Port.

PG_SCHEMA is the schema that will be used to import the raw data to and TAP_CSV_FILES_DEFINITION (`csv_files.json` in the example) is a json file with all the CSV files to be loaded.

Finally, create the `csv_files.json` file in your project directory:

**csv_files.json**
```json
[   
  { "entity" : "users",
    "file" : "GitFlixUsers.csv",
    "keys" : ["id"]
  },
  { "entity" : "episodes",
    "file" : "GitFlixEpisodes.csv",
    "keys" : ["id"]
  },
  { "entity" : "streams",
    "file" : "GitFlixStreams.csv",
    "keys" : ["id"]
  }
]
```

Description of available options:
  - entity: The entity name, used as the table name for the data loaded from that CSV.
  - file: Local path (relative to the project's root) to the file to be ingested.
  - keys: The names of the columns that constitute the unique keys for that entity.

Finally, make the credentials available to Meltano by executing the following command in your terminal:

```bash
source .env
```

### Load the CSV files to Postgres

Run the Extract > Load pipeline:

```bash
meltano elt tap-csv target-postgres
```

The extracted data will be available to the Postgres schema defined by `PG_SCHEMA`.

Using our running example, tables `users`, `episodes` and `streams` will be available in the `csv_imports` schema, with all the data from the original CSV files loaded as records.

### Motivation for transforming the raw extracted data

So all the records in our CSV files were loaded successfully to our Database, but we are still having some issues:

- Everything is a string in a CSV, so all values were loaded as `character varying` to our Postgres DB. Strings are not very useful for calculating aggregates, so we want to convert all numerical measures to floats or integers accordingly.
- Similarly, we want to run more complex value transformations; for example, convert a value like `$2,638,765.21` to `2638765.21` by removing the `$` and commas and converting the result to a float.
- Column names like `clv` (short for customer lifetime value), `avg_logins` (short for average logins per day) or `ad_rev` (short for expected ad revenue per minute on ad supported plans) can be part of raw formatting but are not very useful to a high level user. We want to provide proper, descriptive, attribute names.
- Some of our columns have errors like `#DIV/0!` (division by zero), which we want to clean and convert to NULL values or 0s (depending on the business logic).

We are going to add some simple custom transforms in order to clean and normalize the data.

### Add Custom Transforms

Let's start by adding the base transforms that will clean the loaded data and fix the issues described in the previous section.

First step is to enable the option to run Custom Transforms for our project and set the results of the transforms to be stored as materialized tables:

**transform/dbt_project.yml**
```bash
... ... ...
models:
    my_meltano_project:
        materialized: table
... ... ...
```

The Transforms must be added as dbt models (.sql files) under the `csv-project/transform/models/my_meltano_project/` directory or any of its subdirectories.

The name of each Transform's file will be the name of the final table in the `analytics` schema, so we choose to name them:
- `gitflix_users.sql`
- `gitflix_episodes.sql`
- `gitflix_streams.sql`

**transform/models/my_meltano_project/gitflix_users.sql**

```sql
with source as (

    select * from {{ env_var('PG_SCHEMA') }}.users

),

renamed as (

    select
        -- Primary Key: Cast to integer and provide unique name
        CAST(id as integer)                 as user_id,

        -- Profile Attributes
        name                                as name,

        -- Fix empty values and cast the age to integer
        CAST(nullif(age, '') as integer)    as age,

        -- Add an age_group categorical dimension
        case
            when CAST(nullif(age, '') as integer) < 18
                then '1 - Under 18'
            when CAST(nullif(age, '') as integer) >= 18 
              and CAST(nullif(age, '') as integer) < 40
                then '2 - 20 to 40'
            when CAST(nullif(age, '') as integer) >= 40 
              and CAST(nullif(age, '') as integer) < 60
                then '3 - 40 to 60'
            when CAST(nullif(age, '') as integer) >= 60
                then '4 - Above 60'
            else '5 - Unknown'
        end                                 as age_group,

        gender                              as gender,

        -- Fix empty values and cast the rating to float
        CAST(nullif(clv, '') as float)      as customer_lifetime_value,

        -- Remove #DIV/0 errors, keep only 2 decimals and convert to numeric
        case
            when avg_logins is NULL
                then NULL
            when avg_logins like '%#DIV/0%'
                then NULL
            else 
                round( 
                   CAST(nullif( avg_logins , '') as numeric), 
                   2
                )
        end as avg_logins_per_day,

        CAST(nullif(logins, '') as integer) as logins

    from source

    where 
      -- Make sure that we keep only users with valid IDs
      id is NOT NULL

      -- and that we remove all the test entries
      and name NOT LIKE 'test_user_%'

)

select * from renamed
```

**transform/models/my_meltano_project/gitflix_episodes.sql**

```sql
with source as (

    select * from {{ env_var('PG_SCHEMA') }}.episodes

),

renamed as (

    select
        -- Primary Key: Cast to integer and provide unique name
        CAST(id as integer) as episode_id,

        -- Keep the Episode Number as a string
        no as episode_number,
        title as title,
        tv_series as tv_series,

         -- Fix empty values and cast the rating to float
        CAST(nullif(rating, '') as float) as imdb_rating,

        -- Remove the $ from the start and the commas
        --  and then cast to float
        CAST( 
            nullif( replace( substring(ad_rev from 2), ',', ''),'' ) 
            AS float
        ) as ad_revenue_per_minute

    from source

    where 
      -- Make sure that we keep only episodes with valid IDs
      id is NOT NULL

      -- and that we remove all the test entries
      and title NOT LIKE 'test_the_test_%'

)

select * from renamed
```

**transform/models/my_meltano_project/gitflix_streams.sql**

```sql
with source as (

    select * from {{ env_var('PG_SCHEMA') }}.streams

),

renamed as (

    select
        -- Primary Key: Cast to integer and provide unique name
        CAST(id as integer) as stream_id,

        -- Foreign Keys: Cast to integer
        CAST(user_id as integer) as user_id,
        CAST(episode_id as integer) as episode_id,

        -- Cast everything else to integer
        CAST(nullif(minutes, '') as integer) as minutes_streamed,

        CAST(nullif(day, '') as integer) as day,
        CAST(nullif(month, '') as integer) as month,
        CAST(nullif(year, '') as integer) as year

    from source

    where 
      -- Make sure that we keep only streams with valid IDs
      id is NOT NULL 
      and user_id is NOT NULL 
      and episode_id is NOT NULL

)

select * from renamed
```

In the transforms above we could have hard coded the schema the raw tables reside inside (in this example `csv_imports`), but we make use of the fact that it is defined by the environmental variable `PG_SCHEMA` and use that instead. That means that even if you change the configuration and load the data to a different schema, the Transforms will not have to change.

### Run the Custom Transforms

You are ready to run the custom transforms:

```bash
meltano elt tap-csv target-postgres --transform only
```

Or in general, if you want to extract and load more data first you can run all the ELT steps together:

```bash
meltano elt tap-csv target-postgres --transform run
```

The result will be three new tables in your `analytics` schema with the transformed schema and data, following the transforms defined in the previous section:

- `analytics.gitflix_users`
- `analytics.gitflix_episodes`
- `analytics.gitflix_streams`


### Add Custom Meltano Models

In order to access the newly transformed data in Meltano UI, 2 additional types of files must be created:

- Three table.m5o files, which define the available columns and aggregates for each table created during the Transform step.
- A topic.m5o file, which represents the connections between tables, i.e. what they can be joined on.

These files must be added as .m5o files under the `csv-project/model/` directory.

**gitflix_users.table.m5o**
```bash
{
  version = 1
  sql_table_name = gitflix_users
  name = gitflix_users
  columns {
    user_id {
      primary_key = true
      hidden = true
      type = string
      sql = "{{table}}.user_id"
    }
    name {
      label = User Name
      description = User Name
      type = string
      sql = "{{table}}.name"
    }
    gender {
      label = User Gender
      description = User Gender
      type = string
      sql = "{{table}}.gender"
    }
    age_group {
      label = User Age Group
      description = User Age Group
      type = string
      sql = "{{table}}.age_group"
    }
  }
  aggregates {
    total_users {
      label = Total Users
      description = Total Users
      type = count
      sql = "{{table}}.user_id"
    }
    average_age {
      label = Average User Age
      description = Average User Age
      type = avg
      sql = "{{table}}.age"
    }
    total_customer_lifetime_value {
      label = Total Customer Lifetime Value
      description = Total Customer Lifetime Value
      type = sum
      sql = "{{table}}.customer_lifetime_value"
    }
    average_customer_lifetime_value {
      label = Average Customer Lifetime Value
      description = Average Customer Lifetime Value
      type = avg
      sql = "{{table}}.customer_lifetime_value"
    }
    average_logins_per_day {
      label = Average User Logins Per Day
      description = Average User Logins Per Day
      type = avg
      sql = "{{table}}.avg_logins_per_day"
    }
    total_logins {
      label = Total User Logins
      description = Total User Logins
      type = sum
      sql = "{{table}}.logins"
    }
    average_logins {
      label = Average User Logins
      description = Average User Logins
      type = avg
      sql = "{{table}}.logins"
    }
  }
}
```

**gitflix_episodes.table.m5o**
```bash
{
  version = 1
  sql_table_name = gitflix_episodes
  name = gitflix_episodes
  columns {
    episode_id {
      primary_key = true
      hidden = true
      type = string
      sql = "{{table}}.episode_id"
    }
    tv_series {
      label = TV Series
      description = TV Series
      type = string
      sql = "{{table}}.tv_series"
    }
    title {
      label = Episode Title
      description = Episode Title
      type = string
      sql = "{{table}}.title"
    }
    episode_number {
      label = Episode Number
      description = Episode Number
      type = string
      sql = "{{table}}.episode_number"
    }
  }
  aggregates {
    total_episodes {
      label = Total Episodes
      description = Total Episodes
      type = count
      sql = "{{table}}.episode_id"
    }
    average_imdb_rating {
      label = Average IMDB Rating
      description = Average IMDB Rating
      type = avg
      sql = "{{table}}.imdb_rating"
    }
    total_ad_revenue_per_minute {
      label = Total Ad Revenue per Minute
      description = Total Ad Revenue per Minute
      type = sum
      sql = "{{table}}.ad_revenue_per_minute"
    }
    average_ad_revenue_per_minute {
      label = Average Ad Revenue per Minute
      description = Average Ad Revenue per Minute
      type = avg
      sql = "{{table}}.ad_revenue_per_minute"
    }
  }
}
```

**gitflix_streams.table.m5o**
```bash
{
  version = 1
  sql_table_name = gitflix_streams
  name = gitflix_streams
  columns {
    stream_id {
      primary_key = true
      hidden = true
      type = string
      sql = "{{table}}.stream_id"
    }
    user_id {
      label = User ID
      hidden = yes
      type = string
      sql = "{{TABLE}}.user_id"
    }
    episode_id {
      label = Episode ID
      hidden = yes
      type = string
      sql = "{{TABLE}}.episode_id"
    }
    day {
      label = Stream Day
      description = Stream Day
      type = string
      sql = "{{table}}.day"
    }
    month {
      label = Stream Month
      description = Stream Month
      type = string
      sql = "{{table}}.month"
    }
    year {
      label = Stream Year
      description = Stream Year
      type = string
      sql = "{{table}}.year"
    }
  }
  aggregates {
    total_streams {
      label = Total Streams
      description = Total Streams
      type = count
      sql = "{{table}}.stream_id"
    }
    total_minutes_streamed {
      label = Total Minutes Streamed
      description = Total Minutes Streamed
      type = sum
      sql = "{{table}}.minutes_streamed"
    }
    average_minutes_streamed {
      label = Average Minutes Streamed
      description = Average Minutes Streamed
      type = avg
      sql = "{{table}}.minutes_streamed"
    }
  }
}
```

**gitflix.topic.m5o**
```bash
{
  version = 1
  name = gitflix
  connection = postgres_db
  label = GitFlix
  designs {
    gitflix_users {
      label = GitFlix Users
      from = gitflix_users
      description = "Info on GitFlix Users"
    }
    gitflix_episodes {
      label = GitFlix Episodes
      from = gitflix_episodes
      description = "Info on GitFlix Episodes"
    }
    gitflix_stats_per_user {
      label = GitFlix Users
      from = gitflix_users
      description = "GitFlix Stats Per User, Episode and Stream"
      joins {
        gitflix_streams {
          label = GitFlix Streams
          sql_on = "gitflix_streams.user_id = gitflix_stats_per_user.user_id"
          relationship = many_to_one
        }
        gitflix_episodes {
          label = GitFlix Episodes
          sql_on = "gitflix_episodes.episode_id = gitflix_streams.episode_id"
          relationship = many_to_one
        }
      }
    }
  }
}
```

### Interact with Your Data in The Web App

With the previous step done, you are set to explore your data using Meltano UI and generate ad-hoc reports.

[Start Meltano UI and setup a connection to your Postgres](./tutorial.html#interact-with-your-data-in-the-web-app)

You can now go to the `Analyze` tab and select one of the three Designs we have created:

![](/screenshots/gitflix_analyze.png)

For example, you can check the high level Gitflix stats per Gender or Age group:

![](/screenshots/gitflix_user_stats_per_gender.png)

Or generate in depth reports on the streaming data:

![](/screenshots/gitflix_stats_per_gender_series.png)

### Next steps

You should now be able to follow the same steps to import your own CSV files and generate complex reports in Meltano UI:

- Prepare your CSV files so that they have a header in the first line with the attribute names.

- Update `csv_files.json` to link your CSV files and use the proper entity name and key(s) for each.

- Import and check the raw data

- Add custom Transforms and Models by following the Gitflix example or any other Transforms and Models provided by Meltano. You can check the [Meltano Group](https://gitlab.com/meltano/) for projects that define default [transforms](https://gitlab.com/meltano?utf8=%E2%9C%93&filter=dbt-) or [models](https://gitlab.com/meltano?utf8=%E2%9C%93&filter=model-) for various supported APIs if you want to see real world examples.


## Using Jupyter Notebooks

Once the `meltano elt` pipeline has successfully completed and data extracted from an API or a Data Source have been transformed and loaded to the `analytics` schema of your Data Warehouse, you can use Meltano UI or any data exploration tool to analyze and generate reports.

In this tutorial, we are going to present how to connect [Jupyter Notebook](https://jupyter.org/) to a Meltano Project that uses Postgres to store the transformed data.


### Prerequisites

- Meltano's minimum and [optional requirements](./installation.html#requirements) installed
- Docker started
- You have successfully extracted and loaded data from an API by following the steps described in the previous Tutorials.


### Jupyter Notebook Installation

If you have Jupyter already installed in your system, you can skip this step.

The most common options for [installing Jupyter Notebook](https://jupyter.org/install) are by either using Anaconda or pip. We are going to use pip in this tutorial, as Meltano also uses pip for its installation.

::: tip Remember
If you used a virtual environment (`venv`) to install and run Meltano, don't forget to first navigate to the directory with your `venv` and run `source venv/bin/activate` to enable it.
:::

The following commands will install Jupyter Notebook and the most common python libraries required to connect to a Database (psycopg2, sqlalchemy), manipulate data (pandas) and generate some ad hoc plots (matplotlib):

```bash
pip install jupyter
pip install numpy
pip install pandas
pip install psycopg2
pip install sqlalchemy
pip install matplotlib
```

Once the installation is completed, you are set to use Jupyter Notebooks with Meltano.

### Running Jupyter Notebook 

(**Optional**) Navigate to your Meltano Project and make the credentials you used with Meltano available to the environment the Jupyter Notebook will run:

```bash
cd /path/to/my/meltano/project
set +a
source .env
set -a 
```

This is an optional step, but allows us to use the same credentials (e.g. for connecting to Postgres) from inside Jupyter Notebook without entering them again and, more importantly, without exposing any sensitive information inside the Notebook in case you want to share the Notebook with others.

You can now navigate to Meltano's directory for storing your notebooks and [start Jupyter Notebook](https://jupyter.readthedocs.io/en/latest/running.html#running):

```bash
cd notebook/
jupyter notebook
```

This will print some information about the notebook server in your terminal, including the URL of the web application (by default, http://localhost:8888):

```bash
$ jupyter notebook
[I 13:18:36.606 NotebookApp] Serving notebooks from local directory: /home/iroussos/work/code/my-projects/jupyter-tutorial/notebook
[I 13:18:36.609 NotebookApp] The Jupyter Notebook is running at:
[I 13:18:36.610 NotebookApp] http://localhost:8888/
[I 13:18:36.612 NotebookApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).
```

It will then open your default web browser to this URL.

When the notebook opens in your browser, you will see the Notebook Dashboard, which will show a list of the notebooks, files, and subdirectories in the directory where the notebook server was started. 

If this is the first time you start `jupyter notebook` from the `notebook` directory of your Meltano project, the list will be empty. Let's start a new Python notebook!

### Notebook Basics

While on the Notebook Dashboard, you can start a new Notebook by selecting `Python 3` from the `New` drop down menu.

We are going to showcase the most simple and straightforward way to connect to your `analytics` schema, fetch some transformed data and generate some plots.

The first step for a data exploration Notebook is to import the proper libraries required for data exploration and manipulation and then setup the connection to the Database (Postgres in our case) so that we can fetch data:

**Cell 1**
```python
# Import required libraries
import pandas as pd
import psycopg2
import sqlalchemy
import matplotlib as plt 
import os

from sqlalchemy import create_engine

%matplotlib inline

# Get the Postgres username, password, and database name from the Environment
# You can also set them directly here, but it's better not to include passwords
#  or parameters specific to you inside the Notebook
POSTGRES_ADDRESS = os.getenv("PG_ADDRESS")
POSTGRES_PORT = os.getenv("PG_PORT")
POSTGRES_DBNAME = os.getenv("PG_DATABASE")
POSTGRES_USERNAME = os.getenv("PG_USERNAME")
POSTGRES_PASSWORD = os.getenv("PG_PASSWORD")

# Connect to the analytics schema, not one of the schemas with the raw data extracted
PG_SCHEMA = 'analytics'

# A long string that contains the necessary Postgres login information
postgres_str = ('postgresql://{username}:{password}@{ipaddress}:{port}/{dbname}'
                .format(username=POSTGRES_USERNAME, 
                        password=POSTGRES_PASSWORD,
                        ipaddress=POSTGRES_ADDRESS,
                        port=POSTGRES_PORT,
                        dbname=POSTGRES_DBNAME))

# Create the connection
cnx = create_engine(postgres_str)
```

Click `|>| Run` and we are set to start exploring the data in brought in with Meltano.

You can then write queries and generate plots at will.

As an example, assume that you have loaded data from your Zendesk Account by using `tap_zendesk`. You can then check the most important Ticket statistics by month:

**Cell 2**
```python
# Query to send to the Database
sql_query = f'''
SELECT 
  created_year || '-' || created_month as month, 
  COUNT(*) as total_tickets,
  SUM(ticket_unsolved_counter) as unsolved_tickets,
  SUM(ticket_solved_counter) as solved_tickets,
  SUM(ticket_one_touch_counter) as one_touch_tickets,
  SUM(ticket_reopened_counter) as reopened_tickets,
  SUM(replies) as total_replies,
  ROUND(AVG(replies), 2) as avg_replies,
  ROUND(AVG(full_resolution_time_in_minutes_business), 2) as avg_res_time_mins
    
FROM {PG_SCHEMA}.zendesk_tickets_xf

GROUP BY created_year, created_month

ORDER BY created_year, created_month;
'''

# Execute the query and store the result in a pandas dataframe
result = pd.read_sql_query(sql_query, cnx)

# Print the result to the output to check what the query brought in
result
```

Or generate a bar plot:

**Cell 3**
```python
plt.rcParams['figure.figsize'] = [15, 8]
result.plot.bar(x='month', y=['total_tickets','unsolved_tickets','solved_tickets','one_touch_tickets','reopened_tickets'])
```

### Additional Resources

In order to make the most out of Jupyter Notebooks, you can check the following resources:
*  [Documentation for pandas](https://pandas.pydata.org/), the Python Data Analysis Library that provides high-performance, easy-to-use data structures and data analysis tools for the Python programming language.
*  [Pandas Tutorial using Jupyter Notebooks](https://data36.com/pandas-tutorial-1-basics-reading-data-files-dataframes-data-selection/)
*  [Jupyter Notebook for Beginners: A Tutorial](https://www.dataquest.io/blog/jupyter-notebook-tutorial/)
