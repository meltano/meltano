---
sidebarDepth: 2
---

# Tutorials

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

```bash
# Initialize a new project with a folder called carbon
meltano init carbon

# Change directory into your new carbon project
cd carbon

# Let's see what extractors and loaders are available
meltano discover all

# Run the extractor (tap) and loader (target)
meltano elt tap-carbon-intensity target-sqlite

# Ensure Meltano UI will know how to use data from ELT
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
# Start up the Meltano UI web application!
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

```bash
# Initialize a new project with a folder called sfdc-project
meltano init sfdc-project

# Change directory into your new sfdc-project project
cd sfdc-project

# Start docker postgres instance
docker-compose up -d warehouse_db

# Let's see what extractors and loaders are available
meltano discover all

# Add tap-salesforce - to `select` which Salesforce entities will be extracted before running the meltano `elt` command and set the credentials for your Salesforce instance
meltano add extractor tap-salesforce

# Add target-postgres - to set the credentials for your Postgres DB
meltano add loader target-postgres
```

### Set Your Credentials
Update the .env file in your project directory (i.e. sfdc-project) with the SFDC and Postgres DB credentials.

```
export FLASK_ENV=development
export SQLITE_DATABASE=meltano

export PG_PASSWORD=warehouse
export PG_USERNAME=warehouse
export PG_ADDRESS=localhost
export PG_SCHEMA=analytics
export PG_PORT=5502
export PG_DATABASE=warehouse

export SFDC_URL=
export SFDC_USERNAME=''
export SFDC_PASSWORD=''
export SFDC_SECURITY_TOKEN=''
export SFDC_CLIENT_ID='secret_client_id'

export SFDC_START_DATE='2019-03-01T00:00:00Z'
```

You can leave `SFDC_URL` and `SFDC_CLIENT_ID` as they are in the example above, but you have to set `SFDC_USERNAME`, `SFDC_PASSWORD` and `SFDC_SECURITY_TOKEN` and `SFDC_START_DATE` according to your instance and preferences.

Finally, make the credentials available to Meltano by executing the following command in your terminal:

```bash
source .env
```

### Select The Entities to Export from Salesforce

A Salesforce account may have more than 100 different entities. In order to see the list of available entities, please run

```bash
meltano select tap-salesforce --list --all
```

In this tutorial, we are going to work with a couple of the most common ones and show you how to [select](docs/meltano-cli.html#meltano-select) entities to extract from a specific API: Account, Contact, Lead, User, Opportunity and Opportunity History:

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

```bash
# Only run the Extract and Load steps
meltano elt tap-salesforce target-postgres

# Only run the Transform Step
meltano elt tap-salesforce target-postgres --transform only
```

The transform step uses the dbt [transforms](/docs/meltano-cli.html#transforms) defined by [Mavatar's Salesforce dbt package](https://gitlab.com/meltano/dbt-tap-salesforce).
When meltano elt tap-salesforce target-postgres --transform run is executed, both default and custom dbt transformations in the transform/ directory (a folder created upon project initilization) are being performed.

In order to visualize the data with existing transformations in the UI, the final step would be to add models:

```bash
# Add existing models
meltano add model model-salesforce
```

### Interact with Your Data in The Web App

In order to start the UI, where you can interact with the transformed data, please go back to your terminal and execute the following command:

```bash
# This will start a local web server at [http://localhost:5000](http://localhost:5000)
meltano ui
```

When you visit the URL, you will be using the default connection to Meltano's SQLite database. In order to allow the UI to access your postgres DB instance, please follow the steps below:

1. Navigate to the Postgres Loader Settings (Configuration > Loaders > target-postgres > Account Settings)
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

## Advanced - Create a Custom Extractor

As much as we'd like to support all the data sources out there, we'll need your help to get there. If you find a data source that Meltano doesn't support right now, it might be time to get your hands dirty.

We aim to make Meltano as thin as possible on top of the components it abstracts, so adding a new plugin should be straightforward.

### How to Create a Extractor

First things first, you'll need a data source to integrate: in this example, let's say we want to create a tap to fetch data from `GitLab`.

If you are looking to integrate GitLab's data into your warehouse, please use tap official [https://gitlab.com/meltano/tap-gitlab](tap-gitlab).
:::

### Create the Plugin's Package

Meltano uses [Singer](https://singer.io) taps and targets to extract and load data. For more details about the Singer specification, please visit [https://github.com/singer-io/getting-started](https://github.com/singer-io/getting-started)

::: tip
[cookiecutter](https://cookiecutter.readthedocs.io/en/latest/) is a python tool to scaffold projects quickly from an existing template.
:::

```bash
$ pip install cookiecutter
$ cookiecutter gh:singer-io/singer-tap-template
> project_name: tap-gitlab-custom
```

### Add the Plugin to Your Meltano Project (--custom)

Now that your plugin is part of your Meltano project, you need to add your plugin configuration in the `meltano.yml`'s plugin definition.

::: tip
Using `-e` will install the plugin as editable so any change you make is readily available.
:::

```bash
# test
$ meltano add --custom extractor tap-gitlab-custom
...
> pip_url: -e tap-gitlab-custom
> executable: tap-gitlab-custom
```

Meltano exposes each plugin configuration in the plugin definition, located in the `meltano.yml` file.

::: tip
Meltano manages converting the `config` section to the appropriate definition for the plugin. You can find the generated file in `.meltano/run/tap-gitlab-custom/tap.config.json`.
:::

Looking at the `tap-gitlab-custom` definition, we should see the following (notice the `config` section is `null`):

**meltano.yml**
```yaml
plugins:
  extractors:
  - config: null
    executable: tap-gitlab-custom
    name: tap-gitlab-custom
    pip_url: -e tap-gitlab-custom
