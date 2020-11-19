# Alternative Virtual Environment Setup

If not using [pipx](https://pipxproject.github.io/), we strongly suggest you create a directory
where you want your virtual environments to be saved (e.g. `.venv/`). This can be any directory in
your environment, but we recommend saving it in your Meltano project to make it easier to keep
track of.

Then create a new virtual environment inside that directory:

```bash
mkdir .venv
python -m venv .venv/meltano
```

## Activating Your Virtual Environment

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

## Install Meltano

Now that you have your virtual environment set up and running, run the following command to install
the Meltano package:

```bash
pip3 install meltano
```

Once the installation completes, you can check if it was successful by running:

```bash
meltano --version
```
