# Old Installation Instructions

  - [Make](https://www.gnu.org/software/make/)
  - [Python](https://www.python.org/) (version >= 3.6.6)
  - [Docker](https://www.docker.com/get-started)
  - [docker-compose](https://docs.docker.com/compose/) (now included in Docker)

You can then build the Meltano docker images.

> Alternatively, Meltano provide built images on Docker Hub, you may find them at: https://hub.docker.com/r/meltano/meltano
> To use the prebuilt images, run the following command: `export DOCKER_REGISTRY=docker.io`

```bash
# build (or pull) the Meltano images
make

# initialize the db schema
make init_db

# bring up docker-compose
docker-compose up
```

This will start:

- The front-end UI at http://localhost:8080
- The API server http://localhost:5000
- Meltano API database at `localhost:5501`
- A mock warehouse database at `localhost:5502`

For more info see the [docker-compose.yml](https://gitlab.com/meltano/meltano/blob/master/docker-compose.yml) or skip to [*Using the Meltano Sample Project*](#using-the-meltano-sample-project)

#### Without Docker

##### Requirements

  - [Make](https://www.gnu.org/software/make/)
  - [Python](https://www.python.org/) (version >= 3.6.6)
  - [Docker](https://www.docker.com/get-started) (optional)
  - [docker-compose](https://docs.docker.com/compose/) (now included in Docker)
  - [Yarn](https://yarnpkg.com/en/) or [npm](https://www.npmjs.com/)
  - An available PostgreSQL instance

> Alternatively, you may use the provided database containers if you don't have an available PostgresSQL instance.
> Use `docker-compose up warehouse_db, api_db` to start them.

First, customize the `.env.example` with your database connection settings:

```bash
cp .env.example .env
```

**.env**:
```bash
export PG_DATABASE=warehouse
export PG_PASSWORD=warehouse
export PG_USERNAME=warehouse
export PG_ADDRESS=localhost
export PG_PORT=5502

export MELTANO_ANALYZE_POSTGRES_URL=localhost
export MELTANO_ANALYZE_POSTGRES_DB=meltano
export MELTANO_ANALYZE_POSTGRES_USER=meltano
export MELTANO_ANALYZE_POSTGRES_PASSWORD=meltano
export MELTANO_ANALYZE_POSTGRES_PORT=5501
```

Run the following in your project directory:

::: warning Note
**If you want to install Meltano in a venv: virtualenv and pipenv are not supported. Please use `python -m venv` to create your virtual environment. See [this issue](https://gitlab.com/meltano/meltano/issues/141).**
:::

```bash
# first, load your customized environment
source .env

# then create a virtualenv to isolate Meltano from your system's python
python3 -m venv .venv
source .venv/bin/activate

# then install the package from source
pip3 install -r requirements.txt
pip3 install -e '.[all]'

# or from PyPI
pip3 install -r requirements.txt
pip3 install 'meltano[all]'

# then seed the database
python3 -m meltano.api.init_db

# then start Meltano
python3 -m meltano.api
```

This starts the API server at [http://localhost:5000](http://localhost:5000)

Lastly, let's start the web server:

```bash
# install web server dependencies
cd src/analyze/
yarn install

# run the UI
yarn run dev
```

This starts the front-end UI at [http://localhost:8080](http://localhost:8080)

### Your First Meltano Project

After installing `meltano` CLI, you can choose to run meltano against your project.

The gitlab-runner project contains a `meltano.yml` file:

`meltano.yml`

```yml
version: 0.0.0 **
extractors:
- name: tap-gitlab
  url: https://gitlab.com/meltano/tap-gitlab
- name: tap-mysql
  url: https://gitlab.com/meltano/tap-mysql
- name: tap-zendesk
  url: https://gitlab.com/meltano/tap-zendesk
  ...
loaders:
- name: target-snowflake
  url: https://gitlab.com/meltano/target-snowflake
  database: main **
- name: target-postgresql
  url: https://gitlab.com/meltano/target-postgresql
  database: test **
  ...
databases:
- name: main
  username: "$MAIN_WAREHOUSE"
  password: "$MAIN_WAREHOUSE_PW"
  host: "$MAIN_WAREHOUSE_HOST"
  db: "$MAIN_WAREHOUSE_DB"
  type: snowflake
  ...
orchestrate: **
- name: first-to-csv
  extractor: first
  loader: csv
  transformer:
  - first
  ...
```

Your project should contains the following directory structure:

- model - For your `.lookml` files.
- transform - For your local dbt project files.
- analyze - For your `.yml` dashboard files.
- notebook - For your `.ipynb` notebook files.
- orchestrate - For your airflow `.py` files.
- .meltano - A .gitignored directory for internal caching (virtualenvs, pypi packages, generated configuration files, etc.).
- load - A directory where your configs for your loaders are placed. Each config should be in a directory with the name of the loader. e.g. For csv loader, the config would be in `load/target-csv/tap.config.json`. \*\*
- extract - A directory where your configs for your extractors are placed. Each config should be in a directory with the name of the extractor. e.g. For zendesk extractor, the config would be in `extract/tap-zendesk/target.config.json`. \*\*
- .gitignore
- README.md
- meltano.yml - Config file which shows which extractors and loaders, etc. you would like to use and where to find them.

Here is a sample of what your project might look like:

```
.
├── analyze
│   └── zendesk
│       └── zendesk.dashboard.yml
├── dbt_project.yml
├── extract
│   └── tap-...
│       ├── tap.config.json
│       └── tap.properties.json
├── load
│   └── target-...
│       └── target.config.json
├── .meltano
│   ├── dbt
│   │   └── venv
│   ├── extractors
│   │   └── tap-...
│   ├── loaders
│   │   └── target-...
│   ├── model
│   │   ├── base_ticket.lookml
│   │   └── ticket.lookml
│   └── run
│       ├── dbt
│       ├── tap-...
│       └── target-...
├── meltano.yml
├── model
│   └── zendesk
│       ├── zendesk.model.lookml
│       └── zendesk.view.lookml
├── orchestrate
│   ├── dag_1.py
│   ├── dag_2.py
│   ├── dag_3.py
│   ├── dag_4.py
│   └── dag_5.py
├── packages.yml
├── profiles.yml
└── transform
    └── tap-zendesk
        └── base.sql
```

Once you have your project, you can run `meltano` against it.

- `meltano init [project name]`: Create an empty meltano project.
- {: #meltano-add}`meltano add [extractor | loader] [name_of_plugin]`: Adds extractor or loader to your **meltano.yml** file and installs in `.meltano` directory with `venvs`, `dbt` and `pip`.
- `meltano install`: Installs all the dependencies of your project based on the **meltano.yml** file.
- `meltano discover all`: list available extractors and loaders:
  - `meltano discover extractors`: list only available extractors
  - `meltano discover loaders`: list only available loaders
- `meltano extract [name of extractor] --to [name of loader]`: Extract data to a loader and optionally transform the data
- `meltano transform [name of transformation] --warehouse [name of warehouse]`: \*\*
- `meltano elt <job_id> <extractor> <loader> [--dry]`: Extract, Load, and Transform the data.
- `meltano invoke <plugin_name> PLUGIN_ARGS...`: Invoke the plugin manually.