...
```

Let's include the default configuration for a sample tap:

**meltano.yml**
```yaml
plugins:
  extractors:
  - config:
	  username: $GITLAB_USERNAME # supports env expansion
	  password: my_password
	  start_date: "2015-09-21T04:00:00Z"
    executable: tap-gitlab-custom
    name: tap-gitlab-custom
    pip_url: -e tap-gitlab-custom
...
```

::: warning
Due to an outstanding [bug (#521)](https://gitlab.com/meltano/meltano/issues/521) you must run `meltano install` after modifying the `config` section of a plugin.
:::

### Interacting with your new plugin

Now that your plugin is installed and configured, you are ready to interact with it using Meltano.

```
;; use `meltano invoke` to run your plugin in isolation
$ meltano invoke tap-gitlab-custom --discover

;; use `meltano select` to parse your `catalog`
$ meltano select --list tap-gitlab-custom '*' '*'

;; run an ELT using your new tap
$ meltano elt tap-gitlab-custom target-sqlite
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
  enabled: true
  my_meltano_project:
    materialized: table
  tap_salesforce:
    vars:
      livemode: false
      schema: '{{ env_var(''PG_SCHEMA'') }}'
```
Before we re-run the ELT process, we should update our environment variables.

```bash
source .env
```

We are now ready to run the required [ELT steps](./tutorial.html#run-elt-extract-load-transform) again.

```bash
# Runs transformation step only
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


## Using Docker

### Using pre-built Docker images

We provide the [meltano/meltano](https://hub.docker.com/r/meltano/meltano) docker image with Meltano preinstalled and ready to use.

> Note: The **meltano/meltano** docker image is also available in GitLab's registry: `registry.gitlab.com`

This image contains everything you need to get started with Meltano.

```bash
# to download or update to the latest version
$ docker pull meltano/meltano

# to look the currently installed version
$ docker run meltano/meltano --version
meltano, version …
```

Please refer to the [docker tutorial](/docs/tutorial.html#using-docker) for more details.

### Creating your own Docker image

It is possible to run Meltano as a Docker container to simplify usage, deployment, and orchestration.

> This tutorial is inspired of the [Starter tutorial](#starter) but with Meltano running inside a Docker container.

We will use `docker run` to execute Meltano using the pre-built docker images.

#### Initialize Your Project

First things first, let's create a new Meltano project named **carbon**.

```
$ docker run -v $(pwd):/projects \
             -w /projects \
             meltano/meltano init carbon
```

Then you can `cd` into your new project:

```
$ cd carbon
```

Now let's extract some data from the **tap-carbon-intensity** into **target-sqlite**:

```
$ docker run -v $(pwd):/project \
             -w /project \
             meltano/meltano elt tap-carbon-intensity target-sqlite
```

#### Analyze with Meltano UI

Now that we have data in ur database, let's add the corresponding model bundle as the basis of our analysis.

```
$ docker run -v $(pwd):/project \
             -w /project \
             meltano/meltano add model model-carbon-intensity-sqlite
```

We can then start the Meltano UI.

```
# `ui` is the default command, we can omit it.
$ docker run -v $(pwd):/project \
             -w /project \
             -p 5000:5000 \
             meltano/meltano
```

You can now visit [http://localhost:5000](http://localhost:5000) to access the Meltano UI.

For furter analysis, please head to the [Analyze](#analyze) section.


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
source .env
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
