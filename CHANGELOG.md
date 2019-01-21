# CHANGELOG

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/) and [Keep a Changelog](http://keepachangelog.com/).



## Unreleased
---

### New
* Meltano will now automatically source the .env
* Updated docs with `.m5o` authoring requirements and examples
* add support for timeframes in tables
* add disabled UI for the lack of timeframes support in sqlite

### Changes
* sample designs are now packaged with meltano

### Fixes
* Updated mobile menu to work as expected
* Updated tutorial docs with improved CLI commands and fixed the host setting to `localhost`

### Breaks


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
* update the error message when using Meltano from outside a project - [238](https://gitlab.com/meltano/meltano/merge_requests/238)


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
