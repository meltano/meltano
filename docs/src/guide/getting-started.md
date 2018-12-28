---
sidebar: auto
---

# Getting Started

## Introduction

Welcome to Meltano! Meltano is your solution for taking you from data source to dashboard. What does that mean? It means we have you covered through the entire data lifecycle:

- Model
- Extract
- Load
- Transform
- Analyze
- Notebook
- Orchestrate

::: warning Note
For developers who want to contribute to Meltano, check out our [contributing guide](/docs/contributing.html).
:::

## Prerequisites

Before you get started, there are a couple of things your environment needs:

- [Git](https://git-scm.com/)
- [Docker](https://www.docker.com/get-started)
- [Python 3](https://realpython.com/installing-python/)

## Step 1: Install Meltano CLI

Meltano provides a CLI to kickstart and help you manage the configuration and orchestration of all the components in the data lifecycle. It provides a single source of truth for the entire data pipeline. The CLI makes it easy to develop, run, and debug every step of the data lifecycle.

To start, open your terminal in the directory where you want Meltano to live. Run the following commands:

```bash
# Install Meltano from PyPi
pip install meltano
```

::: warning Note
If you're having issues with the `pip` command, try `pip3 install meltano` instead!
:::

That's it! Meltano should now be available in your local environment.

## Step 2: Initialize a New Sample Project

Now it's time for you to set up a sample project!

Navigate to a directory, in your terminal, where you want your Meltano project to be installed and run the following commands:

```bash
# Initialize a new project with a desired folder name
meltano init my-cool-data-project

# Change directory into your new cool project
cd my-cool-data-project

# Start Docker container, which will start a postgres database to act as our data warehouse.
docker-compose up
```

Since Docker is running in this tab, let's open a new tab (and navigate to your project) for the rest of tutorial.

```bash

cd /path/to/my-cool-data-project

# Source the environment variables. You won't see any output if it's working.
source .env

# let's see what extractors and loaders are available
meltano discover all

# It looks like a tap for carbon intensity data is available, let's add that as a dependency. See https://api.carbonintensity.org.uk/
meltano add extractor tap-carbon-intensity

# Since we have a postgres running, we can add a loader for a Postgres database
meltano add loader target-postgres

# Run elt (extract, load, transform) with an id of your choice and the extractor and loader we just added without the need to transform the data
meltano elt cool_job_id1 --extractor tap-carbon-intensity --loader target-postgres --transform skip

# Start up the Meltano application!
meltano ui
```

Assuming you don't have something else running on that port, you should be able to see Meltano Analyze at [http://localhost:5000](http://localhost:5000).

Now we are ready to analyze the data. We have provided some sample .ma (Meltano Analyze) files that will help you analyze the carbon intensity API. 

[Follow the instructions on our guide](https://meltano.com/guide/#using-the-meltano-sample-project).