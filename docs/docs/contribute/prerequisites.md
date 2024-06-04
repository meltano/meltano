---
title: Prerequisites
description: Meltano is open source software built by a growing team and a community of contributors.
layout: doc
sidebar_position: 2
sidebar_class_name: hidden
---

## Prerequisites

In order to contribute to Meltano, you will need the following:

1. [Python 3.8+](https://www.python.org/downloads/). For more details about Python requirements, refer to the ["Requirements" section](/getting-started/installation#requirements) of the Installation instructions, that also apply here.
2. [Node 16](https://nodejs.org/)
3. [Yarn](https://yarnpkg.com/)

## Setting Up Your Environment

```bash
# Clone the Meltano repo
git clone git@github.com:meltano/meltano.git

# Change directory into the Meltano project
cd meltano

# Install the Poetry tool for managing dependencies and packaging
pip3 install poetry

# Install all the dependencies
poetry install

# Install the pre-commit hook
poetry run pre-commit install --install-hooks

# Obtain a shell in the poetry created virtual environment
poetry shell
```

Meltano is now installed and available at `meltano`, as long as you remain in your virtual environment that you access
via `poetry shell`! Most editor's like [VSCode](https://code.visualstudio.com/) or [PyCharm](https://www.jetbrains.com/pycharm/)
can also be configured to detect and make use of virtualenv's, or even be configured to use poetry directly. That allows
meltano commands to work as you expect in editor based terminals, and is also typically required to enable advanced
editors features (debugging, code hints, etc).

You can also run meltano outside of an activated virtualenv by prefixing all commands with `poetry run` , e.g.
`poetry run meltano...`.

Note that for users who are using pyenv with the [virtualenv plugin](https://github.com/pyenv/pyenv-virtualenv) you will
likely not need to prefix the commands with `poetry` as poetry will default to using the pyenv activated virtual
environment.

This means that you're ready to start Meltano CLI development.

:::caution

  <p><strong>Metrics (anonymous usage data) tracking</strong></p>
  <p>As you contribute to Meltano, you may want to disable <a href="/reference/settings#send-anonymous-usage-stats">metrics tracking</a> globally rather than by project. You can do this by setting the environment variable `MELTANO_SEND_ANONYMOUS_USAGE_STATS` to `False`:</p>

```
# Add to `~/.bashrc`, `~/.zshrc`, etc, depending on the shell you use:
export MELTANO_SEND_ANONYMOUS_USAGE_STATS=False
```
:::

## System Database

Certain features of Meltano are supported by a database that is managed using Alembic migrations.

:::caution

  <p><strong><a href="https://alembic.sqlalchemy.org/en/latest/">Alembic</a> is a full featured database migration working on top of SQLAlchemy.</strong></p>
:::

Migrations for the system database are located inside the `meltano.migrations` module.

To create a new migration, use the `alembic revision -m "message"` command, then edit the created file with the necessary database changes. Make sure to implement both `upgrade` and `downgrade`, so the migration is reversible, as this will be used in migration tests in the future.

Each migration should be isolated from the `meltano` module, so **don't import any model definition inside a migration**.

:::danger

  <p><strong>Meltano doesn't currently support auto-generating migration from the models definition.</strong></p>
  <p></p>
:::

To run the migrations, use `meltano upgrade` inside a Meltano project.

## Resources

- [Managing Multiple Python Versions With pyenv](https://realpython.com/intro-to-pyenv/)
- [Managing environments with poetry](https://python-poetry.org/docs/managing-environments/)
- [Tmux Cheat Sheet & Quick Reference](https://tmuxcheatsheet.com/)

[accepting pull requests]: https://github.com/meltano/meltano/labels/accepting%20pull%20requests
