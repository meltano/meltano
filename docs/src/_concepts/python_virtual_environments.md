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
we recommend using pipx to install Python, see our [Installation Guide](../_guide/installation.md).

However, if you ever need to customize or build your own production pipeline you may need to understand
how to install Meltano in an isolated way so that you don't conflict dependecies with your own Operating System
or other Python applications running on the same box

# How do I use Virtual Environments?

## Virtual Environment (venv) - Based Install of Meltano

If not using [pipx](https://pipxproject.github.io/), we strongly suggest you create a directory
where you want your virtual environments to be saved (e.g. `.venv/`). This can be any directory in
your environment, but we recommend saving it in your Meltano project to make it easier to keep
track of.

Then create a new virtual environment inside that directory:

```bash
mkdir .venv
python -m venv .venv/meltano
```

### Activating Your Virtual Environment

Activate the virtual environment, and upgrade pip using:

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

### Install Meltano into VirtualEnv

Now that you have your virtual environment set up and running, run the following command to install
the Meltano package:

```bash
pip3 install meltano
