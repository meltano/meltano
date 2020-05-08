---
metaTitle: Getting Started with the Meltano CLI
description: The Meltano command line interface makes it easy to develop, run, and debug every step of the data analysis lifecycle.
sidebarDepth: 2
lastUpdatedSignificantly: 2020-05-07
---

# Getting Started

Once you have successfully [installed Meltano](/docs/installation.html) from the command line, you will need to create a project before you launch the Meltano UI.

## Create your first project

To initialize a new project, open your terminal and navigate to the directory that you'd like to store your Meltano projects in.

Use the `meltano init` command, which takes a `PROJECT_NAME` that is of your own choosing. For this guide, let's create a project called "myprojectname".

```bash
meltano init myprojectname
```

This will create a new directory named `myprojectname` in the current directory and initialize Meltano's basic directory structure inside it.

Inside the Meltano project directory, all plugin configuration (which may include tokens and passwords) is stored inside the `.meltano` directory, which is automatically added to the project's `.gitignore` file to prevent this potentially sensitive information from accidentally being pushed up to a hosted Git repository.

## Setup your loader

Self-hosted Meltano instances require you to set up a reporting database and configure Meltano to use it by installing a **Loader**.

Meltano has basic support for a [few different loaders](/plugins/loaders/), but dashboards and reports are only supported with [PostgreSQL](/plugins/loaders/postgres.html).

You will find detailed instructions in the docs for your loader of choice.

## Start the application

Now that you've created your first Meltano project, let's change directory to our new project and start Meltano UI:

```bash
cd myprojectname
meltano ui
```

Meltano is now running and should open a new tab at [http://localhost:5000](http://localhost:5000).

Now that you have access to the Meltano UI, [use our Getting Started with Data Analysis guide](/docs/analysis.html#connect-data-sources) to learn more about how to use the software.
