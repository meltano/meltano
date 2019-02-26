# CHANGELOG

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/) and [Keep a Changelog](http://keepachangelog.com/).



## Unreleased
---

### New
* Update stages table style in docs

### Changes

### Fixes
* Resolved duplicate display issue of Dashboards and Reports on the Files page
* Removed legacy `carbon.dashboard.m5o` (regression from merge)
* Updated dashboards and reports to use UI-friendly name vs slugified name

### Breaks


## 0.13.0 - (2019-02-25)
---

### New
* Add the `tap-salesforce` transform to Meltano. It is using the dbt package defined in https://gitlab.com/meltano/dbt-tap-salesforce
* Add m5o model and tables for tap-salesforce
* Updated the deep-link icon (for Dashboards/Reports on the Files page)

### Changes
* Polished the RBAC view, making it clearer the feature is experimental.
* Rename "Models" to "Topics"
* Use the current connection's schema when generating queries at run time for Postgres Connections.
* Add support for multiple Aggregates over the same attribute when generating HDA queries.


## 0.12.0 - (2019-02-21)
---

### New
* UI cleanup across routes (Analyze focus) and baseline polish to mitigate "that looks off comments"
* Update installation and contributing docs
* Meltano implement role-based access control - [!368](https://gitlab.com/meltano/meltano/merge_requests/368)
* Add version CLI commands for checking current Meltano version
* Add deep linking to dashboards
* Add deep linking to reports

### Fixes
* Fixed a problem when environment variables where used as default values for the CLI - [!390](https://gitlab.com/meltano/meltano/merge_requests/390)
* Fixed dashboards initial load issue due to legacy (and empty) `carbon.dashboard.m5o` file
* New standardized approach for `.m5o` id generation (will need to remove any dashboard.m5o and report.m5o)


## 0.11.0 - (2019-02-19)
---

### New
* Update installation and contributing docs
* Add support for generating Hyper Dimensional Aggregates (HDA)
* Add internal Meltano classes for representing and managing Designs, Table, Column, Aggregate, Definitions, and Query definitions

### Changes
* Move core functionality out of `api/controllers` to `/core/m5o` (for m5o and m5oc management) and `/core/sql` (for anything related to sql generation)

### Fixes
* Fixed a problem when environment variables where used as default values for the CLI - [!390](https://gitlab.com/meltano/meltano/merge_requests/390)


## 0.10.0 - (2019-02-12)
---

### New
* Add gunicorn support for Meltano UI as a WSGI application - [!377](https://gitlab.com/meltano/meltano/merge_requests/377)
* Meltano will now generate the minimal joins when building SQL queries  - [!382](https://gitlab.com/meltano/meltano/merge_requests/382)

### Changes
* Add analytics to authentication page
* Meltano will now use SQLite for the job log. See https://meltano.com/docs/architecture.html#job-logging for more details.
* Removed manual `source .env` step in favor of it running automatically

### Fixes
* Meltano will correctly source the `.env`
* fixed charts to render as previously they were blank
* Fixed Analyze button groupd CSS to align as a single row

### Breaks
* Meltano will now use SQLite for the job log. See https://meltano.com/docs/architecture.html#job-logging for more details.
* URL routing updates ('/model' to '/files', removed currently unused '/extract', '/load', '/transform' and '/project/new')


## 0.9.0 - (2019-02-05)
---

### New
* add ability to save reports
* add ability to update an active report during analysis
* add ability to load reports
* add dashboards page and related add/remove report functionality

### Changes
* Generate default `Meltano UI` connection for the `meltano.db` SQLite DB when a new project is created with `meltano init`
* updated main navigation to Files, Analysis, and Dashboards
* Update the `meltano permissions grant` command to fetch the existing permissions from the Snowflake server and only return sql commands for permissions not already assigned
* Add `--diff` option to the `meltano permissions grant` command to get a full diff with the permissions already assigned and new ones that must be assigned

### Fixes
* Entry model definition correctly defines `region_id`.
* Updated the Fundamentals documentation section regarding reports
* Fixed Files page for empty state of Dashboards and Reports
* Fixed Analyze page's left column to accurately preselect columns and aggregates after loading a report


## 0.8.0 - (2019-01-29)
---

### New
* Add tracking of anonymous `meltano cli` usage stats to Meltano's Google Analytics Account
* Add `project_config.yml` to all meltano projects to store concent for anonymous usage tracking and the project's UUID

### Changes
* Add `--no_usage_stats` option to `meltano init <project_name>` to allow users to opt-out from anonymous usage stats tracking
* Bundled Meltano models are now SQLite compatible.


## 0.7.0 - (2019-01-22)
---

### New
* Added basic authentication support for meltano ui.
* Meltano will now automatically source the .env
* Updated docs with `.m5o` authoring requirements and examples
* add support for timeframes in tables
* add basic analytics to understand usage
* add disabled UI for the lack of timeframes support in sqlite
* update Results vs. SQL UI focus based on a results response or query update respectively

### Changes
* Meltano will now discover components based on `https://meltano.com/discovery.yml`
* sample designs are now packaged with meltano

### Fixes
* Updated mobile menu to work as expected
* Updated tutorial docs with improved CLI commands and fixed the host setting to `localhost`


## 0.6.1 - (2019-01-15)
---

## 0.6.0 - (2019-01-15)
---

### New
* add new command `meltano add transform [name_of_dbt_transformation]`
* add transforms to the available plugins

### Changes
* Auto install missing plugins when `meltano elt` runs
* Terminology updates for simpler understanding

### Fixes
* Edit links on the bottom of doc pages are working now

### Breaks
* Updated docs tutorial bullet regarding inaccurate "Validate" button


## 0.5.0 - (2019-01-09)
---

### New
* ensure `meltano init <project-name>` runs on windows
* settings ui now provides sqlite-specific controls for sqlite dialect
* add `target-sqlite` to available loaders for meltano projects
* add new command `meltano add transformer [name_of_plugin]`
* add transformers (dbt) to the available plugins

### Changes
* extractors and loaders are arguments in the elt command instead of options
* `meltano www` is now `meltano ui`
* remove dbt installation from `meltano init`
* move everything dbt related under `transform/`
* update `meltano elt` to not run transforms by default
* update `meltano elt` to auto generate the job_id (job_id has been converted to an optional argument)

### Fixes
* left joins now work correctly in analyze.
* fixed broken sql toggles in analyze view
* fixed sql output based on sql toggles in analyze view


## 0.4.0 - (2019-01-03)
---

### New
* add Using Superset with Meltano documentation


## 0.3.3 - (2018-12-21)
---

## 0.3.2 - (2018-12-21)
---

## 0.3.1 - (2018-12-21)
---

### Changes
* add default models for 'tap-carbon-intensity'.
* Meltano Analyze is now part of the package.
* removes database dependency from Meltano Analyze and uses .ma files
* update the error message when using Meltano from outside a project - [!238](https://gitlab.com/meltano/meltano/merge_requests/238)


## 0.3.0 - (2018-12-18)
---

### New
* updated Settings view so each database connection can be independently disconnected
* add `meltano select` to manage what is extracted by a tap.

### Changes
* documentation site will utilize a new static site generation tool called VuePress

* meltano.com will be deployed from the meltano repo

### Fixes
* model dropdown now updates when updating database (no longer requires page refresh)
* prevent model duplication that previously occurred after subsequent "Update Database" clicks


## 0.2.2 - (2018-12-11)
---

### Changes

* documentation site will utilize a new static site generation tool called VuePress
* first iteration of joins (working on a small scale)


## 0.2.1 - (2018-12-06)
---

### Fixes
* resolve version conflict for `idna==2.7`
* fix the `discover` command in the docker images
* fix the `add` command in the docker images
* fix module not found for meltano.core.permissions.utils


## 0.2.0 - (2018-12-04)
---

### New
* add `meltano permissions grant` command for generating permission queries for Postgres and Snowflake - [!90](https://gitlab.com/meltano/meltano/merge_requests/90)
* add 'tap-stripe' to the discovery

### Changes
* demo with [carbon intensity](https://gitlab.com/meltano/tap-carbon-intensity), no API keys needed
* .ma file extension WIP as alternative to lkml

### Fixes
* fix order in Meltano Analyze


## 0.1.4 - (2018-11-27)

### Fixes
* add default values for the 'www' command - [!185](https://gitlab.com/meltano/meltano/merge_requests/185)
* add CHANGELOG.md
* fix a problem with autodiscovery on taps - [!180](https://gitlab.com/meltano/meltano/merge_requests/180)

### Changes
* move the 'api' extra package into the default package
* add 'tap-fastly' to the discovery

---

## 0.1.3

### Changes
* remove `setuptools>=40` dependency
* `meltano` CLI is now in the `meltano` package

## 0.1.2

### Fixes
* target output state is now saved asynchronously

## 0.1.1

### Changes
* initial release
