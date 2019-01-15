# Guide

## Introduction

Welcome to Meltano! Meltano is your solution for taking you from data source to dashboard. What does that mean? It means we have you covered through the entire data life cycle:

- Model
- Extract
- Load
- Transform
- Analyze
- Notebook
- Orchestrate

::: tip Tip
For developers who want to contribute to Meltano, check out our [contributing guide](/docs/contributing.html).
:::

## Requirements

Before you get started, there are a couple of things your environment needs:

- [Git](https://git-scm.com/)
- [Docker](https://www.docker.com/get-started)
- [Python 3](https://realpython.com/installing-python/)

## Installation

Meltano provides a CLI to kick start and help you manage the configuration and orchestration of all the components in the data life cycle. It provides a single source of truth for the entire data pipeline. The CLI makes it easy to develop, run, and debug every step of the data life cycle.

To start, open your terminal in the directory where you want Meltano to live. Run the following commands:

```bash
# Install Meltano from PyPi
pip install meltano
```

::: warning Note
If you're having issues with the `pip` command, try `pip3 install meltano` instead!
:::

That's it! Meltano should now be available in your local environment.
