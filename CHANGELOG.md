# CHANGELOG

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/) and [Keep a Changelog](http://keepachangelog.com/).



## Unreleased
---

### New
* [#757](https://gitlab.com/meltano/meltano/issues/757) Update 'meltano permissions' to add support for GRANT ALL and FUTURE GRANTS on tables in schemas
* [#760](https://gitlab.com/meltano/meltano/issues/760) Update 'meltano permissions' to add support for granting permissions on VIEWs
* [#812](https://gitlab.com/meltano/meltano/issues/812) `meltano ui` will now stop stale Airflow workers when starting

### Changes
* [#828](https://gitlab.com/meltano/meltano/issues/828) Docker installation instructions have been dogfooded, clarified, and moved to Installation section

### Fixes
* [#807](https://gitlab.com/meltano/meltano/issues/807) Fix filter input validation when editing saved filters
* [#822](https://gitlab.com/meltano/meltano/issues/822) Fix pipeline schedule naming via slugify to align with Airflow DAG naming requirements
* [#820](https://gitlab.com/meltano/meltano/issues/820) Fix `meltano select` not properly connecting to the system database
* [#787](https://gitlab.com/meltano/meltano/issues/787) Fix results sorting to support join tables

### Breaks


## 0.33.0 - (2019-07-22)
---

### New
* [#788](https://gitlab.com/meltano/meltano/issues/788) Reydrate filters in Analyze UI after loading a saved report containing filters

### Changes
* [#804](https://gitlab.com/meltano/meltano/issues/804) Connection set in the Design view are now persistent by Design

### Fixes
* [#788](https://gitlab.com/meltano/meltano/issues/788) Properly reset the default state of the Analyze UI so stale results aren't displayed during a new analysis
* [!806](https://gitlab.com/meltano/meltano/merge_requests/806) Fix filters editing to prevent input for `is_null` and `is_not_null` while also ensuring edits to existing filter expressions types adhere to the same preventitive input.
* [#582](https://gitlab.com/meltano/meltano/issues/582) Remove the `export` statements in the default `.env` initialized by `meltano init`.
* [#816](https://gitlab.com/meltano/meltano/issues/816) Fix `meltano install` failing when connections where specified in the `meltano.yml`
* [#786](https://gitlab.com/meltano/meltano/issues/786) Fixed an issue with the SQL engine would mixup table names with join/design names
* [#808](https://gitlab.com/meltano/meltano/issues/808) Fix filter aggregate value with enforced number via `getQueryPayloadFromDesign()` as `input type="number"` only informs input keyboards on mobile, and does not enforce the Number type as expected


## 0.32.2 - (2019-07-16)
---

### New
* [#759](https://gitlab.com/meltano/meltano/issues/759) Added filtering functionality to the Analyze UI while additionally cleaning it up from a UI/UX lens

## 0.32.1 - (2019-07-15)
---

### Fixes
* [#792](https://gitlab.com/meltano/meltano/issues/792) Fix an error when trying to schedule an extractor that didn't expose a `start_date`.


## 0.32.0 - (2019-07-15)
---

### New
* [!718](https://gitlab.com/meltano/meltano/merge_requests/718) Add support for filters (WHERE and HAVING clauses) to MeltanoQuery and Meltano's SQL generation engine
* [#748](https://gitlab.com/meltano/meltano/issues/748) Added the `Connections` plugin to move the Analyze connection settings to the system database
* [#748](https://gitlab.com/meltano/meltano/issues/748) Added the `meltano config` command to manipulate a plugin's configuration


### Fixes
[!726](https://gitlab.com/meltano/meltano/merge_requests/726) Fixed InputDateIso8601's default value to align with HTML's expected empty string default


## 0.31.0 - (2019-07-08)
---

### New
* [#766](https://gitlab.com/meltano/meltano/issues/766) Add Codeowners file so that the "approvers" section on MRs is more useful for contributors
* [#750](https://gitlab.com/meltano/meltano/issues/750) Various UX updates (mostly tooltips) to make the configuration UI for scheduling orchestration easier to understand
* [#739](https://gitlab.com/meltano/meltano/issues/739) Updated `discovery.yml` for better consistency of UI order within each connector's settings (authentication -> contextual -> start/end dates). Improved various settings' `kind`, `label`, and `description`. Added a `documentation` prop to provide a documentation link for involved settings (temp until we have better first class support for more complex setting types)


### Fixes
* [#737](https://gitlab.com/meltano/meltano/issues/737) Fixed UI flash for connector settings when installation is complete but `configSettings` has yet to be set
* [#751](https://gitlab.com/meltano/meltano/issues/751) Fixed the Orchestrations view by properly checking if Airflow is installed so the correct directions display to the user


## 0.30.0 - (2019-07-01)
---

### New
* [#736](https://gitlab.com/meltano/meltano/issues/736) Add "Cancel", "Next", and a message to the entities UI when an extractor doesn't support discovery and thus entity selection
* [#730](https://gitlab.com/meltano/meltano/issues/730) Updated Analyze Models page UI with improved content organization so it is easier to use
* [#710](https://gitlab.com/meltano/meltano/issues/710) Updated connector (extractor and loader) settings with specific control type (text, password, email, boolean, and date) per setting, added form validation, and added an inference by default for password and token fields as a protective measure
* [#719](https://gitlab.com/meltano/meltano/issues/719) Added InputDateIso8601.vue component to standardize date inputs in the UI while ensuring the model data remains in Iso8601 format on the frontend.
* [#643](https://gitlab.com/meltano/meltano/issues/643) Updated `minimallyValidated` computeds so that new users are intentionally funneled through the pipelines ELT setup UI (previously they could skip past required steps)
* [#752](https://gitlab.com/meltano/meltano/issues/752) Fix the schedule having no start_date when the extractor didn't expose a `start_date` setting


### Fixes
* [!703](https://gitlab.com/meltano/meltano/merge_requests/703) Fix `ScheduleService` instantiation due to signature refactor


## 0.29.0 - (2019-06-24)
---

### New
* [#724](https://gitlab.com/meltano/meltano/issues/724) Add the `model-gitlab-ultimate` plugin to Meltano. It includes .m5o files for analyzing data available for Gitlab Ultimate or Gitlab.com Gold accounts (e.g. Epics, Epic Issues, etc) fetched using the Gitlab API. Repository used: https://gitlab.com/meltano/model-gitlab-ultimate
* [#723](https://gitlab.com/meltano/meltano/issues/723) Add proper signage and dedicated sub-navigation area in views/pages. Standardized the view -> sub-view markup relationships for consistent layout. Directory refactoring for improved organization.
* [#612](https://gitlab.com/meltano/meltano/issues/612) Move the plugins' configuration to the database, enabling configuration from the UI

### Changes
* [#636](https://gitlab.com/meltano/meltano/issues/636) Refactored connector logo related logic into a ConnectorLogo component for code cleanliness, reusability, and standardization
* [#728](https://gitlab.com/meltano/meltano/issues/728) Change error notification button link to open the bugs issue template

### Fixes
* [#718](https://gitlab.com/meltano/meltano/issues/718) Fix dynamically disabled transforms always running. Transforms can now be dynamically disabled inside a dbt package and Meltano will respect that. It will also respect you and your time.
* [#684](https://gitlab.com/meltano/meltano/issues/684) Enables WAL on SQLite to handle concurrent processes gracefully
* [#732](https://gitlab.com/meltano/meltano/issues/732) Fix plugin installation progress bar that wasn't updating upon installation completion


## 0.28.0 - (2019-06-17)
---

### New
* [!683](https://gitlab.com/meltano/meltano/issues/683) Add `--start-date` to `meltano schedule` to give the control over the catch up logic to the users
* [#651](https://gitlab.com/meltano/meltano/issues/651) Added model installation in the Analyze UI to bypass an otherwise "back to the CLI step"
* [#676](https://gitlab.com/meltano/meltano/issues/676) Add pipeline schedule UI for viewing and saving pipeline schedules for downstream use by Airflow/Orchestration

### Changes
* [#708](https://gitlab.com/meltano/meltano/issues/708) Enable `tap-gitlab` to run using Gitlab Ultimate and Gitlab.com Gold accounts and extract Epics and Epic Issues.
* [#711](https://gitlab.com/meltano/meltano/issues/711) Add new call to action for submitting an issue on docs site
* [#717](https://gitlab.com/meltano/meltano/issues/717) Enable `dbt-tap-gitlab` to run using Gitlab Ultimate and Gitlab.com Gold accounts and generate transformed tables that depend on Epics and Epic Issues.


### Fixes
* [#716](https://gitlab.com/meltano/meltano/issues/716) Fix entities UI so only installed extractors can edit selections
* [#715](https://gitlab.com/meltano/meltano/issues/715) Remove reimport of Bulma in `/orchestration` route to fix borked styling


## 0.27.0 - (2019-06-10)
---

### New
* [!640](https://gitlab.com/meltano/meltano/merge_requests/640) Google Analytics logo addition for recent tap-google-analytics Extractor addition
* [#671](https://gitlab.com/meltano/meltano/issues/671) Add the `tap-google-analytics` transform to Meltano. It is using the dbt package defined in https://gitlab.com/meltano/dbt-tap-google-analytics
* [#672](https://gitlab.com/meltano/meltano/issues/672) Add the `model-google-analytics` plugin to Meltano. It includes .m5o files for analyzing data fetched from the Google Analytics Reporting API. Repository used: https://gitlab.com/meltano/model-google-analytics
* [#687](https://gitlab.com/meltano/meltano/issues/687) Implemented a killswitch to prevent undefined behaviors when a Meltano project is not compatible with the installed `meltano` version


### Fixes
* [#661](https://gitlab.com/meltano/meltano/issues/661) Fixed empty UI for extractors that lack configuration settings by providing feedback message with actionable next steps
* [#663](https://gitlab.com/meltano/meltano/issues/663) Fixed Airflow error when advancing to Orchestration step after installing and saving a Loader configuration
* [#254](https://gitlab.com/meltano/meltano/issues/254) Fixed `meltano init` not working on terminal with cp1252 encoding
* [#254](https://gitlab.com/meltano/meltano/issues/254) Fixed `meltano add/install` crashing on Windows
* [#664](https://gitlab.com/meltano/meltano/issues/664) Minor CSS fix ensuring Airflow UI height is usable (side-effect of recent reparenting)
* [#679](https://gitlab.com/meltano/meltano/issues/679) Fix an issue with `meltano select` emitting duplicate properties when the property used the `anyOf` type
* [#650](https://gitlab.com/meltano/meltano/issues/650) Add `MELTANO_DISABLE_TRACKING` environment variable to disable all tracking
* [#670](https://gitlab.com/meltano/meltano/issues/670) Update tests to not send tracking events


## 0.26.0 - (2019-06-03)
---

### New
* [#603](https://gitlab.com/meltano/meltano/issues/603) `meltano select` now supports raw JSON Schema as a valid Catalog
* [#537](https://gitlab.com/meltano/meltano/issues/537) Add Extractor for Google Analytics (`tap-google-analytics`) to Meltano. It uses the tap defined in https://gitlab.com/meltano/tap-google-analytics/

### Changes
* [#621](https://gitlab.com/meltano/meltano/issues/621) Added new tutorial for tap-gitlab
* [#657](https://gitlab.com/meltano/meltano/issues/657) Update Analyze page to have single purpose views

### Fixes
* [#645](https://gitlab.com/meltano/meltano/issues/645) Fixed confusion around Loader Settings and Analytics DB Connector Settings
* [#580](https://gitlab.com/meltano/meltano/issues/580) Fixed `project_compiler` so the Analyze page can properly display custom topics
* [#658](https://gitlab.com/meltano/meltano/issues/658) Fixed the Analyze page when no models are present
* [#603](https://gitlab.com/meltano/meltano/issues/603) Fix an issue where `meltano select` would incorrectly report properties as excluded
* [#603](https://gitlab.com/meltano/meltano/issues/603) Fix an issue where `meltano select` incorrectly flatten nested properties
* [#553](https://gitlab.com/meltano/meltano/issues/553) Fix an issue where running `meltano select --list` for the first time would incorrectly report properties

### Break


## 0.25.0 - (2019-05-28)
---

### New
* [#586](https://gitlab.com/meltano/meltano/issues/586) `meltano ui` now automatically start Airflow if installed; Airflow UI available at `Orchestration`.
* [#592](https://gitlab.com/meltano/meltano/issues/592) Added baseline UX feedback via toast for uncaught API response errors with a link to "Submit Bug"
* [#642](https://gitlab.com/meltano/meltano/issues/642) Improved UX during extractor plugin installation so settings can be configured *during* installation as opposed to waiting for the (typically lengthy) install to complete
* [!647](https://gitlab.com/meltano/meltano/merge_requests/647) Added preloader for occasional lengthy extractor loading and added feedback for lengthy entities loading
* [#645](https://gitlab.com/meltano/meltano/issues/645) Added an Analyze landing page to facilitate future sub-UIs including the Analyze database settings; Added proper Loader Settings UI.


### Fixes
* [#645](https://gitlab.com/meltano/meltano/issues/645) Fixed confusion around Loader Settings and Analyze database settings


## 0.24.0 - (2019-05-06)
---

### New
* [#622](https://gitlab.com/meltano/meltano/issues/622) Added ELT flow UI Routes & Deep Linking to advance user through next steps after each step's save condition vs. requiring them to manually click the next step to advance
* [#598](https://gitlab.com/meltano/meltano/issues/598) Updated color and greyscale use in the context of navigation and interactive elements to better communicate UI hierarchy
* [#607](https://gitlab.com/meltano/meltano/issues/607) Add "All/Default/Custom" button bar UI for improved entities selection UX
* [#32](https://gitlab.com/meltano/meltano-marketing/issues/32) Integrate Algolia Search for docs
* [#590](https://gitlab.com/meltano/meltano/issues/590) Add documentation for deploying Meltano in ECS
* [#628](https://gitlab.com/meltano/meltano/issues/628) Add documentation for tap-mongodb
* [!605](https://gitlab.com/meltano/meltano/merge_requests/605) Added tooltips for areas of UI that are WIP for better communication of a feature's status

### Changes
* [375](https://gitlab.com/meltano/meltano/issues/375) Meltano can now run on any host/port

### Fixes
* [#595](https://gitlab.com/meltano/meltano/issues/595) Fix `meltano invoke` not working properly with `dbt`
* [#606](https://gitlab.com/meltano/meltano/issues/606) Fix `SingerRunner.bookmark_state()` to properly handle and store the state output from Targets as defined in the Singer.io Spec.


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
* [!528](https://gitlab.com/meltano/meltano/issues/528) Add documentation for RBAC alpha feature and environment variables

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
