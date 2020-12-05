---
description: Learn how to install Meltano locally or using Docker.
---

# Installation

If the installation instructions on the [homepage](/) or the [Getting Started guide](/docs/getting-started.html#install-meltano) did not work on your environment, or if you'd like to learn more about how to manage your Meltano installation, you've come to the right place.

::: tip Short on time, or just curious what the fuss is about?

To get a sense of the Meltano experience in just a few minutes, follow the [examples on the homepage](/).

They can be copy-pasted right onto your command shell and will take you all the way through
[installation](/#installation), [data integration (EL)](/#integration), [data transformation (T)](/#transformation), [orchestration](/#orchestration), and [containerization](/#containerization)
with the [`tap-gitlab` extractor](/plugins/extractors/gitlab.html)
and the [`target-jsonl`](/plugins/loaders/jsonl.html) and [`target-postgres`](/plugins/loaders/postgres.html) loaders.

:::

## Local Installation

In this section, we will install Meltano locally on your system, so that you can use it [on the command line](/docs/command-line-interface.html) and [from your browser](/docs/ui.html).

### Requirements

Before you install Meltano, make sure you have the following requirements installed and up to date.

#### Unix-like environment

Recent versions of Linux and macOS are both fully supported, but Windows is not.

If you'd like to run Meltano on Windows, you can install it inside the [Windows Subsystem for Linux (WSL)](https://docs.microsoft.com/en-us/windows/wsl/about). You may also try [installing Meltano on Docker](#installing-on-docker), although Docker on Windows is known to have [some idiosyncrasies](https://gitlab.com/meltano/meltano/issues/1261#note_240256080) that might hinder Meltano's ability to function.

#### Python 3.6, 3.7 or 3.8

::: tip
You may refer to [https://realpython.com/installing-python/](https://realpython.com/installing-python/) for platform specific installation instructions.
:::

Use the following command to check that you have the correct Python version installed:

```bash
python3 --version
```

#### pip3 and pipx

- `pip` is a package installer that comes automatically with Python 3+.
- [`pipx`](https://pipxproject.github.io/pipx/) is a wrapper around `pip` which cleanly installs
  executable python tools (such as Meltano) into their own virtual environments.

```bash
# install pipx and ensure it is on the path
python3 -m pip install --user pipx
pipx ensurepath
```

::: tip Why use pipx and virtual environments?

_Your local environment may use a different version of Python or other dependencies that are
difficult to manage. The pipx installer automatically creates a virtual environment and provides a
"clean" isolated space without version conflicts or other compatibility issues._

:::

### Install Meltano

Now that you have [pipx](https://pipxproject.github.io/pipx) installed, run the following command to install the Meltano package into its
own pipx-backed virtual environment:

```bash
pipx install meltano --include-deps
```

Once the installation completes, you can check if it was successful by running:

```bash
meltano --version
```

### Troubleshooting

- _If you have difficulty with pipx or if you prefer to create a custom virtual environment, see
  our instructions [here](#install-meltano-into-virtualenv)._

### Next Steps

Now that you've installed Meltano and its requirements, you can continue setting up your Meltano project by following the [Getting Started guide](/docs/getting-started.html#create-your-meltano-project).

## Installing on Docker

[Docker](https://www.docker.com/) is an alternative installation option to [using a virtual environment to run Meltano](#virtual-environment). To use these instructions you will need to [install Docker](https://docs.docker.com/install/) onto your computer and have it running when you execute the commands below.

### Using Pre-built Docker Images

We maintain the [`meltano/meltano`](https://hub.docker.com/r/meltano/meltano) Docker image on DockerHub, which comes with Python and Meltano pre-installed.

To get the latest version of Meltano, pull the `latest` tag. Images for specific versions of Meltano are tagged `v<X.Y.Z>`, e.g. `v1.55.0`.

By default, these images come with the oldest version of Python supported by Meltano, currently 3.6.
If you'd like to use Python 3.7 or 3.8 instead, add a `-python<X.Y>` suffix to the image tag, e.g. `latest-python3.8` and `v1.54.0-python3.7`.

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

Once you have Docker installed, running, and have pulled the pre-built image you can use Meltano just as you would in our [Getting Started Guide](/docs/getting-started.html). However, the command line syntax is slightly different. For example, let's create a new Meltano project:

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

Now that you're successfully running Meltano, you can continue setting up your Meltano project by following the [Getting Started guide](/docs/getting-started.html).

Note that wherever you are asked to run the `meltano` command, you will want to run it through `docker run` as in the snippet above.

## VirtualEnv-Based Install

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

Activate the virtual environment using:

```bash
source .venv/meltano/bin/activate
```

If the virtual environment was activated successfully, you'll see a `(meltano)` indicator added to
your prompt.

::: tip
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

:::

### Install Meltano into VirtualEnv

Now that you have your virtual environment set up and running, run the following command to install
the Meltano package:

```bash
pip3 install meltano
```

Once the installation completes, you can check if it was successful by running:

```bash
meltano --version
```

## Troubleshooting Installation

::: tip
Are you having installation or deployment problems? We are here to help you. Check out [Getting Help](/docs/getting-help.html) on the different ways to get in touch with us.
:::

## Upgrading Meltano Version

We release new versions of Meltano every week. To keep tabs on the latest releases, follow along on the [Meltano blog](https://meltano.com/blog/), or have a look at our [CHANGELOG](https://gitlab.com/meltano/meltano/blob/master/CHANGELOG.md).

### Using the command line

You can update Meltano to the latest version by running the following command in your terminal from inside a Meltano project:

```
meltano upgrade
```

### Using Meltano UI

When an update is available, you will be informed of this automatically through a shiny blue button in the top right corner of Meltano UI:

![](/screenshots/update-available.png)

Clicking this button will show more information and give you the option to install the update right away:

![](/screenshots/update-available-popup.png)

The Meltano UI will refresh automatically once installation is complete.
