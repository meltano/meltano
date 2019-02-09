# Tutorial

In this section, we will create and walk through a sample project using Meltano! If you haven't installed it, check out our [installation guide](/docs/installation.html).

## Initialize a New Project

Now it's time for you to set up a sample project!

Navigate to a directory, in your terminal, where you want your Meltano project to be installed and run the following commands:

```bash
# Initialize a new project with a folder called carbon
meltano init carbon

# Change directory into your new carbon project
cd carbon

# Start Docker container to setup logging
docker-compose up -d

# Set environment variables
source .env

# Let's see what extractors and loaders are available
meltano discover all

# Run elt (extract, load, transform) with an id of your choice and the extractor and
# loader we just added without the need to transform the data
meltano elt tap-carbon-intensity target-sqlite

# Start up the Meltano UI web application!
meltano ui
```

Assuming you don't have something else running on that port, you should be able to see Meltano UI at [http://localhost:5000](http://localhost:5000).

Now we are ready to analyze the data. We have provided some sample .m5o (Meltano UI) files that will help you analyze the carbon intensity API.

## Using Meltano on Your New Project

First, go to the Meltano UI [http://localhost:5000](http://localhost:5000)

::: warning Note
Follow the [installation](/docs/installation.html) steps if Meltano UI is not running
:::

Next, we'll ensure our models are valid so Meltano Analyze can properly generate queries for us:
- By default the Model page is loaded, same as clicking the Model button (upper-left)
    - Every time you go to this page, the models are linted, synced, and the UI updates with an error if a model is invalid. Otherwise you'll see the "Passed" indicator meaning you're clear to analyze.

Lastly, we'll query and explore the data:
- Navigate to Model > Region (Model dropdown)
- Open Region accordion
  - Toggle Columns and Aggregates buttons to generate SQL query
  - Click Run button to query
- Open Charts accordion and explore the data!
