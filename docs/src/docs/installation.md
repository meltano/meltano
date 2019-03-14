# Installation

## Requirements

Minimum:
- [Python 3.6.1](https://realpython.com/installing-python/)

Additional:
- [Git](https://git-scm.com/): to version control your Meltano project
- [Docker Desktop](https://www.docker.com/get-started): to create a sample/default database

## Instructions

Meltano provides a command line interface (CLI) to kick start and help you manage the configuration and orchestration of all the components in the data life cycle. It provides a single source of truth for the entire data pipeline. The CLI makes it easy to develop, run, and debug every step of the data life cycle.

Let's make sure our requirements are up to date:

#### Python
You may refer to [https://realpython.com/installing-python/](https://realpython.com/installing-python/) for platform specific installation instructions.

```bash
$ python --version
Python 3.6.1
```

#### pip
Run `pip install --upgrade pip` to update `pip` to the latest version.

```bash
$ pip --version
pip 10.0.1 from … (python 3.6)
```

::: tip
If `pip`/`python` is not working, try `pip3`/`python3` instead. This would be the case if you have both Python 2+ *and* 3+ installed.
:::

### Installation

Open your terminal in the directory where you want Meltano installed. For example `/Users/YOUR_USER_NAME/Documents/Meltano`.

::: tip
We highly recommend installing Meltano using Python 3's virtual environment (`venv` snippet below). Doing so prevents Meltano's dependencies from clashing with current versions already installed on your machine.

See [this issue](https://gitlab.com/meltano/meltano/issues/141) for more information.
:::

Then run the following commands:
```bash
$ python -m venv venv

$ pip install meltano
```

```bash
$ meltano --help
Usage: meltano [OPTIONS] COMMAND [ARGS]
    …
```

That's it! Meltano is now be available in the virtual environment we setup. Now, we can [create a Meltano project](/docs/tutorial.html).

## Troubleshooting

Are you having installation problems? Help us help you. Here is a [pre-baked form to streamline us doing so](https://gitlab.com/meltano/meltano/issues/new?issue%5Bassignee_id%5D=&issue%5Bmilestone_id%5D=&issuable_template=bugs).