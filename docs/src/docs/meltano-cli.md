# Meltano CLI

Meltano provides a CLI to kick start and help you manage the configuration and orchestration of all the components in the data life cycle.

Our CLI tool provides a single source of truth for the entire data pipeline. The CLI makes it easy to develop, run and debug every step of the data life cycle.

- `meltano add [extractor | loader ] [name_of_plugin]`: Adds extractor or loader to your **meltano.yml** file and installs in `.meltano` directory with `venvs` and `pip`.
- `meltano add [transform | transformer]`: Adds transform to your **meltano.yml** and updates the dbt packages and project configuration, so that the transform can run. Also used to install the `dbt` transformer for enabling transformations to run after extracting and loading data. 
- `meltano add model [name_of_model]`: Adds a model bundle to your **meltano.yml** and installs it inside the `.meltano` directory. Installed models are available to use in the Meltano UI.
- `meltano install`: Installs all the dependencies of your project based on the **meltano.yml** file.
- `meltano discover all`: list available extractors and loaders:
  - `meltano discover extractors`: list only available extractors
  - `meltano discover loaders`: list only available loaders
  - `meltano discover models`: list only available models
- `meltano extract [name of extractor] --to [name of loader]`: Extract data to a loader and optionally transform the data
- `meltano transform [name of transformation] --warehouse [name of warehouse]`: \*\*
- `meltano elt <extractor> <loader> [--dry] [--transform run]`: Extract, Load, and Transform the data.
- `meltano invoke <plugin_name> PLUGIN_ARGS...`: Invoke the plugin manually.
- `meltano select [--list] [--all] <tap_name> [ENTITIES_PATTERN] [ATTRIBUTE_PATTERN]`: Manage the selected entities/attribute for a specific tap.

## `init`

The `init` command is used to create a new meltano project with a basic infrastructure in place. 

### Example

```bash
# Format
meltano init [project_name] [--no_usage_stats]
```

### Parameters

* **project_name** - This determines the folder name for the project

### Options

* **no_usage_stats** - This flag disables sending anonymous usage data when creating a new project. 

::: tip
To disable tracking manually, you can add the following to the `meltano.yml` file:
```yaml
send_anonymous_usage_stats: false
```
:::

## Version

To check which version of Meltano you are using, run the following command:

```bash
meltano --version
```

To update Meltano to the latest version, run the following command in your terminal:

```bash
pip install --upgrade meltano
```

## meltano select

> Note: not all tap support this feature; tap needs to support the --discover switch.
> You can use `meltano invoke tap-... --discover` to see if the tap supports it.

Use this command to add select patterns to a specific extractor in your Meltano project.

### Select Pattern

