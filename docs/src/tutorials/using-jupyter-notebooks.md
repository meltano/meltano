---
sidebar: auto
metaTitle: Meltano Tutorial - Using Jupyter Notebooks with Meltano
description: Learn how to use a Jupyter Notebook as a part of a Meltano analysis workflow.
lastUpdatedSignificantly: 2020-02-20
---

# Using Jupyter Notebooks

Once the `meltano elt` pipeline has successfully completed and data extracted from an API or a Data Source have been transformed and loaded to the `analytics` schema of your Data Warehouse, you can use Meltano UI or any data exploration tool to analyze and generate reports.

In this tutorial, we are going to present how to connect [Jupyter Notebook](https://jupyter.org/) to a Meltano Project that uses Postgres to store the transformed data.

## Prerequisites

- Meltano's minimum and [optional requirements](/docs/installation.html#requirements) installed
- Docker started
- You have successfully extracted and loaded data from an API by following the steps described in the previous Tutorials.

## Jupyter Notebook Installation

If you have Jupyter already installed in your system, you can skip this step.

The most common options for [installing Jupyter Notebook](https://jupyter.org/install) are by either using Anaconda or pip3. We are going to use pip3 in this tutorial, as Meltano also uses pip3 for its installation.

::: tip Remember
If you used a virtual environment (`venv`) to install and run Meltano, don't forget to first navigate to the directory with your `venv` and run `source venv/bin/activate` to enable it.
:::

The following commands will install Jupyter Notebook and the most common python libraries required to connect to a Database (psycopg2, sqlalchemy), manipulate data (pandas) and generate some ad hoc plots (matplotlib):

```bash
pip3 install jupyter
pip3 install numpy
pip3 install pandas
pip3 install psycopg2
pip3 install sqlalchemy
pip3 install matplotlib
```

Once the installation is completed, you are set to use Jupyter Notebooks with Meltano.

## Set Your Credentials

Create a .env file in your project directory (i.e. sfdc-project) with the SFDC and Postgres DB credentials.

**.env**

```
export PG_PASSWORD=warehouse
export PG_USERNAME=warehouse
export PG_ADDRESS=localhost
export PG_PORT=5502
export PG_DATABASE=warehouse
```

This is an optional step, but allows us to use the same credentials from inside all Jupyter Notebooks without entering them again and, more importantly, without exposing any sensitive information inside the Notebook in case you want to share the Notebook with others.

## Running Jupyter Notebook

You can now navigate to Meltano's directory for storing your notebooks and [start Jupyter Notebook](https://jupyter.readthedocs.io/en/latest/running.html#running):

```bash
cd notebook/
jupyter notebook
```

This will print some information about the notebook server in your terminal, including the URL of the web application (by default, http://localhost:8888):

```bash
$ jupyter notebook
[I 13:18:36.606 NotebookApp] Serving notebooks from local directory: /home/iroussos/work/code/my-projects/jupyter-tutorial/notebook
[I 13:18:36.609 NotebookApp] The Jupyter Notebook is running at:
[I 13:18:36.610 NotebookApp] http://localhost:8888/
[I 13:18:36.612 NotebookApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).
```

It will then open your default web browser to this URL.

When the notebook opens in your browser, you will see the Notebook Dashboard, which will show a list of the notebooks, files, and subdirectories in the directory where the notebook server was started.

If this is the first time you start `jupyter notebook` from the `notebook` directory of your Meltano project, the list will be empty. Let's start a new Python notebook!

## Notebook Basics

While on the Notebook Dashboard, you can start a new Notebook by selecting `Python 3` from the `New` drop down menu.

We are going to showcase the most simple and straightforward way to connect to your `analytics` schema, fetch some transformed data and generate some plots.

The first step for a data exploration Notebook is to import the proper libraries required for data exploration and manipulation and then setup the connection to the Database (Postgres in our case) so that we can fetch data:

**Cell 1**

```python
# Import required libraries
import pandas as pd
import psycopg2
import sqlalchemy
import matplotlib as plt
import os

from sqlalchemy import create_engine

%matplotlib inline

# Get the Postgres username, password, and database name from the Environment
# You can also set them directly here, but it's better not to include passwords
#  or parameters specific to you inside the Notebook
POSTGRES_ADDRESS = os.getenv("PG_ADDRESS")
POSTGRES_PORT = os.getenv("PG_PORT")
POSTGRES_DBNAME = os.getenv("PG_DATABASE")
POSTGRES_USERNAME = os.getenv("PG_USERNAME")
POSTGRES_PASSWORD = os.getenv("PG_PASSWORD")

# Connect to the analytics schema, not one of the schemas with the raw data extracted
PG_SCHEMA = 'analytics'

# A long string that contains the necessary Postgres login information
postgres_str = ('postgresql://{username}:{password}@{ipaddress}:{port}/{dbname}'
                .format(username=POSTGRES_USERNAME,
                        password=POSTGRES_PASSWORD,
                        ipaddress=POSTGRES_ADDRESS,
                        port=POSTGRES_PORT,
                        dbname=POSTGRES_DBNAME))

# Create the connection
cnx = create_engine(postgres_str)
```

Click `|>| Run` and we are set to start exploring the data in brought in with Meltano.

You can then write queries and generate plots at will.

As an example, assume that you have loaded data from your Zendesk Account by using `tap_zendesk`. You can then check the most important Ticket statistics by month:

**Cell 2**

```python
# Query to send to the Database
sql_query = f'''
SELECT
  created_year || '-' || created_month as month,
  COUNT(*) as total_tickets,
  SUM(ticket_unsolved_counter) as unsolved_tickets,
  SUM(ticket_solved_counter) as solved_tickets,
  SUM(ticket_one_touch_counter) as one_touch_tickets,
  SUM(ticket_reopened_counter) as reopened_tickets,
  SUM(replies) as total_replies,
  ROUND(AVG(replies), 2) as avg_replies,
  ROUND(AVG(full_resolution_time_in_minutes_business), 2) as avg_res_time_mins

FROM {PG_SCHEMA}.zendesk_tickets_xf

GROUP BY created_year, created_month

ORDER BY created_year, created_month;
'''

# Execute the query and store the result in a pandas dataframe
result = pd.read_sql_query(sql_query, cnx)

# Print the result to the output to check what the query brought in
result
```

Or generate a bar plot:

**Cell 3**

```python
plt.rcParams['figure.figsize'] = [15, 8]
result.plot.bar(x='month', y=['total_tickets','unsolved_tickets','solved_tickets','one_touch_tickets','reopened_tickets'])
```

## Additional Resources

In order to make the most out of Jupyter Notebooks, you can check the following resources:

- [Documentation for pandas](https://pandas.pydata.org/), the Python Data Analysis Library that provides high-performance, easy-to-use data structures and data analysis tools for the Python programming language.
- [Pandas Tutorial using Jupyter Notebooks](https://data36.com/pandas-tutorial-1-basics-reading-data-files-dataframes-data-selection/)
- [Jupyter Notebook for Beginners: A Tutorial](https://www.dataquest.io/blog/jupyter-notebook-tutorial/)
