# Salesforce Tutorials

## Salesforce > Postgres Tutorial

This is an advanced tutorial on how to extract data from your Salesforce account, load the extracted entities to a Postgres DB, transform the raw data and analyze the result.

### Prerequisites

You have successfully installed Meltano by following the instructions in the Installation section.

### Initialize Your Project

To get started, navigate to a directory, in your terminal, where you want your Meltano project to be installed and run the following commands:

```bash
# Initialize a new project with a folder called sfdc-project
meltano init sfdc-project 

# Change directory into your new sfdc-project project
cd sfdc-project

# Let's see what extractors and loaders are available
meltano discover all

# Add tap-salesforce (required as we'll want to select what will be extracted before running the meltano elt command)
meltano add extractor tap-salesforce

# Add target-postgres (optional: it will be added automatically by Meltano if it is not there when )
meltano add loader target-postgres
```

In contrast to the simple introducory tutorial for working with the Carbon Intensity API, in this case adding both `tap-salesforce` and `target-postgres` before running the `meltano elt` command is required, as we want to:

- Select which Salesforce Entities to Extract from Salesforce
- Set the credentials for your Salesforce account
- Set the credentials for your Postgres DB

### Select the Entities to export from Salesforce

A Salesforce Account may have available for extraction more than 100 different entities. Some of those are common between all Salesforce Accounts and some are unique or uniquely customized per Account.

Salesforce offers incredible customization to its customers, but there are still common threads we want to pull on for analytics. 

In this tutorial, we are going to work with a couple of the most common entities: Account, Contact, Lead, User, Opportunity and Opportunity History:

```bash
meltano select tap-salesforce "User" "*"
meltano select tap-salesforce "Account" "*"
meltano select tap-salesforce "Lead" "*"
meltano select tap-salesforce "Opportunity" "*"
meltano select tap-salesforce "OpportunityHistory" "*"
meltano select tap-salesforce "Contact" "*"
```

In general, when using Meltano, you can select which entities are extracted from a specific API.

(!! Add proper link to the documentation for the Select Command: https://www.meltano.com/docs/meltano-cli.html#meltano-select !!)


### Set your credentials

Update the .env file in your project directory with the SFDC and Postgres credentials.

```
export FLASK_ENV=development
export SQLITE_DATABASE=meltano

export PG_PASSWORD=warehouse
export PG_USERNAME=warehouse
export PG_ADDRESS=localhost
export PG_SCHEMA=meltano
export PG_PORT=5502
export PG_DATABASE=warehouse

export SFDC_URL=
export SFDC_USERNAME=''
export SFDC_PASSWORD=''
export SFDC_SECURITY_TOKEN=''
export SFDC_CLIENT_ID='secret_client_id'

export SFDC_START_DATE='2019-02-21T00:00:00Z'
```

You can leave `SFDC_URL` and `SFDC_CLIENT_ID` as they are in the example above, but you have to set `SFDC_USERNAME`, `SFDC_PASSWORD` and `SFDC_SECURITY_TOKEN` with the ones for your Salesforce Account. 

Set the `SFDC_START_DATE` to the earliest date you want to extract Opportunities and Leads for, by following the format in the example above (which stands for 21st of February, 2019).

Finally, make the credentials available to Meltano:

```bash
source .env
```

### Run elt (extract, load, transform)

Run the full Extract > Load > Transform pipeline:

```bash
meltano elt tap-salesforce target-postgres --transform run
```

Depending on your Account, the aforementioned command may take from a couple minutes to a couple hours. That's why we propose to set the `SFDC_START_DATE` not too far in the past for your first test.

You could also extract and load the data and then run the transformations at a later point (or run them again in case you have deleted something)

```bash
# Only run the Extract and Load steps
meltano elt tap-salesforce target-postgres

# Only run the Transform Step
meltano elt tap-salesforce target-postgres --transform only
```

The raw data extracted from Salesforce, are stored in the Database and Schema defined in your .env. Database `warehouse` and Schema: `meltano` in the example above.

The transform step uses the dbt transforms defined by default by [Mavatar's Salesforce dbt package](https://gitlab.com/meltano/dbt-tap-salesforce). Those transformations clean the raw tables and store them together with a join table to an `analytics` schema in the same Database.

You can check the section on how transforms work if you want to find more on how to change the default settings of the transform step or add additional transformations. 

(!! Add proper link to the documentation for Transforms: https://www.meltano.com/docs/meltano-cli.html#transforms !!)


### Interact with Your Data in the Web App

Now that your data is ready to be analyzed, it's time to start up the web app! Go back into your terminal and run the following command:

```bash
# Start up the Meltano UI web application!
$ meltano ui
```

This will start a local web server at [http://localhost:5000](http://localhost:5000). 

When you visit the URL, you will be using the default connection to Meltano's SQLite database. 

Let's add one more connection for your Postgres DB:

1. Navigate to Settings (upper-right) and select `Database`
1. Enter connection settings
  - Name = `postgres_db` (important to use that name)
  - Dialect = `PostgresSQl`
  - The rest of your Postgres creds
1. Click "Save Connection"

It's important to use the `postgres_db` name for the connection as it is used by default by the Salesforce Model used in Meltano UI.

You can now query and explore the extracted data:

- Navigate to `Analyze` > `sf opportunity history joined` (under SFDC in the drop-down)
- Toggle Columns and Aggregates buttons to generate the SQL query.
- Click the Run button to query the transformed tables in the `analytics` schema.
- Check the Results or Open the Charts accordion and explore the data!



## Salesforce > Snowflake Tutorial

Coming soon


## Advanced Content

Looking for even more advanced tutorials? You can look forward to the following tutorials in the future:

- Salesforce > Snowflake Tutorial
- How to add your own transforms
- How to add your own .m5o models for generating reports