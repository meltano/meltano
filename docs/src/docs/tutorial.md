# Tutorial

In this section, we will create and walk through a sample project using Meltano! If you haven't installed it, check out our [installation guide](/docs/#installation).

## Initialize a New Project

Now it's time for you to set up a sample project!

Navigate to a directory, in your terminal, where you want your Meltano project to be installed and run the following commands:

```bash
# Initialize a new project with a folder called carbon
meltano init carbon

# Change directory into your new carbon project
cd carbon

# Start Docker container, which will start a postgres database 
# to act as our data warehouse.
docker-compose up
```

Since Docker is running in this tab, let's open a new tab (and navigate to your project) for the rest of tutorial.

```bash
# Change directory to you new carbon project
cd carbon 

# Source the environment variables. You won't see any output if it's working.
source .env

# let's see what extractors and loaders are available
meltano discover all

# It looks like a tap for carbon intensity data is available, 
# let's add that as a dependency. See https://api.carbonintensity.org.uk/
meltano add extractor tap-carbon-intensity

# Since we have a postgres running, we can add a loader for a Postgres database
meltano add loader target-postgres

# Run elt (extract, load, transform) with an id of your choice and the extractor and
# loader we just added without the need to transform the data
meltano elt cool_job_id1 --extractor tap-carbon-intensity --loader target-postgres --transform skip

# Start up the Meltano Analyze web application!
meltano www
```

Assuming you don't have something else running on that port, you should be able to see Meltano Analyze at [http://localhost:5000](http://localhost:5000).

Now we are ready to analyze the data. We have provided some sample .ma (Meltano Analyze) files that will help you analyze the carbon intensity API. 

## Using Meltano on Your New Project

First, go to the Meltano UI [http://localhost:8080](http://localhost:8080)

::: warning Note
Follow the [installation](/docs/#installation) steps if Meltano UI is not running
:::

Next, we'll wire up our data warehouse to store data from the *carbon dataset*:
- Navigate to Settings (upper-right)
- Enter connection settings
  - Name = `runners_db`
  - Dialect = `PostgresSQL`
  - Host = `warehouse_db`
  - Port = `5502`
  - Database = `warehouse`
  - Schema = `gitlab`
  - Username = `warehouse`
  - Password = `warehouse`
- Click "Save Connection"

Then, we'll populate our data warehouse:
- Click Model button (upper-left)
- Click Validate button
- Click Update Database button

Lastly, we'll query and explore the data:
- Navigate to Model > Region (Model dropdown)
- Open Region accordion
  - Toggle Dimensions and Measures buttons to generate SQL query
  - Click Run button to query
- Open Charts accordion and explore the data!
