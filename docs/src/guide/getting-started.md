---
sidebar: auto
---

# Getting Started

Welcome to Meltano! Meltano is your solution for taking you from data source to dashboard. What does that mean? It means we have you covered from:

- Model
- Extract
- Load
- Transform
- Analyze
- Notebook
- Orchestrate

## Prerequisites

Before you get started, there are a couple of things your environment has the following:

- [Git](https://git-scm.com/)
- [Docker](https://www.docker.com/get-started)
- [Python 3](https://realpython.com/installing-python/)

## Step 1: Install Meltano CLI

Meltano provides a CLI to kickstart and help you manage the configuration and orchestration of all the components in the data lifecycle. It provides a single source of truth for the entire data pipeline. The CLI makes it easy to develop, run and debug every step of the data lifecycle.

To start, open your terminal in the directory where you want Meltano to live. Run the following commands:

```bash
# Clone the repo
git clone https://gitlab.com/meltano/meltano

# Change directory to the fresh clone of Meltano
cd meltano

# Install Meltano locally
pip install .
```

That's it! Meltano should now be available on your local environment.

## Step 2: Initialize a New Sample Project

Now it's time for you to set up a sample project!

::: tip 
Before getting started on a Meltano project, make sure that Docker is up and running!
:::

Go ahead and navigate to a directory separate from your Meltano directory in your terminal. Run the following commands:

```bash
# Initialize a new project with a desired folder name
meltano init my-cool-data-project

# Change directory into your new cool project
cd my-cool-data-project

# Source the environment variables
source .env

# Add an extractor for carbon-intensity
meltano add extractor tap-carbon-intensity

# Add a loader for a Postgres database
meltano add loader target-postgres

# Run elt (extract, load, transform) with an id of your choice and the extractor and loader we just added without the need to transform the data
meltano elt cool_job_id1 --extractor tap-carbon-intensity --loader target-postgres --transform skip

# Start up Meltano analyze!
meltano www
```

Assuming you don't have something else running on that port, you should be able to see Meltano Analyze at [http://localhost:5001](http://localhost:5001).
