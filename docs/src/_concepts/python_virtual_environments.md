---
title: Python Virtual Environments
description: What are Python Virtual Environments? Why should I care? How do I use them?
layout: doc
weight: 12 
---
# What are Python Virtual Environments

Python Virtual Environments also known as a venv (Pronounced: v-EHN-vah), are a way to allow a
Python application access to specefic versions of the libraries that it needs. In the singer ecosystem
you may need to install multiple Taps and Targets, which all of different dependencies. If any of those 
dependecies conflict with eachother you'd have a bad time without Virtual Envrionments. 

Python has a great technical write up at [Virtual Environments and Packages](https://docs.python.org/3/tutorial/venv.html). 

We're going to focus on the Meltano use case for Virtual Environments which is use for a two main purposes
1. Installing Meltano in an isolated environment
1. Installing Plugins (Taps, Targets, Transformers, etc) in isolated environments

# Why should I care about Virtual Environments?

Ideally you don't have to to worry about Virtual Environments while using Meltano, 
we recommend using pipx to install meltano which manages creating venvs for you, see our [Installation Guide](../_guide/installation.md).

However, if you ever need to customize or build your own production pipeline (Or do anything else) you may need to understand
how to install Meltano in an isolated way so that you don't conflict dependecies with your own Operating System
or other Python applications running on the same box

# How do I use Virtual Environments?

We strongly suggest you create a directory where you want your virtual environments to be saved (e.g. `.venv/`). 
This can be any directory in your environment, but we recommend saving it in your Meltano project to make it easier to keep
track of.

Then create a new virtual environment inside that directory:

```bash
mkdir .venv
python -m venv .venv/meltano
```

That's it! You've created a virtual environment. Feel free to explore the directory and compare it to your global python directory!

## Activating Your Virtual Environment

Activate the virtual environment, and upgrade pip using:

<div class="notification is-info">
  <p>Note that pip needs to be upgraded everytime you make a new venv, you want to do this to avoid hard to troubleshoot issues with dependencies later.</p>
</div>

```bash
source .venv/meltano/bin/activate
pip install --upgrade pip
```

If the virtual environment was activated successfully, you'll see a `(meltano)` indicator added to
your prompt.

Once a virtual environment is activated, it stays active until the current shell is closed. In a new
shell, you must re-activate the virtual environment before interacting with the `meltano` command
that will be installed in the next step.

To streamline this process, you can define a [shell alias](https://shapeshed.com/unix-alias/)
that'll be easier to remember than the entire activation invocation:

```bash
# add to `~/.bashrc`, `~/.zshrc`, etc, depending on the shell you use:
alias meltano!="source $MELTANO_PROJECT_PATH/.venv/meltano/bin/activate"
 
# use as follows, after creating a new shell:
meltano!
```

You can deactivate a virtual environment by typing `deactivate` in your shell.

### Install Meltano into a Virtual Environment

Now that you have your virtual environment set up and running, run the following command to install
the Meltano package:

```bash
pip3 install meltano
```

# How does meltano use Virtual Environments internally?

Whenever you run `meltano install`, Meltano creates a `.meltano/` directory in your project.
This folder has a number of sub folders (these folders are subject to change at any point as this is an internal folder).
In `.meltano/` you may see an `extractors/` folder that was created (if you have an extractor). 
Go into that folder, you'll see the name of a your tap, inside of that folder is a virtual environment! 

Each plugin is an application, so each of the steps we ran above to install Meltano is ran for each of your plugins when you run `meltano install`.
Meltano manages all of your plugins virtual environments for you! 
Pretty neat, no need to worry about any of that stuff yourself.
