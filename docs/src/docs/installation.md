# Installation

## Requirements

Meltano minimally requires:
- [Python 3.6.1](https://realpython.com/installing-python/)

Meltano conditionally requires:
- [Git](https://git-scm.com/) (if you want to version control your Meltano projects)
- [Docker](https://www.docker.com/get-started) (if you want to use databases other than SQLite)

## Instructions

Meltano provides a command line interface (CLI) to kick start and help you manage the configuration and orchestration of all the components in the data life cycle. It provides a single source of truth for the entire data pipeline. The CLI makes it easy to develop, run, and debug every step of the data life cycle.

Let's make sure our requirements are up to date:

#### Python
You may refer to [https://realpython.com/installing-python/](https://realpython.com/installing-python/) for platform specific installation instructions.

```
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
If `pip` is not working, try `pip3` instead. This would be the case if you have both Python 2+ *and* 3+ installed.
:::

### Installation

Open your terminal in the directory where you want Meltano to live. For example `/Users/YOUR_USER_NAME/Documents/Meltano`. Then run the following command:

```
$ pip install meltano
```

```
$ meltano --help
Usage: meltano [OPTIONS] COMMAND [ARGS]
    …
```

::: tip
If you want to install Meltano in a virtual environment `virtualenv` and `pipenv` are not supported. Python 3 has built-in support for [virtual environments](https://docs.python.org/3/tutorial/venv.html) (see `venv`).

Please use `python -m venv venv` to create your virtual environment.

See [this issue](https://gitlab.com/meltano/meltano/issues/141) for more information.
:::

That's it! Meltano should now be available in your local environment.

### Troubleshooting: Getting the Latest Version

To update Meltano to the latest version, run the following command in your terminal:

```
pip install --upgrade meltano
```

