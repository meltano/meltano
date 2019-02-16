# Installation

## Requirements

Before you get started, there are a couple of things your environment needs:

- [Git](https://git-scm.com/)
- [Docker](https://www.docker.com/get-started)
- [Python 3.6.1](https://realpython.com/installing-python/)
- [pip](https://pypi.org/project/pip/)

::: warning
If you want to install Meltano in a virtual environment `virtualenv` and `pipenv` are not supported. Python 3 has built-in support for [virtual environments](https://docs.python.org/3/tutorial/venv.html) (see `venv`).

Please use `python -m venv venv` to create your virtual environment.

See [this issue](https://gitlab.com/meltano/meltano/issues/141) for more information.
:::

## Instructions

::: tip
If you're having issues with the `pip` command, try `pip3` instead!
:::

Meltano provides a CLI to kick start and help you manage the configuration and orchestration of all the components in the data life cycle. It provides a single source of truth for the entire data pipeline. The CLI makes it easy to develop, run, and debug every step of the data life cycle.

Let's make sure our requirements are up to date:

#### Python
You may refer to https://realpython.com/installing-python/ for platform specific installation instructions.

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

### Installation

Open your terminal in the directory where you want Meltano to live, then run the following command:

```
$ pip install meltano
```

```
$ meltano --help
Usage: meltano [OPTIONS] COMMAND [ARGS]
    …
```

That's it! Meltano should now be available in your local environment.
