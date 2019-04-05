# Tutorial - Loading CSV files to a Database

This tutorial explains how to load data stored in CSV files to a Postgres Database.

## Prerequisites

- Meltano's minimum and [optional requirements](./installation.html#requirements) installed
- Docker started
- Understanding how Transforms and Models work in Meltano. (!!! Link to `Custom Transforms and Models` Tutorial !!!)

## Initialize Your Project

To get started, navigate to a directory, in your terminal, where you want your Meltano project to be installed and run the following commands:

::: tip Remember
Run `source venv/bin/activate` to leverage the `meltano` installed in your virtual environment (`venv`) if you haven't already.
:::

```bash
# Initialize a new project with a folder called csv-project
meltano init csv-project

# Change directory into your new csv-project project
cd csv-project

# Start docker postgres instance
docker-compose up -d warehouse_db
```

## Set Your Credentials
Update the .env file in your project directory (i.e. csv-project) with your Postgres DB credentials and the file you are going to use to describe the CSV files to be loaded.

**.env**
```bash
export FLASK_ENV=development
export SQLITE_DATABASE=meltano

export PG_PASSWORD=warehouse
export PG_USERNAME=warehouse
export PG_ADDRESS=localhost
export PG_PORT=5502
export PG_DATABASE=warehouse

export PG_SCHEMA='csv_imports'

export TAP_CSV_FILES_DEFINITION="csv_files.json"
```

Where PG_SCHEMA is the schema that will be used to import the raw data to and TAP_CSV_FILES_DEFINITION (`csv_files.json` in the example) is a json file with all the CSV files to be loaded:

**csv_files.json**
```json
[   
  { "entity" : "leads",
    "file" : "/path/to/leads.csv",
    "keys" : ["Id"]
  },
  { "entity" : "opportunities",
    "file" : "/path/to/opportunities.csv",
    "keys" : ["Id"]
  }
]
```

Description of available options:
  - entity: The entity name, used as the table name for the data loaded from that csv.
  - file: Local path to the file to be ingested.
  - keys: The names of the columns that constitute the unique keys for that entity.

For example, assume that we have copied 3 csv files with data for users (`users.csv`), products (`products.csv`) and subscriptions (`subs.csv`) to the project directory we just created. `csv_files.json` would be like follows:

**csv_files.json**
```json
[   
  { "entity" : "users",
    "file" : "users.csv",
    "keys" : ["id"]
  },
  { "entity" : "products",
    "file" : "products.csv",
    "keys" : ["product_id"]
  },
  { "entity" : "subscriptions",
    "file" : "subs.csv",
    "keys" : ["id"]
  }
]
```


Finally, make the credentials available to Meltano by executing the following command in your terminal:

```bash
source .env
```

## Load the CSV files to Postgres

Run the Extract > Load pipeline:

```bash
meltano elt tap-csv target-postgres
```

The extracted data will be available to the Postgres schema defined by `PG_SCHEMA`.

In the example above, tables `users`, `products` and `subscriptions` will be available in the `csv_imports` schema, with all the data from the original CSV files loaded as records.

## Add Custom Transforms

(!!! Work In Progress !!!)
