# Installation

Meltano is a powerful combination of command line tool and web app. It leverages the file system, coordinates across databases, and automates data extraction, loading, and transforming in addition to providing reporting and dashboarding. As such, installing and getting up and running takes a bit longer than double-clicking an installer. At least for now...

## Requirements

Minimum:
- [Python 3.6.1](https://realpython.com/installing-python/)

Optional:
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

::: tip Note
We currently require installing Meltano using Python 3's virtual environment (`venv` snippet below) to isolate it from the rest of your python packages.

See [this issue](https://gitlab.com/meltano/meltano/issues/141) for more information.
:::

Then run the following commands:
```bash
# create a virtual environment to run Meltano isolated from OS-level packages
$ python -m venv venv

# install Meltano in the aforementioned virtual environment
$ pip install meltano
```

```bash
$ meltano --help
Usage: meltano [OPTIONS] COMMAND [ARGS]
    …
```

That's it! Meltano is now be available in the virtual environment we setup. Now, we can [create a Meltano project](/docs/tutorial.html).

## Docker Images

We provide the [meltano/meltano](https://hub.docker.com/r/meltano/meltano) docker image with Meltano preinstalled and ready to use.

> Note: The **meltano/meltano** docker image is also available in GitLab's registry: `registry.gitlab.com`

This image contains everything you need to get started with Meltano.

```
# to download or update to the latest version
$ docker pull meltano/meltano

# to look the currently installed version
$ docker run meltano/meltano --version
meltano, version …
```

Please refer to the [docker tutorial](/docs/tutorial.html#using-docker) for more details.

## Troubleshooting

### Getting the Latest Version

To update Meltano to the latest version, run the following command in your terminal:

::: tip Remember
Run `source venv/bin/activate` to leverage the `meltano` installed in your virtual environment (`venv`) if you haven't already.
:::

```
pip install --upgrade meltano
```

:::warning Troubleshooting
Still having installation problems? Help us help you. Here is a [pre-baked form to streamline us doing so](https://gitlab.com/meltano/meltano/issues/new?issue%5Bassignee_id%5D=&issue%5Bmilestone_id%5D=&issuable_template=bugs).
:::
