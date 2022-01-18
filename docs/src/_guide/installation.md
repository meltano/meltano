---
title: Install Meltano
description: Learn how to install Meltano locally or using Docker.
layout: doc
weight: 1
---

If the installation instructions on the [homepage](/) or the [Getting Started guide](/getting-started/getting-started#install-meltano) did not work on your environment, or if you'd like to learn more about how to manage your Meltano installation, you've come to the right place.

<div class="notification is-warning">
    <p><strong>Short on time, or just curious what the fuss is about?</strong></p>
    <p>To get a sense of the Meltano experience in just a few minutes, follow the <a href="https://meltano.com">examples on the homepage</a> or watch the <a href="https://meltano.com/blog/2021/04/28/speedrun-from-0-to-elt-in-90-seconds/">"from 0 to ELT in 90 seconds" speedrun</a></p>
    <p>They can be copy-pasted right into your terminal and will take you all the way through <a href="/getting-started/installation">installation</a>, <a href="/tutorials/integration">data integration (EL)</a>, <a href="/reference/transforms">data transformation (T)</a>, <a href="/tutorials/orchestration">orchestration</a>, and <a href="/tutorials/containerization">containerization</a> with the <a href="https://hub.meltano.com/extractors/gitlab.html">tap-gitlab extractor</a> and the <a href="https://hub.meltano.com/loaders/jsonl.html">target-jsonl</a> and <a href="https://hub.meltano.com/loaders/postgres.html">target-postgres</a> loaders.</p>
</div>

## Local Installation

In this section, we will install Meltano locally on your system, so that you can use it [on the command line](/reference/command-line-interface) and [from your browser](/reference/ui).

### Requirements

Before you install Meltano, make sure you have the following requirements installed and up to date.

#### Unix-like environment

Recent versions of Linux and macOS are both fully supported, but Windows is not.

If you'd like to run Meltano on Windows, you can install it inside the [Windows Subsystem for Linux (WSL)](https://docs.microsoft.com/en-us/windows/wsl/about). You may also try [installing Meltano on Docker](#installing-on-docker), although Docker on Windows is known to have [some idiosyncrasies](https://gitlab.com/meltano/meltano/issues/1261#note_240256080) that might hinder Meltano's ability to function.

#### Python 3.6, 3.7, 3.8 or 3.9

<div class="notification is-info">
  <p>You may refer to <a href="https://realpython.com/installing-python/">https://realpython.com/installing-python/</a> for platform specific installation instructions.</p>
</div>

Use the following command to check that you have the correct Python version installed:

```bash
python --version
```

#### pip3

`pip` is a package installer that comes automatically with Python 3+. This is also what we will be using to install Meltano. Here are some commands related to `pip` that may be of interest:

```bash
# check for current version of pip to ensure that it is using Python 3
pip3 --version

# update pip3
pip3 install --upgrade pip
```

#### Virtual Environment

<div class="notification is-danger">
  <p><strong>IMPORTANT</strong></p>
  <p>Unless you are building a Docker image, it is **strongly recommended** that Meltano be installed inside a virtual environment in order to avoid potential system conflicts that may be difficult to debug.</p>
</div>

**Why use a virtual environment?**

Your local environment may use a different version of Python or other dependencies that are difficult to manage. The virtual environment provides a "clean" space to work without these issues.

#### Recommended Virtual Environment Setup

We suggest you create a directory where you want your virtual environments to be saved (e.g. `.venv/`). This can be any directory in your environment, but we recommend saving it in your Meltano project to make it easier to keep track of.

Then create a new virtual environment inside that directory:

```bash
mkdir .venv
python -m venv .venv/meltano
```

#### Activating Your Virtual Environment

Activate the virtual environment using:

```bash
source .venv/meltano/bin/activate
```

If the virtual environment was activated successfully, you'll see a `(meltano)` indicator added to your prompt.

<div class="notification is-info">
  <p>Once a virtual environment is activated, it stays active until the current shell is closed. In a new shell, you must re-activate the virtual environment before interacting with the <code>meltano</code> command that will be installed in the next step.</p>
  <p>To streamline this process, you can define a shell alias that'll be easier to remember than the entire activation invocation:</p>
<pre>
# add to `~/.bashrc`, `~/.zshrc`, etc, depending on the shell you use:
alias meltano!="source $MELTANO_PROJECT_PATH/.venv/meltano/bin/activate"

# use as follows, after creating a new shell:
meltano!
</pre>
  <p>You can deactivate a virtual environment by typing <code>deactivate</code> in your shell.</p>
</div>

### Install Meltano

Now that you have your virtual environment set up and running, run the following command to install the Meltano package:

```bash
pip3 install meltano
```

Once the installation completes, you can check if it was successful by running:

```bash
meltano --version
```

### Next Steps

Now that you've installed Meltano and its requirements, you can continue setting up your Meltano project by following the [Getting Started guide](/getting-started/getting-started#create-your-meltano-project).

## Installing on Docker

[Docker](https://www.docker.com/) is an alternative installation option to [using a virtual environment to run Meltano](#virtual-environment). To use these instructions you will need to [install Docker](https://docs.docker.com/install/) onto your computer and have it running when you execute the commands below.

### Using Pre-built Docker Images

We maintain the [`meltano/meltano`](https://hub.docker.com/r/meltano/meltano) Docker image on DockerHub, which comes with Python and Meltano pre-installed.

To get the latest version of Meltano, pull the `latest` tag. Images for specific versions of Meltano are tagged `v<X.Y.Z>`, e.g. `v1.55.0`.

By default, these images come with the oldest version of Python supported by Meltano, currently Python 3.6.
If you'd like to use a newer version of Python instead, add a `-python<X.Y>` suffix to the image tag, e.g. `latest-python3.8` and `v1.54.0-python3.7`.

```bash
# download or update to the latest version
docker pull meltano/meltano

# Or choose a specific version of Meltano and/or Python:
# docker pull meltano/meltano:v1.55.0
# docker pull meltano/meltano:latest-python3.7
# docker pull meltano/meltano:v1.55.0-python3.8

# check the currently installed version
docker run meltano/meltano --version
```

### Initialize Your Project

Once you have Docker installed, running, and have pulled the pre-built image you can use Meltano just as you would in our [Getting Started Guide](/getting-started/getting-started). However, the command line syntax is slightly different. For example, let's create a new Meltano project:

```bash
cd /your/projects/directory

docker run -v $(pwd):/projects \
             -w /projects \
             meltano/meltano init yourprojectname
```

Then you can `cd` into your new project:

```bash
cd yourprojectname
```

We can then start the Meltano UI. Since `ui` is the default command, we can omit it.

```bash
docker run -v $(pwd):/project \
             -w /project \
             -p 5000:5000 \
             meltano/meltano
```

You can now visit [http://localhost:5000](http://localhost:5000) to access the Meltano UI.

Now that you're successfully running Meltano, you can continue setting up your Meltano project by following the [Getting Started guide](/getting-started/getting-started).

Note that wherever you are asked to run the `meltano` command, you will want to run it through `docker run` as in the snippet above.

## Troubleshooting Installation

<div class="notification is-info">
  <p>Are you having installation or deployment problems? We are here to help you. Check out <a href="/getting-started/community">Getting Help</a> on the different ways to get in touch with us.</p>
</div>

## Upgrading Meltano Version

We release new versions of Meltano every week. To keep tabs on the latest releases, follow along on the [Meltano blog](https://meltano.com/blog/), or have a look at our [CHANGELOG](https://gitlab.com/meltano/meltano/blob/master/CHANGELOG.md).

### Using the command line

You can update Meltano to the latest version by running the following command in your terminal from inside a Meltano project:

```
meltano upgrade
```

### Using Meltano UI

When an update is available, you will be informed of this automatically through a shiny blue button in the top right corner of Meltano UI:

![Update Available Message](images/installation/update-available.png)

Clicking this button will show more information and give you the option to install the update right away:

![Update Available Popup](images/installation/update-available-popup.png)

The Meltano UI will refresh automatically once installation is complete.
