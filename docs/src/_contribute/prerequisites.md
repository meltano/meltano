---
title: Prerequisites
description: Meltano is open source software built by a growing team and a community of contributors.
layout: doc
weight: 2
---

## Prerequisites

In order to contribute to Meltano, you will need the following:

1. [Python 3.7+](https://www.python.org/downloads/). For more details about Python requirements, refer to the ["Requirements" section](/guide/installation#requirements) of the Installation instructions, that also apply here.
2. [Node 8.11.0+](https://nodejs.org/)
3. [Yarn](https://yarnpkg.com/)

## Setting Up Your Environment

```bash
# Clone the Meltano repo
git clone git@gitlab.com:meltano/meltano.git

# Change directory into the Meltano project
cd meltano

# Install the Poetry tool for managing dependencies and packaging
pip3 install poetry

# Install all the dependencies
poetry install

# Install the pre-commit hook
poetry run pre-commit install --install-hooks

# Bundle the Meltano UI into the `meltano` package
make bundle
```

Meltano is now installed and available at `meltano`, as long as you remain in your `meltano-development` virtual environment!

This means that you're ready to start Meltano CLI development. For API and UI development, read on.

<div class="notification is-warning">
  <p><strong>Metrics (anonymous usage data) tracking</strong></p>
  <p>As you contribute to Meltano, you may want to disable <a href="/reference/settings#send-anonymous-usage-stats">metrics tracking</a> globally rather than by project. You can do this by setting the environment variable `MELTANO_DISABLE_TRACKING` to `True`:</p>
<pre>
# Add to `~/.bashrc`, `~/.zshrc`, etc, depending on the shell you use:
export MELTANO_DISABLE_TRACKING=True
</pre>
</div>



## System Database

Meltano API and CLI are both supported by a database that is managed using Alembic migrations.

<div class="notification is-warning">
  <p><strong><a href="https://alembic.sqlalchemy.org/en/latest/">Alembic</a> is a full featured database migration working on top of SQLAlchemy.</strong></p>
</div>

Migrations for the system database are located inside the `meltano.migrations` module.

To create a new migration, use the `alembic revision -m "message"` command, then edit the created file with the necessary database changes. Make sure to implement both `upgrade` and `downgrade`, so the migration is reversible, as this will be used in migration tests in the future.

Each migration should be isolated from the `meltano` module, so **don't import any model definition inside a migration**.

<div class="notification is-danger">
  <p><strong>Meltano doesn't currently support auto-generating migration from the models definition.</strong></p>
  <p></p>
</div>

To run the migrations, use `meltano upgrade` inside a Meltano project.



## Testing

### End-to-End Testing with Cypress

Our end-to-end tests are currently being built with [Cypress](https://www.cypress.io/).

#### How to Run Tests

1. Initialize a new meltano project with `meltano init $PROJECT_NAME`
1. Change directory into `$PROJECT_NAME`
1. Start up project with `meltano ui`
1. Clone Meltano repo
1. Open Meltano repo in Terminal
1. Run `yarn setup`
1. Run `yarn test:e2e`

This will kick off a Cypress application that will allow you to run tests as desired by clicking each test suite (which can be found in `/src/tests/e2e/specs/*.spec.js`)

![Preview of Cypres app running](images/contributor-guide/cypTest-01.png)

<div class="notification is-info">
  <p><strong>In the near future, all tests can flow automatically; but there are some complications that require manual triggering due to an inability to read pipeline completion.</strong></p>
  <p></p>
</div>

## Tmuxinator

Tmuxinator is a way for you to efficiently manage multiple services when starting up Meltano.

### Why Tmuxinator?

In order to run applications, you need to run multiple sessions and have to do a lot of repetitive tasks (like sourcing your virtual environments). So we have created a way for you to start and track everything in its appropriate panes with a single command.

1. Start up Docker
1. Start Meltano API
1. Start the web app

It's a game changer for development and it's worth the effort!

### Requirements

1. [tmux](https://github.com/tmux/tmux) - Recommended to install with brew
1. [tmuxinator](https://github.com/tmuxinator/tmuxinator)

This config uses `$MELTANO_VENV` to source the virtual environment from. Set it to the correct directory before running tmuxinator.

### Instructions

1. Make sure you know what directory your virtual environment is. It is normally `.venv` by default.
1. Run the following commands. Keep in mind that the `.venv` in line 2 refers to your virtual environment directory in Step #1.

```bash
cd path/to/meltano
MELTANO_VENV=.venv tmuxinator local
```

### Resources

- [Tmux Cheat Sheet & Quick Reference](https://tmuxcheatsheet.com/)

[Accepting Merge Requests]: https://gitlab.com/groups/meltano/-/issues?label_name[]=Accepting%20Merge%20Requests