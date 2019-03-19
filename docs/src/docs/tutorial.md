---
sidebarDepth: 2
---

# Tutorials

First time using Meltano? No worries. We have you covered with tutorials that will guide you through how Meltano works. Let's get started!

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

# Ensure Meltano UI will know how to use data from ELT
meltano add model model-carbon-intensity-sqlite

# Run the extractor (tap) and loader (target)
meltano elt tap-carbon-intensity target-sqlite
```

Congratulations! You have just extracted all the data from the Carbon Intensity API and loaded it into your local SQLite database.

:::tip
Meltano is magical and powerful.

It extracts data from various sources like Salesforce, Zendesk, and Google Analytics and then loads that data into the database of your choice. You can use community extractors and loaders or write your own too.

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

![](/screenshots/meltano-ui-carbon-tutorial-output.png)

:::warning Troubleshooting
Having issues with Meltano? Help us help you. Here is a [pre-baked form to streamline us doing so](https://gitlab.com/meltano/meltano/issues/new?issue%5Bassignee_id%5D=&issue%5Bmilestone_id%5D=&issuable_template=bugs).
:::

---
#### Analyze

With Meltano UI up and running, we can automatically generate queries with as little as a single click and then explore the query results:

- Navigate to Model > Region (Model dropdown)
- Open Region accordion
  - Toggle *at least one* aggregate button to generate SQL
  - Toggle any number of column buttons to generate SQL
  - Click the Run button to query using the generated SQL
- Open the Charts accordion to visualize the data!

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

# Add a m5o model so Meltano UI will know how to use data from ELT
meltano add model model-salesforce

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

In this tutorial, we are going to work with a couple of the most common ones and show you how to [select](docs/meltano-cli.html#meltano-select ) entities to extract from a specific API: Account, Contact, Lead, User, Opportunity and Opportunity History:

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

### Interact with Your Data in The Web App

In order to start the UI, where you can interact with the transformed data, please go back to your terminal and execute the following command:

```bash
# This will start a local web server at [http://localhost:5000](http://localhost:5000)
meltano ui
```

When you visit the URL, you will be using the default connection to Meltano's SQLite database. In order to allow the UI to access your postgres DB instance, please follow the steps below:

1. Navigate to Settings (upper-right corner) and select `Database`
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

## Advanced - Coming Soon

You can look forward to the following tutorials in the future:

- Salesforce > Snowflake Tutorial
- How to add your own transforms
- How to add your own .m5o models for generating reports

## Using Docker

It is possible to run Meltano as a Docker container to simplify usage, deployment, and orchestration.

> This tutorial is inspired of the [Starter tutorial](#starter) but with Meltano running inside a Docker container.

We will use `docker run` to execute Meltano using the pre-built docker images.

### Initialize Your Project

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

### Analyze with Meltano UI

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
