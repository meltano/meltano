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

Go ahead and navigate to a directory separate from your Meltano directory in your terminal. Run the following commands:

```bash
# Initialize a new project with a desired folder name
meltano init my-cool-data-project

# Change directory into your new cool project
cd my-cool-data-project

# Start Docker container
docker-compose up

# Source the environment variables
source .env

# Add an extractor for carbon-intensity
meltano add extractor tap-carbon-intensity

# Add a loader for a Postgres database
meltano add loader target-postgres

# Run elt (extract, load, transform) with an id of your choice and the extractor and loader we just added without the need to transform the data
meltano elt cool_job_id1 --extractor tap-carbon-intensity --loader target-postgres --transform skip

# Start up the Meltano Analyze web application!
meltano www
```

Assuming you don't have something else running on that port, you should be able to see Meltano Analyze at [http://localhost:5001](http://localhost:5001).
