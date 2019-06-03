# Installation

In this section, we will install Meltano as an application you can access from your browser and command line. If you prefer to install to Docker, please view the installation instructions [here](/docs/meltano-cli.html#using-docker).

We do not have a double click installer at this time, but it is in our roadmap and we will be sure to update this page when we do!

## Requirements

Before you install meltano with `pip install meltano` make sure you have the following requirements installed and up to date.

### Python 3+

- [Python 3.6.1+](https://realpython.com/installing-python/)

You may refer to [https://realpython.com/installing-python/](https://realpython.com/installing-python/) for platform specific installation instructions.

To check if you have the correct Python version, open your terminal and use the following commands to check the version:

```bash
$ python --version
Python 3.6.1
```

### pip

`pip` is a package installer that comes automatically with Python 3+. This is also what we will be using to install Meltano. Here are some commands related to `pip` that may be of interest:

```bash
# Check for current version of pip
$ pip --version

# Update pip
$ pip install --upgrade pip
```

::: tip
If `pip`/`python` is not working, try `pip3`/`python3` instead. This would be the case if you have both Python 2+ *and* 3+ installed.
:::

### Virtual Environment

Meltano must be installed inside a virtual environment, unless you are building a Docker image.

We suggest you create a directory where you want your virtual environments to be saved, e.g.:
  - **Linux, OSX**:  `~/virtualenvs`
  - **Windows**: `%ALLUSERSPROFILE%\\virtualenvs`

Then create a new virtual environment inside that directory:

```bash
# Linux, OSX
$ mkdir ~/virtualenvs
$ python -m venv ~/virtualenvs/meltano

# Windows
$ mkdir %ALLUSERSPROFILE%\\virtualenvs
$ python -m venv %ALLUSERSPROFILE%\\virtualenvs\\meltano
```

Then, you will need to activate the virtual environment using:

```bash
# Linux, OSX
$ source ~/virtualenvs/meltano/bin/activate

# Windows
$ %HOME%\\virtualenvs\\meltano\\Scripts\\activate.bat
```

## Installing Meltano

Now that you have your virtual environment set up and running, navigate to the directory where you want to install Meltano and run the following command:

```bash
$ pip install meltano
```

Once the installation completes, you can check if it was successful by running:

```bash
$ meltano --version
meltano, version X.XX.X
```

That's it! Meltano is now be available for you to use. Now we can [create a Meltano project](/docs/quickstart.html).

::: tip
Once a virtual environment is activated, it stays active until the current shell is closed.

You must re-activate the virtual environment before interacting with Meltano. 
To streamline this process, you can add the `meltano` executable directly in your `PATH`.

```bash
# Linux, OSX
export PATH=$PATH:$HOME/virtualenvs/meltano/bin/meltano

# Windows
setx PATH "%PATH%;%ALLUSERPROFILES\virtualenvs\meltano\Scripts\meltano"
```
:::

## Troubleshooting

Are you having installation problems? We are here to help you. Please feel out this [issue template](https://gitlab.com/meltano/meltano/issues/new?issue%5Bassignee_id%5D=&issue%5Bmilestone_id%5D=&issuable_template=bugs) and we'll get back to you as soon as we can!

## Upgrading Version

We release new versions of Meltano weekly. To update Meltano to the latest version, run the following command in your terminal:

```
$ pip install --upgrade meltano
```

Follow along on the [Meltano blog](https://meltano.com/blog/) to keep tabs on the latest releases, or visit our [CHANGELOG](https://gitlab.com/meltano/meltano/blob/master/CHANGELOG.md).