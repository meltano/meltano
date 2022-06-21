---
title: Python Virtual Environments
description: What are Python Virtual Environments? Why should I care? How do I use them?
layout: doc
weight: 12
---
# What are Python Virtual Environments

Python Virtual Environments, also known as a venv, are a way to allow a
Python application access to specific versions of the libraries it needs to run properly. In the Singer ecosystem
you may need to install multiple Taps and Targets, which all have different dependencies.

If any of those dependecies are were in conflict with each other you would have a difficult development experience without Virtual Envrionments.

Python has a great technical write up at [Virtual Environments and Packages](https://docs.python.org/3/tutorial/venv.html).

We're going to focus on the Meltano use case for Virtual Environments which is use for a two main purposes:
1. Installing Meltano
1. Installing Plugins (Taps, Targets, Transformers, etc)

# Why should I care about Virtual Environments?

Ideally, you don't have to to worry about Virtual Environments while using Meltano,
we recommend using pipx to install Meltano which manages the creation of venvs for you.
See our [Installation Guide](/guide/installation) for more details.

However, if you ever need to customize or build your own production pipeline (or do anything else) you may need to understand
how to install Meltano in an isolated way so that you don't have a conflict with dependecies within your own Operating System
or other Python applications running on the same machine.

# How do I use Virtual Environments?

We strongly suggest you create a directory where you want your virtual environments to be saved (e.g. `.venv/meltano/`).
This can be any directory in your environment, but we recommend saving it in your Meltano project to make it easier to keep
track of.

Then create a new virtual environment inside that directory:

```bash
python -m venv .venv/meltano/
```

This `python` command is calling the `venv` package and it is creating a virtual environment in `.venv/meltano/`.

And that's it! You've created a virtual environment.
Feel free to explore the directory and compare it to your global python directory!
You can navigate to the directory by running `cd .venv/meltano/`.

## Activating Your Virtual Environment

Activate the virtual environment, and upgrade pip using:

```bash
source .venv/meltano/bin/activate
pip install --upgrade pip
```

<div class="notification is-info">
  <p>Note that pip needs to be upgraded every time you make a new venv. Doing this helps avoid hard to troubleshoot issues with dependencies later.</p>
</div>

If the virtual environment was activated successfully, you'll see a `(meltano)` indicator added to
your prompt.

Once a virtual environment is activated, it stays active until the current shell is closed. In a new
shell, you must re-activate the virtual environment before interacting with the `meltano` command
that will be installed in the next step.

You can deactivate a virtual environment by typing `deactivate` in your shell.

### Install Meltano into a Virtual Environment

Now that you have your virtual environment set up and running, run the following command to install
the Meltano package:

```bash
pip install meltano
```

<div class="notification is-info">
  <p>As a reminder, we do generally recommend using `pipx` for installing python packages.
Ensure you have `pipx` installed by reviewing the <a href="/guide/installation#install-pipx">Install pipx</a> instructions.</p>
</div>

# How does meltano use Virtual Environments internally?

Whenever you run `meltano install`, Meltano creates a `.meltano/` directory in your project.
This directory has a number of sub-directories (subject to change at any point, as this is an
internal directory).
In `.meltano/` you may see an `extractors/` directory that was created (if you
have an extractor).
In that directory you'll see the name of a your tap and inside of that
directory is a virtual environment!

Each plugin is an application, so each of the steps we ran above to install Meltano is ran for you for each plugin when you run `meltano install`.
Meltano manages all of your plugins virtual environments for you!
