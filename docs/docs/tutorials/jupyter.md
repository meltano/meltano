---
title: How to use Jupyter with Meltano
description: Using jupyter Python notebook as transformation tooling or to run analyses across your meltano maintained data.
layout: doc
sidebar_position: 4
---

As of _Sep-2022_, jupyter is not yet available as utility on [Meltano Hub](https://hub.meltano.com/), so you need to add it to your Meltano project as (local) custom plugin. Even if it is available as plugin on the Hub, you will probably want to do some customization, so it will make sense to create your own version.

The steps involved are:

1. Add a (local) custom jupyter utility
2. Add potential Python libraries you will need
3. _Optional: Add database connection variables to be exposed into the environment_
4. Add Papermill or nbconvert to execute your data transformations & customize commands for jupyter to run the notebook
5. Execute your notebooks & add them to a schedule

_Steps 1-4 are customizing the meltano.yml to suit your setup, if you're comfortable with the process, read through them, and go straight for step 4 to copy & customize the yaml block from there, and you're ready to go._

## 1. Add a (local) custom jupyter utility

You can add a custom plugin either [via the CLI](https://docs.meltano.com/guide/plugin-management#custom-plugins) or [using the YAML file](https://docs.meltano.com/concepts/project#custom-plugin-definitions). As jupyter serves multiple purposes, the type "utility" is recommended as plugin type.

For Jupyter, you can choose both the "classic notebook" installed via the pip-package "jupyter" or the newer jupyterlab installed via the pip-package jupyterlab.

_Note: The code snippets will use jupyterlab, if you want the classic notebook, just replace jupyterlab=>jupyter, the "executable" stays the same._

Via the yaml file: add the follow code block inside your `meltano.yml` (ignore the _launch_ip0_ command if not necessary for you):

```yaml
plugins:
  utilities: # meltano invoke jupyter will start up the lab...
  - name: jupyterlab
    namespace: jupyterlab
    pip_url: jupyterlab
    executable: jupyter
    commands:
      launch_ip0: #important for Mac users running Meltano inside Docker.
        args: lab --ip=0.0.0.0
        description: Start lab server, on any ip range for Mac users inside docker.
      launch:
        args: lab
        description: Start lab server

```

Run `meltano install` to ensure the correctness of your yaml file. Then run `meltano invoke jupyterlab:launch` to launch the GUI.

Using the command line, you can also run `meltano add --custom utility jupyterlab` and interactively fill out these properties.

## 2. Add potential Python libraries you will need

To work with jupyter notebooks, you will end up using additional Python libraries which will generally fall into three categories

1. helper libraries like matplotlib or pandas
2. connection libraries like sqlAlchemy (and psycopg2)
3. And nbconvert or papermill to execute the notebook. These are handled in step 4.

To add additional Python libraries, extend the meltano.yml definition by space-separated pip-package names behind `pip_url: jupyterlab`. An example:

```yaml
plugins:
 utilities: # meltano invoke jupyter will start up the lab...
 - name: jupyterlab
   namespace: jupyterlab
   pip_url: jupyterlab pandas matplotlib sqlalchemy psycopg2-binary
   executable: jupyter
   commands:
     launch_ip0: #important for Mac users running Meltano inside Docker.
       args: lab --ip=0.0.0.0
       description: Start lab server, on any ip range for Mac users inside docker.
     launch:
       args: lab
       description: Start lab server

```

### 3. _Optional: Expore database connection variables into the environment_

To connect to datasources across different plugins it is useful to expose the connection details using environment variables. Meltano is able to do so in the meltano.yml. Here is an example configuration using plain text connection details:

```yaml
default_environment: dev
environments:
- name: dev
  config:
  env:
      PG_HOST: postgres
      PG_PORT: "5432"
      PG_DB: demo
      PG_USER: admin
      PG_PWD: password
```

You can read more on [Meltano and environment variables here](https://docs.meltano.com/guide/configuration#environment-variables).
These variables will then be accessible inside your jupyter notebooks. E.g.

```python
import os

PG_HOST = os.getenv("PG_HOST", default=None)
PG_PORT = os.getenv("PG_PORT", default=None)
PG_DB = os.getenv("PG_DB", default=None)
PG_USER = os.getenv("PG_USER", default=None)
PG_PWD = os.getenv("PG_PWD", default=None)

```

### 4. Execute notebooks via nbconvert or papermill

Whether your notebook is outputting machine learning accuracy data, a business intelligence report or is transforming data inside your data warehouse, you will likely want to be able to execute it without the GUI, using either:

- a CLI
- or automatic via the Meltano scheduler.

Jupyter and jupyterlab both offer "nbconvert" as default option to execute notebook. You can also use the additional Python package [papermill](https://papermill.readthedocs.io/en/latest/index.html). Papermill allows you to execute and parametrize notebooks for execution, while nbconvert only does execution.

If you want to use "nbconvert" you will want to add a command to the plugin, replace "notebook/sql_magic.ipynb" with your notebook path:

```yaml
  - name: jupyterlab
    namespace: jupyterlab
    pip_url: jupyterlab pandas matplotlib sqlalchemy psycopg2-binary papermill
    executable: jupyter
    commands:
      launch_ip0:
        args: lab --ip=0.0.0.0
        description: Start lab server, on any ip range for Mac users inside docker.
      launch:
        args: lab
        description: Start lab server
      execute:
        args: nbconvert --to notebook --execute notebook/sql_magic.ipynb
        description: Start lab server
```

You can then execute with `meltano invoke jupyterlab:execute`

If you want to use papermill, the easiest option is to use [plugin inheritance](https://docs.meltano.com/concepts/project#inheriting-plugin-definitions) to reuse the venvs created for each plugin. That way, you will not need to install jupyterlabs and all the dependencies twice. Here's an example yaml block:

```yaml
  - name: papermill
    inherit_from: jupyterlab
    executable: papermill
    commands:
      execute:
        args: notebook/sql_magic.ipynb output/output.ipynb -p price_1 1000
        description: Start lab server, on any ip range for Mac users inside docker.
```

You will need to adapt the "args" to your notebook path, output path and parameters. The example notebook here has one cell with a defined parameter "price_1" which we are able to override from the outside. For details, refer to the (pleasently short) [documentation from papermill](https://papermill.readthedocs.io/en/latest/usage-parameterize.html), it's a simple process.

### 5. Execute & schedule your notebooks

Putting it all together, you will end up with a meltano.yml like this:

```yaml
plugins:
  utilities: # meltano invoke jupyter will start up the lab...
  - name: jupyterlab
    namespace: jupyterlab
    pip_url: jupyterlab pandas matplotlib sqlalchemy psycopg2-binary papermill
    executable: jupyter
    commands:
      launch_ip0:
        args: lab --ip=0.0.0.0
        description: Start lab server, on any ip range for Mac users inside docker.
      launch:
        args: lab
        description: Start lab server
      execute:
        args: nbconvert --to notebook --execute notebook/sql_magic.ipynb
        description: Start lab server

  - name: papermill
    inherit_from: jupyterlab
    executable: papermill
    commands:
      execute:
        args: notebook/sql_magic.ipynb output/output.ipynb -p price_1 1000
        description: Start lab server, on any ip range for Mac users inside docker.
```

Then execute `meltano invoke papermill:execute` to run your notebook and possibly include it in your meltano pipeline.