Meltano select patterns are inspired by the [glob](https://en.wikipedia.org/wiki/Glob_(programming)) syntax you might find in your operating system.

  - `*`: matches any sequence of characters
  - `?`: matches one character
  - `[abc]`: matches either `a`, `b`, or `c`
  - `[!abc]`: matches any character **but** `a`, `b`, or `c`

#### Examples

> Note: Most shells parse glob syntax: you must escape the special characters in the select pattern by quoting the pattern.

```bash
$ meltano select tap-carbon-intensity '*' 'name*'
```

This will select all attributes starting with `name`.

```bash
$ meltano select tap-carbon-intensity 'region'
```

This will select all attributes of the `region` entity.

### --exclude

Use `--exclude` to exclude all attributes that match the filter.

> Note: exclusion has precedence over inclusion. If an attribute is excluded, there
> is no way to include it back without removing the exclusion pattern first.

#### Examples

```bash
$ meltano select --exclude tap-carbon-intensity '*' 'longitude'
$ meltano select --exclude tap-carbon-intensity '*' 'latitude'
```

This will exclude all `longitude` and `latitude` attributes.

### --list

Use `--list` to list the current selected tap attributes.

> Note: `--all` can be used to show all the tap attributes with their selected status.

## Transforms

Transforms in Meltano are implemented by using [dbt](https://www.getdbt.com/). All Meltano generated projects have a `transform/` directory, which is populated with the required configuration, models, packages, etc in order to run the transformations.

When Meltano elt runs with the `--transform run` option, the default dbt transformations for the extractor used are run.

As an example, assume that the following command runs:

```
meltano elt tap-carbon-intensity target-postgres --transform run
```

After the Extract and Load steps are successfuly completed and data have been extracted from the [Carbon Intensity API](https://api.carbonintensity.org.uk/) and loaded to a Postgres DB, the dbt transform runs. 

Meltano uses the convention that the transform has the same name as the extractor it is for. Transforms are automatically added the first time an elt operation that requires them runs, but they can also be discovered and added to a Meltano project manually:

```
(venv) $ meltano discover transforms

transforms
tap-carbon-intensity

(venv) $ meltano add transform tap-carbon-intensity
Transform tap-carbon-intensity added to your meltano.yml config
Transform tap-carbon-intensity added to your dbt packages
Transform tap-carbon-intensity added to your dbt_project.yml
```

Transforms are basically dbt packages that reside in their own repositories. If you want to see in more details how such a package can be defined, you can check the dbt documentation on [Package Management](https://docs.getdbt.com/docs/package-management) and [dbt-tap-carbon-intensity](https://gitlab.com/meltano/dbt-tap-carbon-intensity), the project used for defining the default transforms for `tap-carbon-intensity`.

When a transform is added to a project, it is added as a dbt package in `transform/packages.yml`, enabled in `transform/dbt_project.yml`, and loaded for usage the next time dbt runs.


The format of the `meltano.yml` entries for transforms can have additional parameters. For example, the `tap-carbon-intensity` dbt package requires three variables, which are used for finding the tables where the raw Carbon Intensity data have been loaded during the Extract-Load phase:

```
transforms:
- name: tap-carbon-intensity
  pip_url: https://gitlab.com/meltano/dbt-tap-carbon-intensity.git
  vars:
    entry_table: "{{ env_var('PG_SCHEMA') }}.entry"
    generationmix_table: "{{ env_var('PG_SCHEMA') }}.generationmix"
    region_table: "{{ env_var('PG_SCHEMA') }}.region"
```

Those entries may follow dbt's syntax in order to fetch values from environment variables. In this case, $PG_SCHEMA must be available in order for the transformations to know in which Postgres schema to find the tables with the Carbon Intensity data. Meltano uses $PG_SCHEMA by default as it is the same default schema also used by the Postgres Loader. 

You can keep those parameters as they are and provide the schema as an environment variable or set the schema manually in `meltano.yml`:

```
transforms:
- name: tap-carbon-intensity
  pip_url: https://gitlab.com/meltano/dbt-tap-carbon-intensity.git
  vars:
    entry_table: "my_raw_schema.entry"
    generationmix_table: "my_raw_schema.generationmix"
    region_table: "my_raw_schema.region"
```

When Meltano runs a new transformation, `transform/dbt_project.yml` is always kept up to date with whatever is provided in `meltano.yml`.

Finally, dbt can be configured by updating `transform/profile/profiles.yml`. By default, Meltano sets up dbt to use the same database and user as the Postgres Loader and store the results of the transformations in the `analytics` schema.

## meltano permissions 

Use this command to check and manage the permissions of a Snowflake account.

```bash
$ meltano permissions grant <spec_file> --db snowflake [--dry] [--diff]
```

Given the parameters to connect to a Snowflake account and a YAML file (a "spec") representing the desired database configuration, this command makes sure that the configuration of that database matches the spec. If there are differences, it will return the sql commands required to make it match the spec.

We currently support only Snowflake, as [pgbedrock](https://github.com/Squarespace/pgbedrock) can be used for managing the permissions in a Postgres database.

### spec_file

The YAML specification file is used to define in a declarative way the databases, roles, users and warehouses in a Snowflake account, together with the permissions for databases, schemas and tables for the same account.

Its syntax is inspired by [pgbedrock](https://github.com/Squarespace/pgbedrock), with additional options for Snowflake.

All permissions are abreviated as `read` or `write` permissions, with Meltano generating the proper grants for each type of object.

A specification file has the following structure:

```
# Databases
databases:
    - db_name:
        shared: boolean
    - db_name:
        shared: boolean
    ... ... ...

# Roles
roles:
    - role_name:
        warehouses:
            - warehouse_name
            - warehouse_name
            ...

        member_of:
            - role_name
            - role_name
            ...

        privileges:
            databases:
                read:
                    - database_name
                    - database_name
                    ...
                write:
                    - database_name
                    - database_name
                    ...
            schemas:
                read:
                    - database_name.*
                    - database_name.schema_name
                    ...
                write:
                    - database_name.*
                    - database_name.schema_name
                    ...
            tables:
                read:
                    - database_name.*.*
                    - database_name.schema_name.*
                    - database_name.schema_name.table_name
                    ...
                write:
                    - database_name.*.*
                    - database_name.schema_name.*
                    - database_name.schema_name.table_name
                    ...

        owns:
            databases:
                - database_name
                ...
            schemas:
                - database_name.*
                - database_name.schema_name
                ...
            tables:
                - database_name.*.*
                - database_name.schema_name.*
                - database_name.schema_name.table_name
                ...

    - role_name:
    ... ... ...

# Users
users:
    - user_name:
        can_login: boolean
        member_of:
            - role_name
            ...
    - user_name:
    ... ... ...

# Warehouses
warehouses:
    - warehouse_name:
        size: x-small
    ... ... ...
```

For a working example, you can check [the Snowflake specification file](https://gitlab.com/meltano/meltano/blob/master/tests/meltano/core/permissions/specs/snowflake_spec.yml) that we are using for testing `meltano permissions`.

### --db

The database to be used, either `postgres` or `snowflake`. Postgres is still experimental and may be fully supported in the future.

### --diff

When this flag is set, a full diff with both new and already granted commands is returned. Otherwise, only required commands for matching the definitions on the spec are returned.

### --dry

When this flag is set, the permission queries generated are not actually sent to the server and run; They are just returned to the user for examining them and running them manually.

Currently we are still evaluating the results generated by the `meltano permissions grant` command, so the `--dry` flag is required.

### Connection Parameters

The following environmental variables must be available to connect to Snowflake:

```
$PERMISSION_BOT_USER
$PERMISSION_BOT_PASSWORD
$PERMISSION_BOT_ACCOUNT
$PERMISSION_BOT_DATABASE
$PERMISSION_BOT_ROLE
$PERMISSION_BOT_WAREHOUSE
```

## How ELT Commands Fetch Dependencies

When you run ELT commands on a tap or target, this is the general process for fetching dependencies:

- First, the CLI looks in the project directory that you initialized
- Then it looks in the global file (`discovery.yml`) for urls of a package or repo
  - Note: This will eventually be moved into its own repository to prevent confusion since you cannot have local references for dependencies
- If this is the first time that the dependencies are requested, it will download to a local directory (if it is a package) or cloned (if it is a repo)
- By doing this, you ensure that packages are version controlled via `discovery.yml` and that it will live in two places:
  - in the project itself for the user to edit
  - in a global repo for meltano employees to edit
