# Local Installation

In this section, we will install Meltano as an application you can access locally from your browser and on the command line. If you prefer to install to Docker, please view the installation instructions [here](/docs/installation.html#installing-on-docker).

::: tip
We do not have a double click installer at this time, but it is in our roadmap and we will be sure to update this page when we do!
:::

## Requirements

Before you install Meltano, make sure you have the following requirements installed and up to date.

### Python 3+

- [Python 3.6.1+](https://realpython.com/installing-python/)

::: tip
You may refer to [https://realpython.com/installing-python/](https://realpython.com/installing-python/) for platform specific installation instructions.
:::

To check if you have the correct Python version, open your terminal and use the following commands to check the version:

```bash
python --version
```

If you've installed Python 3, but are not getting the result you expect, you may have installed Python 3 alongside an existing Python 2 installation. In this case, please use `python3` and `pip3` wherever this guide refers to the `python` and `pip` commands.

### pip

`pip` is a package installer that comes automatically with Python 3+. This is also what we will be using to install Meltano. Here are some commands related to `pip` that may be of interest:

```bash
# Check for current version of pip
pip --version

# Update pip
pip install --upgrade pip
```

::: tip
If you installed Python 3 alongside an existing Python 2 installation, you'll want to use `pip3` instead!
:::

### Virtual Environment

::: danger IMPORTANT
Unless you are building a Docker image, It is **strongly recommended** that Meltano be installed inside a virtual environment in order to avoid potential system conflicts that may be difficult to debug.
:::

**Why use a virtual environment?**

Your local environment may use a different version of Python or other dependencies that are difficult to manage. The virtual environment provides a "clean" space to work without these issues.

#### Recommended Virtual Environment Setup

We suggest you create a directory where you want your virtual environments to be saved, e.g.:

- **Linux, macOS**: `~/virtualenvs`
- **Windows**: `%ALLUSERSPROFILE%\\virtualenvs`

Then create a new virtual environment inside that directory:

```bash
# Linux, macOS
mkdir ~/virtualenvs
python -m venv ~/virtualenvs/meltano

# Windows
mkdir %ALLUSERSPROFILE%\\virtualenvs
python -m venv %ALLUSERSPROFILE%\\virtualenvs\\meltano
```

#### Activating Your Virtual Environment

Activate the virtual environment using:

```bash
# Linux, macOS
source ~/virtualenvs/meltano/bin/activate

# Windows
%HOME%\\virtualenvs\\meltano\\Scripts\\activate.bat
```

If the virtual environment was activated successfully, you'll see a `(meltano)` indicator added to your prompt.

::: tip
Once a virtual environment is activated, it stays active until the current shell is closed. In a new shell, you must re-activate the virtual environment before interacting with the `meltano` command that will be installed in the next step.

To streamline this process, you can define a [shell alias](https://shapeshed.com/unix-alias/) that'll be easier to remember than the entire activation invocation:

```bash
# Add to `~/.bashrc`, `~/.zshrc`, etc, depending on the shell you use:
alias meltano!="source ~/virtualenvs/meltano/bin/activate"

# Use as follows, after creating a new shell:
meltano!
```

:::

## Installing Meltano

Now that you have your virtual environment set up and running, run the following command to install the Meltano package:

```bash
pip install meltano
```

Once the installation completes, you can check if it was successful by running:

```bash
meltano --version
```

That's it! Meltano is now be available for you to use. Now we can [create a Meltano project](/docs/getting-started.html).

### Installing on Docker

[Docker](https://www.docker.com/) is an alternative installation option to [using a virtual environment to run Meltano](/docs/installation.html#virtual-environment). To use these instructions you will need to [install Docker](https://docs.docker.com/install/) onto your computer and have it running when you execute the commands below.

#### Using Pre-built Docker Images

We provide the [meltano/meltano](https://hub.docker.com/r/meltano/meltano) docker image with Meltano pre-installed and ready to use.

> Note: The **meltano/meltano** docker image is also available in GitLab's registry: `registry.gitlab.com`

This image contains everything you need to get started with Meltano.

```bash
# download or update to the latest version
docker pull meltano/meltano

# look the currently installed version
docker run meltano/meltano --version
```

#### Initialize Your Project

Once you have Docker installed, running, and have pulled the pre-built image you can use Meltano just as you would in our [Getting Started Guide](/docs/getting-started.html). However, the command line syntax is slightly different. For example, let's create a new Meltano project:

```
docker run -v $(pwd):/projects \
             -w /projects \
             meltano/meltano init YOUR_PROJECT_NAME
```

Then you can `cd` into your new project:

```
cd YOUR_PROJECT_NAME
```

We can then start the Meltano UI. Since `ui` is the default command, we can omit it.

```
docker run -v $(pwd):/project \
             -w /project \
             -p 5000:5000 \
             meltano/meltano
```

You can now visit [http://localhost:5000](http://localhost:5000) to access the Meltano UI.

If you are a Meltano end-user who is not going to be contributing code to our open source repository, you should be able to use Meltano entirely from the UI at this point.

Follow the steps in our [Getting Started Guide](/docs/getting-started.html) to get started.

#### For Contributors: Example Command Line Syntax for Docker

Here are some example of CLI commands you may need to run if you are working with Meltano as an open source contributor:

##### Running the ELT from the Command Line

To run the ELT and extract some data from the **tap-carbon-intensity** into **target-sqlite**:

```
docker run -v $(pwd):/project \
             -w /project \
             meltano/meltano elt tap-carbon-intensity target-sqlite
```

##### Adding a Model from the Command Line

Now that we have data in your database, let's add the corresponding model bundle as the basis of our analysis.

```
docker run -v $(pwd):/project \
             -w /project \
             meltano/meltano add model model-carbon-intensity-sqlite
```

## Upgrading Version

We release new versions of Meltano weekly. To update Meltano to the latest version, run the following command in your terminal:

```
pip install --upgrade meltano
```

Follow along on the [Meltano blog](https://meltano.com/blog/) to keep tabs on the latest releases, or visit our [CHANGELOG](https://gitlab.com/meltano/meltano/blob/master/CHANGELOG.md).

## Troubleshooting

Are you having installation or deployment problems? We are here to help you. Please fill out this [issue template](https://gitlab.com/meltano/meltano/issues/new?issue%5Bassignee_id%5D=&issue%5Bmilestone_id%5D=&issuable_template=bugs) and we'll get back to you as soon as we can!
