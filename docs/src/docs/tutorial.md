---
sidebarDepth: 2
---

# Tutorials

## Quick Start

First time using Meltano? No worries. We got you covered with tutorials that will guide you through how Meltano works. Let's get started!

### Carbon API

This tutorial is perfect if your goal is to get Meltano up and running as quickly as possible.

For this tutorial, we will be working with the [Carbon Intensity API](https://carbon-intensity.github.io/api-definitions/) because it is:
- free to access
- does not require authentication

### Initialize Your Project

Navigate to the directory in your terminal where you want your Meltano project to be installed. Then run the following commands:

```bash
# Initialize a new project with a folder called carbon
meltano init carbon

# Change directory into your new carbon project
cd carbon

# Let's see what extractors and loaders are available
meltano discover all

# Run elt (extract, load, transform) with an id of your choice and the extractor and
# loader we just added without the need to transform the data
meltano elt tap-carbon-intensity target-sqlite
```

Congratulations! You have just loaded all the data from Carbon Intensity API into your local warehouse.

### Interact with Your Data in the Web App

Now that your data is ready to be analyzed, it's time to start up the web app! Go back into your terminal and run the following command:

```bash
# Start up the Meltano UI web application!
$ meltano ui
```

This will start a local web server at [http://localhost:5000](http://localhost:5000).

When you visit the URL, you should see:

![](/screenshots/01-meltano-ui.png)

---
#### Run a Simple Analysis on Your Data

Meltano uses custom data files wth the extension `.m5o` that define the structure for your data.

In your project directory, you will see some examples under the `model` folder: `carbon.model.m5o`.




Next, we'll ensure our models are valid so Meltano Analyze can properly generate queries for us:

- By default the Model page is loaded, same as clicking the Model button (upper-left)
  - Every time you go to this page, the models are linted, synced, and the UI updates with an error if a model is invalid. Otherwise you'll see the "Passed" indicator meaning you're clear to analyze.

Lastly, we'll query and explore the data:

- Navigate to Model > Region (Model dropdown)
- Open Region accordion
  - Toggle Columns and Aggregates buttons to generate SQL query
  - Click Run button to query
- Open Charts accordion and explore the data!

## Salesforce API - Postgres DB Tutorial

This is an advanced tutorial on how to extract data from your Salesforce account, load the extracted entities to a Postgres DB, transform the raw data and analyze the result.

### Prerequisites

You have successfully installed Meltano by following the instructions in the [Installation](/docs/installation.html) section. Please note you should have already installed and started Docker.

### Initialize Your Project

To get started, navigate to a directory, in your terminal, where you want your Meltano project to be installed and run the following commands:

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


## Advanced Content

You can look forward to the following tutorials in the future:

- Salesforce > Snowflake Tutorial
- How to add your own transforms
- How to add your own .m5o models for generating reports
