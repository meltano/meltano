# CHANGELOG

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/) and [Keep a Changelog](http://keepachangelog.com/).



## Unreleased
---

### New
* [#32](https://gitlab.com/meltano/meltano-marketing/issues/32) Integrate Algolia Search for docs
- [#590](https://gitlab.com/meltano/meltano/issues/590) Add documentation for deploying Meltano in ECS

### Changes
* [375](https://gitlab.com/meltano/meltano/issues/375) Meltano can now run on any host/port

### Fixes
* [#595](https://gitlab.com/meltano/meltano/issues/595) Fix `meltano invoke` not working properly with `dbt`

### Breaks


## 0.23.0 - (2019-04-29)
---

### New
* [#32](https://gitlab.com/meltano/meltano-marketing/issues/32) Integrate Algolia Search for docs

### Changes
* [#522](https://gitlab.com/meltano/meltano/issues/522) Update Carbon tutorial with new instructions and screenshots


## 0.22.0 - (2019-04-24)
---

### New
* [#477](https://gitlab.com/meltano/meltano/issues/477) Add ability for users to sign up for email newsletters
* [!580](https://gitlab.com/meltano/meltano/merge_requests/580) Add sorting to plugins for improved UX, both UI via extractors/loaders/etc. and `meltano discover all` benefit from sorted results

### Changes
* [#588](https://gitlab.com/meltano/meltano/issues/588) Updated core navigation and depth hierarchy styling to facilitate main user flow and improved information architecture
* [#591](https://gitlab.com/meltano/meltano/issues/591) Revert #484: remove `meltano ui` being run outside a Meltano project.
* [#584](https://gitlab.com/meltano/meltano/issues/584) Initial v1 for enabling user to setup ELT linearly through the UI via a guided sequence of steps

### Fixes
* [#600](https://gitlab.com/meltano/meltano/issues/600) Fix a bug with meltano select when the extractor would output an invalid schema
* [#597](https://gitlab.com/meltano/meltano/issues/597) Automatically open the browser when `meltano ui` is run


## 0.21.0 - (2019-04-23)
---

### New
* [#477](https://gitlab.com/meltano/meltano/issues/477) Add ability for users to sign up for email newsletters

### Changes
* [#591](https://gitlab.com/meltano/meltano/issues/591) Revert #484: remove `meltano ui` being run outside a Meltano project.


## 0.20.0 - (2019-04-15)
---

### New
* Add documentation on custom transformations and models. Link to Tutorial: https://www.meltano.com/docs/tutorial.html#advanced-adding-custom-transformations-and-models


## 0.19.1 - (2019-04-10)
---

### New
* [#539](https://gitlab.com/meltano/meltano/issues/539) Add Tutorial for "Using Jupyter Notebooks" with Meltano
* [#534](https://gitlab.com/meltano/meltano/issues/534) Add UI entity selection for a given extractor
* [#520](https://gitlab.com/meltano/meltano/issues/520) Add v1 UI for extractor connector settings
* [#486](https://gitlab.com/meltano/meltano/issues/486) Add the `model-gitlab` plugin to Meltano. It includes .m5o files for analyzing data fetched using the Gitlab API. Repository used: https://gitlab.com/meltano/model-gitlab
* [#500](https://gitlab.com/meltano/meltano/issues/500) Add the `model-stripe` plugin to Meltano. It includes .m5o files for analyzing data fetched using the Stripe API. Repository used: https://gitlab.com/meltano/model-stripe
* [#440](https://gitlab.com/meltano/meltano/issues/440) Add the `model-zuora` plugin to Meltano. It includes .m5o files for analyzing data fetched using the Zuora API. Repository used: https://gitlab.com/meltano/model-zuora
* [#541](https://gitlab.com/meltano/meltano/issues/541) Add a 404 page for missing routes on the web app

### Fixes
* [#576](https://gitlab.com/meltano/meltano/issues/576) Fix switching between designs now works
* [#555](https://gitlab.com/meltano/meltano/issues/555) Fix `meltano discover` improperly displaying plugins
* [#530](https://gitlab.com/meltano/meltano/issues/530) Fix query generation for star schemas
* [#575](https://gitlab.com/meltano/meltano/issues/575) Move Airflow configuration to .meltano/run/airflow
* [#571](https://gitlab.com/meltano/meltano/issues/571) Fix various routing and API endpoint issues related to recent `projects` addition


## 0.19.0 - (2019-04-08)

---

### New
* [#513](https://gitlab.com/meltano/meltano/issues/513) Added initial e2e tests for the UI
* [#431](https://gitlab.com/meltano/meltano/issues/431) Add the `tap-zendesk` transform to Meltano. It is using the dbt package defined in https://gitlab.com/meltano/dbt-tap-zendesk
* [484](https://gitlab.com/meltano/meltano/issues/484) Updated `meltano ui` to automatically launch the UI, and projects from the UI (previously only an option in the CLI)
* [#327](https://gitlab.com/meltano/meltano/issues/327) Add `meltano add --custom` switch to enable integration of custom plugins
* [#540](https://gitlab.com/meltano/meltano/issues/540) Add CHANGELOG link in intro section of the docs
* [#431](https://gitlab.com/meltano/meltano/issues/431) Add the `model-zendesk` plugin to Meltano. It includes .m5o files for analyzing data fetched using the Zendesk API. Repository used: https://gitlab.com/meltano/model-zendesk
* [!544](https://gitlab.com/meltano/meltano/merge_requests/544) Add support for extracting data from CSV files by adding [tap-csv](https://gitlab.com/meltano/tap-csv) to Meltano
* [#514](https://gitlab.com/meltano/meltano/issues/514) Add 'airflow' orchestrators plugin to enable scheduling
* Add the `tap-zuora` transform to Meltano. It is using the dbt package defined in https://gitlab.com/meltano/dbt-tap-zuora

### Changes
* [#455](https://gitlab.com/meltano/meltano/issues/455) Add documentation about `target-snowflake`

### Fixes
* [#507](https://gitlab.com/meltano/meltano/issues/507) Ensure design name and table name don't need to match so multiple designs can leverage a single base table
* [#551](https://gitlab.com/meltano/meltano/issues/551) Fix HDA queries generated when an attribute is used both as a column and as an aggregate.
* [#559](https://gitlab.com/meltano/meltano/issues/559) Add support for running custom transforms for taps without default dbt transforms.


## 0.18.0 - (2019-04-02)
---

### New
* [#432](https://gitlab.com/meltano/meltano/issues/432) Add the `tap-zuora` transform to Meltano. It is using the dbt package defined in https://gitlab.com/meltano/dbt-tap-zuora

### Changes
* Remove Snowflake references from advanced tutorial.
* [#2 dbt-tap-zuora](https://gitlab.com/meltano/dbt-tap-zuora/issues/2) Remove custom SFDC related attributes from Zuora Account and Subscription Models
* Update [Contributing - Code Style](https://meltano.com/docs/contributing.html#code-style) documentation to including __pycache__ troubleshooting

### Fixes
* [#529](https://gitlab.com/meltano/meltano/issues/529) Resolve "SFDC Tutorial - ELT Fails due to invalid schema.yml" by [#4 dbt-tap-salesforce](https://gitlab.com/meltano/dbt-tap-salesforce/issues/4) removing the schema.yml files from the dbt models for tap-salesforce.
* [#502](https://gitlab.com/meltano/meltano/issues/502) Fix the situation where an m5o has no joins, the design still will work.


## 0.17.0 - (2019-03-25)
---

### New
- [#485](https://gitlab.com/meltano/meltano/issues/485) Added various UI unit tests to the Analyze page
- [#370](https://gitlab.com/meltano/meltano/issues/370) Enabled authorization using role-based access control for Designs and Reports

### Changes
* [#283](https://gitlab.com/meltano/meltano/issues/283) Silence pip's output when there is not error
* [#468](https://gitlab.com/meltano/meltano/issues/468) Added reminder in docs regarding the need for `source venv/bin/activate` in various situations and added minor copy updates

### Fixes
* [#433](https://gitlab.com/meltano/meltano/issues/433) Add the `sandbox` configuration to `tap-zuora`.
* [#501](https://gitlab.com/meltano/meltano/issues/501) Fix `meltano ui` crashing when the OS ran out of file watcher.
* [#510](https://gitlab.com/meltano/meltano/issues/510) Fix an issue when finding the current Meltano project in a multi-threaded environment.
* [#494](https://gitlab.com/meltano/meltano/issues/494) Improved documentation around tutorials and Meltano requirements
* [#492](https://gitlab.com/meltano/meltano/issues/492) A few small contextual additions to help streamline the release process
* [#503](https://gitlab.com/meltano/meltano/issues/503) Fix a frontend sorting issue so the backend can properly generate an up-to-date query


## 0.16.0 - (2019-03-18)
---

### New
* Add support for extracting data from Gitlab through the updated tap-gitlab (https://gitlab.com/meltano/tap-gitlab)
* Add the `tap-gitlab` transform to Meltano. It is using the dbt package defined in https://gitlab.com/meltano/dbt-tap-gitlab
* Add "Copy to Clipboard" functionality to code block snippets in the documentation
* Add the `tap-stripe` transform to Meltano. It is using the dbt package defined in https://gitlab.com/meltano/dbt-tap-stripe
* Add new command `meltano add model [name_of_model]`
* Add models to the available plugins

### Changes
* Various documentation [installation and tutorial improvements](https://gitlab.com/meltano/meltano/issues/467#note_149858308)
* Added troubleshooting button to help users add context to a pre-filled bug issue

### Fixes
* Fix the API database being mislocated
* Replaced the stale Meltano UI example image in the Carbon Emissions tutorial
* 473: Fix the docker image (meltano/meltano) from failing to expose the API


## 0.15.1 - (2019-03-12)
---

### Fixes
* locks down dependencies for issues with sqlalchemy snowflake connector


## 0.15.0 - (2019-03-11)
---

### New
* Add Salesforce Tutorial to the docs
* Add documentation for the permissions command
* Add tracking for the `meltano ui` command


### Fixes
* Updated analytics to properly recognize SPA route changes as pageview changes


## 0.14.0 - (2019-03-04)
---

### New
* Update stages table style in docs
* Add custom transforms and models tutorial to the docs

### Changes
* Add api/v1 to every route
* Update DbtService to always include the my_meltano_project model when transform runs

### Fixes
* Resolved duplicate display issue of Dashboards and Reports on the Files page
* Removed legacy `carbon.dashboard.m5o` (regression from merge)
* Updated dashboards and reports to use UI-friendly name vs slugified name
* Fix minor clipped display issue of right panel on `/settings/database`
* Fix minor display spacing in left panel of Settings
* Fix dashboard page to properly display a previously active dashboard's updated reports
* Fix pre-selected selections for join aggregates when loading a report
* Fix charts to display multiple aggregates (v1)
* Fix 404 errors when refreshing the frontend
* Fix a regression where the Topics would not be shown in the Files page


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
