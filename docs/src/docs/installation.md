# Installation

## Requirements

Before you get started, there are a couple of things your environment needs:

- [Git](https://git-scm.com/)
- [Docker](https://www.docker.com/get-started)
- [Python 3](https://realpython.com/installing-python/)

::: warning
If you want to install Meltano in a virtual environmnt: virtualenv and pipenv are not supported. Please use `python -m venv venv` to create your virtual environment. See [this issue](https://gitlab.com/meltano/meltano/issues/141) for more information.
:::

## Instructions

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
