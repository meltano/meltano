# Installation

In this section, we will be installing Meltano as an application that you will be able to access on the command line (i.e., the terminal). We currently do not have a double click installer at this time, but it is in our roadmap and we will be sure to update this page when we have one!

## Requirements

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
# Check version of pip
$ pip --version
```

::: tip
If `pip`/`python` is not working, try `pip3`/`python3` instead. This would be the case if you have both Python 2+ *and* 3+ installed.
:::


## Instructions

1. Open your command line tool (i.e., Terminal for macOS)
2. Then run the following command:
```bash
$ pip install meltano
```
3. Once the installation, you can check if it was successful by running:
```bash
$ meltano --version
meltano, version X.XX.X
```

That's it! Meltano is now be available for you to use. Now we can [create a Meltano project](/docs/tutorial.html).

## Troubleshooting

Are you having installation problems? We are here to help you. Please feel out this [issue template](https://gitlab.com/meltano/meltano/issues/new?issue%5Bassignee_id%5D=&issue%5Bmilestone_id%5D=&issuable_template=bugs) and we'll get back to you as soon as we can!
