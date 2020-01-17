# CHANGELOG

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/) and [Keep a Changelog](http://keepachangelog.com/).

## Unreleased

---

### New

- [#1556](https://gitlab.com/meltano/meltano/issues/1556) Add default transformations for the Facebook Ads Extractor. They are using the dbt package defined in https://gitlab.com/meltano/dbt-tap-facebook
- [#1557](https://gitlab.com/meltano/meltano/issues/1557) Add default Meltano Models for the Facebook Ads Extractor. They are defined in https://gitlab.com/meltano/model-facebook
- [#1560](https://gitlab.com/meltano/meltano/issues/1560) Make the Facebook Ads Extractor available by default on Meltano UI

### Changes

- [#1541](https://gitlab.com/meltano/meltano/issues/1541) Revert `tap-csv`'s `kind: file` to text input for `csv_files_definition` as we don't fully support `tap-csv` via the UI with single (definition json) and multiple (csv files) file uploading
- [#608](https://gitlab.com/meltano/meltano/issues/608) Add the Facebook Ads Extractor to Meltano as a hidden plugin. It will be fully enabled on Meltano UI once bundled Transformations and Models are added. It uses the tap defined in https://gitlab.com/meltano/tap-facebook/
- [#1477](https://gitlab.com/meltano/meltano/issues/1477) Add a `read-only` mode to Meltano to disable all modifications from the UI

### Changes


### Fixes

### Breaks

## 1.15.1 - (2020-01-16)

---

### New

- [#608](https://gitlab.com/meltano/meltano/issues/608) Add the Facebook Ads Extractor to Meltano as a hidden plugin. It will be fully enabled on Meltano UI once bundled Transformations and Models are added. It uses the tap defined in https://gitlab.com/meltano/tap-facebook/
- [meltano/model-stripe#2](https://gitlab.com/meltano/model-stripe/issues/2) Add timeframes to the Stripe models
- [#1533](https://gitlab.com/meltano/meltano/issues/1533) Add documentation for the Facebook Ads Extractor

### Changes

- [#1527](https://gitlab.com/meltano/meltano/issues/1527) Update the dashboard modal header to properly differentiate between "Create" and "Edit"
- [#1456](https://gitlab.com/meltano/meltano/issues/1456) 404 Error page now has better back functionality and ability to file new issues directly from the page

### Fixes

- [#1538](https://gitlab.com/meltano/meltano/issues/1538) Fix timeframes not properly displaying on the base table
- [#1574](https://gitlab.com/meltano/meltano/issues/1574) Fix an issue with Meltano crashing after a succesful login
- [#1568](https://gitlab.com/meltano/meltano/issues/1568) Restore support for custom plugins that don't have their available settings defined in discovery.yml

## 1.15.0 - (2020-01-13)

---

### New

- [#1483](https://gitlab.com/meltano/meltano/issues/1483) Add login audit columns to track last login time
- [#1480](https://gitlab.com/meltano/meltano/issues/1480) Add tests to `meltano permissions` command for Snowflake
- [#1392](https://gitlab.com/meltano/meltano/issues/1392) Add inline docs to Extractor configurations in iteration toward improving data setup onboarding

### Changes

- [#1480](https://gitlab.com/meltano/meltano/issues/1480) Add schema revocations for roles in the `meltano permissions` command
- [#1458](https://gitlab.com/meltano/meltano/issues/1458) Remove tap-carbon-intensity-sqlite model from default installation
- [#1458](https://gitlab.com/meltano/meltano/issues/1458) Update docs to reflect new getting started path and updated screenshots
- [#1513](https://gitlab.com/meltano/meltano/issues/1513) Remove dead code related to `/model` route that we no longer link to in favor of the contextual Analyze CTAs and the `MainNav.vue`'s Analyze dropdown
- [#1542](https://gitlab.com/meltano/meltano/issues/1542) Update version, logout, and help UI partial (upper right) to have less prominence and more clearly communicate the "Sign Out" action

### Fixes

- [#1480](https://gitlab.com/meltano/meltano/issues/1480) Fix database revocations corner case for roles in the `meltano permissions` command
- [#1553](https://gitlab.com/meltano/meltano/issues/1553) Fix bug occurring when loading a report that lacks join tables
- [#1540](https://gitlab.com/meltano/meltano/issues/1540) Meltano Analyze will now leverage Pipelines instead of Loaders in the connection dropdown
- [#1540](https://gitlab.com/meltano/meltano/issues/1540) Meltano Analyze will now infer the connection to use instead of it being provided by the user

### Breaks

## 1.14.3 - (2020-01-09)

---

### Fixes

- [#1521](https://gitlab.com/meltano/meltano/issues/1521) Sanitize user-submitted string before using it in file path

## 1.14.2 - (2020-01-09)

---

### New

- [#1391](https://gitlab.com/meltano/meltano/issues/1391) Lock all settings that are controlled through environment variables
- [#1393](https://gitlab.com/meltano/meltano/issues/1393) Add contextual Analyze CTAs for each Pipeline in the Pipelines list
- [#1551](https://gitlab.com/meltano/meltano/issues/1551) Add dbt clean before compile and runs

### Changes

- [#1424](https://gitlab.com/meltano/meltano/issues/1424) Update pipeline elapsed time display to be more human friendly

### Fixes

- [#1430](https://gitlab.com/meltano/meltano/issues/1430) Fix the state not stored for pipelines when Transforms run
- [#1448](https://gitlab.com/meltano/meltano/issues/1448) Fix `AnalyzeList.vue` to display message and link when lacking contextual models

### Breaks

## 1.14.1 - (2020-01-06)

---

### Fixes

- [#1520](https://gitlab.com/meltano/meltano/issues/1520) Fix bug when updating a dashboard that could undesirably overwrite another existing dashboard

### Breaks

## 1.14.0 - (2019-12-30)

---

### New

- [#1461](https://gitlab.com/meltano/meltano/issues/1461) Display toasted notification for report adding to dashboard
- [#1419](https://gitlab.com/meltano/meltano/issues/1419) Add ability to edit and delete dashboards
- [#1411](https://gitlab.com/meltano/meltano/issues/1411) Add download log button to Job Log Modal

### Changes

- [#1311](https://gitlab.com/meltano/meltano/issues/1311) Remove unused meltano/meltano/runner docker image
- [#1502](https://gitlab.com/meltano/meltano/issues/1502) Update configuration file uploads to occur on save vs. file picker completion

### Fixes

- [#1518](https://gitlab.com/meltano/meltano/issues/1518) Fix bug that caused all text fields to show up as required in configuration modals
- [#1446](https://gitlab.com/meltano/meltano/issues/1446) Fix bug that could result in a broken report when the report URL was manually modified
- [#1411](https://gitlab.com/meltano/meltano/issues/1411) Fix bug when reading too large a job log file

## 1.13.0 - (2019-12-23)

---

### New

- [#1269](https://gitlab.com/meltano/meltano/issues/1269) Add `kind: file` so single file uploads can be used with extractors (`tap-google-analytics`'s `key_file_location` is the first user)
- [#1494](https://gitlab.com/meltano/meltano/issues/1494) Add `LIKE` options to Analyze Filter UI so users better understand what filtering patterns are available

### Changes

- [#1399](https://gitlab.com/meltano/meltano/issues/1399) Log Modal now has a prompt to explain potential factors in required time for pipelines to complete
- [#1433](https://gitlab.com/meltano/meltano/issues/1433) Remove `/orchestrate` route and thus the Airflow iframe as this is overkill for our current target users

### Fixes

- [#1434](https://gitlab.com/meltano/meltano/issues/1434) Fix Analyze CTAs to only enable if at least one related pipeline has succeeded
- [#1447](https://gitlab.com/meltano/meltano/issues/1447) Various fixes around loading and reloading reports to mitigate false positive `sqlErrorMessage` conditions
- [#1509](https://gitlab.com/meltano/meltano/issues/1509) Allow plugin profile config to be set through meltano.yml

## 1.12.2 - (2019-12-20)

---

### New

- [#1437](https://gitlab.com/meltano/meltano/issues/1437) Users can now share their dashboards with an automatically generated email

### Changes

- [#1466](https://gitlab.com/meltano/meltano/issues/1466) Filters now have clear language and indiciation that they use AND for chaining
- [#1464](https://gitlab.com/meltano/meltano/issues/1464) Remove the "only" option for transforms in Create Pipeline form

- [#1399](https://gitlab.com/meltano/meltano/issues/1399) Log Modal now has a prompt to explain potential factors in required time for pipelines to complete
- [#1431](https://gitlab.com/meltano/meltano/issues/1431) Add "pipeline will still run if modal is closed" message in the Job Log Modal

### Changes

- [#1422](https://gitlab.com/meltano/meltano/issues/1422) Update start date field to have a recommendation

### Fixes

- [#1447](https://gitlab.com/meltano/meltano/issues/1447) Various fixes around loading and reloading reports to mitigate false positive `sqlErrorMessage` conditions
- [#1443](https://gitlab.com/meltano/meltano/issues/1443) Fix tooltip clipping in modals
- [#1500](https://gitlab.com/meltano/meltano/issues/1500) Fix `meltano install` not running the migrations.

## 1.12.1 - (2019-12-18)

---

### Changes

- [#1403](https://gitlab.com/meltano/meltano/issues/1403) Remove "Orchestrate", "Model", and "Notebook" from the main navigation until each respective UI is more useful (the `/orchestrate` and `/model` routes still exist)
- [#1476](https://gitlab.com/meltano/meltano/issues/1476) Add database and warehouse revocations for roles in the `meltano permissions` command
- [#1473](https://gitlab.com/meltano/meltano/issues/1473) Update Release issue template to recent guidelines

## 1.12.0 - (2019-12-16)

---

### New

- [#1374](https://gitlab.com/meltano/meltano/issues/1374) Add role revocation for users and roles in the `meltano permissions` command
- [#1377](https://gitlab.com/meltano/meltano/issues/1377) Document cleanup steps after MeltanoData testing
- [#1438](https://gitlab.com/meltano/meltano/issues/1438) Add documentation for DNS spoofing error
- [#1436](https://gitlab.com/meltano/meltano/issues/1436) Add video walkthrough on how to setup Google Analytics so that the Meltano Extractor can be able to access the Google APIs and the Google Analytics data.

### Changes

- [#1350](https://gitlab.com/meltano/meltano/issues/1350) Switch to all lower case for Snowflake permission comparisons in the `meltano permissions` command
- [#1449](https://gitlab.com/meltano/meltano/issues/1449) Hide the Marketo Extractor form Meltano UI
- [#1397](https://gitlab.com/meltano/meltano/issues/1397) Optimize workflow for MeltanoData setup
- [#1423](https://gitlab.com/meltano/meltano/issues/1423) Update sidebar and docs to include Ansible

## 1.11.2 - (2019-12-13)

---

### Changes

- [#1435](https://gitlab.com/meltano/meltano/issues/1435) Change "Model" to "Analyze" so the Pipeline CTA is actionable and less abstract
- [#1432](https://gitlab.com/meltano/meltano/issues/1432) Changed "Close" to "Back" in Log Modal to help mitigate "Am I ending the pipeline?" concerns

### Fixes

- [#1439](https://gitlab.com/meltano/meltano/issues/1439) Fix relative elapsed time since last run time display in the Pipelines UI
- [#1441](https://gitlab.com/meltano/meltano/issues/1441) Fix auto advance to "Create Pipeline" when coming from "Load" step (previously "Transform" step, but this has been removed from the UI)
- [#1440](https://gitlab.com/meltano/meltano/issues/1440) Allow installed plugins to appear in UI even if hidden in configuration

## 1.11.1 - (2019-12-12)

---

### New

- [#1351](https://gitlab.com/meltano/meltano/issues/1351) Add "Create Meltano Account" promo for `meltano.meltanodata.com`
- [#1055](https://gitlab.com/meltano/meltano/issues/1055) Add "Disable" button to Tracking Acknowledgment toast so user's can opt-out from the UI
- [#1408](https://gitlab.com/meltano/meltano/issues/1408) Add "Last Run" context to each pipeline
- [#1408](https://gitlab.com/meltano/meltano/issues/1408) Add "Started At", "Ended At", and "Elapsed" to Job Log modal
- [#1390](https://gitlab.com/meltano/meltano/issues/1390) Display of extractors and loaders can now be configured through the `hidden` property in `discovery.yml`

### Changes

- [#1398](https://gitlab.com/meltano/meltano/issues/1398) Update default Transform from "Skip" to "Run"
- [#1406](https://gitlab.com/meltano/meltano/issues/1406) Update Analyze Query section CSS for improved UX (visually improved organization and scanability)
- [#1417](https://gitlab.com/meltano/meltano/issues/1417) Update SCSS variable usage in components for SSOT styling
- [#1408](https://gitlab.com/meltano/meltano/issues/1408) Updated date and time displays to be human-friendly (`moment.js`)
- [#1268](https://gitlab.com/meltano/meltano/issues/1268) Remove Transform step from UI (Create Schedule still allows choosing "Skip" or "Only" but will intelligently default to "Skip" or "Run")

## 1.11.0 - (2019-12-09)

---

### New

- [#1361](https://gitlab.com/meltano/meltano/issues/1361) Add `kind: hidden` to `discovery.yml` so certain connector settings can validate with a default `value` but remain hidden from the user for improved UX

### Changes

- [#1389](https://gitlab.com/meltano/meltano/issues/1389) Temporary Profiles feature removal (conditionally removed if 2+ profiles not already created so existing users can continue using multiple profiles if created)
- [#1373](https://gitlab.com/meltano/meltano/issues/1373) Update MeltanoData deletion process with 1Password

### Fixes

- [#1401](https://gitlab.com/meltano/meltano/issues/1401) Fix double instance of self hosted CTA on desktop sites

## 1.10.2 - (2019-12-06)

---

### Changes

- [#1371](https://gitlab.com/meltano/meltano/issues/1371) Provide more specific instructions for Google Analytics configuration
- [#1381](https://gitlab.com/meltano/meltano/issues/1381) Update the default directory for client_secrets.json for the Google Analytics Extractor to be located under the extract/ directory and not the project's root.
- [#1345](https://gitlab.com/meltano/meltano/issues/1345) Update the documentation for the [Salesforce Extractor](https://www.meltano.com/plugins/extractors/salesforce.html) to contain additional information on Security Tokens
- [#1383](https://gitlab.com/meltano/meltano/issues/1383) Add CTA for hosted solution signup to navigation

### Fixes

- [#1379](https://gitlab.com/meltano/meltano/issues/1379) Fix an issue with Airflow scheduling too many jobs.
- [#1386](https://gitlab.com/meltano/meltano/issues/1386) Fix connector modal clipping issue where small browser heights prevented accessing the "Save" area

### Breaks

## 1.10.1 - (2019-12-05)

---

### Changes

- [#1373](https://gitlab.com/meltano/meltano/issues/1373) Update MeltanoData deletion process with 1Password
- [#1373](https://gitlab.com/meltano/meltano/issues/1373) Update Analyze dropdown as scrollable to better display model CTAs (scrollable dropdown vs. scrolling entire page)

### Fixes

- [#1373](https://gitlab.com/meltano/meltano/issues/1373) Fix formatting on custom containers in MeltanoData guide

## 1.10.0 - (2019-12-04)

---

### New

- [#1343](https://gitlab.com/meltano/meltano/issues/1343) Add current Meltano version to main navigation

### Changes

- [#1358](https://gitlab.com/meltano/meltano/issues/1358) Update MeltanoData guide with maintenance and debugging instructions
- [#1337](https://gitlab.com/meltano/meltano/issues/1337) Add CTA to installations for free hosted dashboards
- [#1365](https://gitlab.com/meltano/meltano/issues/1365) Add process for deleting meltanodata instances
- [#1340](https://gitlab.com/meltano/meltano/issues/1340) Update connector settings UI to communicate the required status of each setting
- [#1357](https://gitlab.com/meltano/meltano/issues/1357) Update LogModal Analyze CTAs so Analyze can preselect the correct loader for a given analysis

### Fixes

- [#1364](https://gitlab.com/meltano/meltano/issues/1364) Fix instructions to SSH into MeltanoData.com instance

## 1.9.1 - (2019-12-04)

---

### Fixes

- [#1355](https://gitlab.com/meltano/meltano/issues/1355) Upgrade version of `discovery.yml` so that not upgraded Meltano instances with a pre v1.9.0 Meltano version do not break.

## 1.9.0 - (2019-12-03)

---

### New

- [marketing#103](https://gitlab.com/meltano/meltano-marketing/issues/103) Add Google Site Verification token to site
- [#1346](https://gitlab.com/meltano/meltano/issues/1346) Add new tutorial for using FileZilla with a Meltano project
- [#1292](https://gitlab.com/meltano/meltano/issues/1292) Add guide for setting up Meltano projects on meltanodata.com

### Changes

- [#1341](https://gitlab.com/meltano/meltano/issues/1341) Various `discovery.yml` and connector configuration UI updates to improve UX.
- [#1341](https://gitlab.com/meltano/meltano/issues/1341) Updated documentation to communicate the various optional settings of a connector

### Fixes

- [#1334](https://gitlab.com/meltano/meltano/issues/1334) Fix automatic population of airflow.cfg after installation
- [#1344](https://gitlab.com/meltano/meltano/issues/1344) Fix an ELT automatic discovery error when running Meltano on Python3.6

## 1.8.0 - (2019-12-02)

---

### New

- [#764](https://gitlab.com/meltano/meltano/issues/764) Add plugin profiles to enable multiple configurations for extractors
- [#1081](https://gitlab.com/meltano/meltano/issues/1081) Add ability to delete data pipelines
- [#1217](https://gitlab.com/meltano/meltano/issues/1217) Add "Test Connection" button to validate connection settings prior to ELT runs
- [#1236](https://gitlab.com/meltano/meltano/issues/1236) Add contextual Analyze CTAs in the Job Log UI
- [#1271](https://gitlab.com/meltano/meltano/issues/1271) Add labels in discovery.yml for easy brand definition

### Changes

- [#1323](https://gitlab.com/meltano/meltano/issues/1323) Add CTA to send users to Typeform to provide info for setting up a hosted dashboard

- [#1323](https://gitlab.com/meltano/meltano/issues/1323) Add CTA to send users to Typeform to provide info for setting up a hosted dashboard
- [#1271](https://gitlab.com/meltano/meltano/issues/1271) Improve messaging on tap and target settings modals
- [#1226](https://gitlab.com/meltano/meltano/issues/1226) Update Pipelines main navigation link to show all data pipeline schedules if that step has been reached
- [#1323](https://gitlab.com/meltano/meltano/issues/1323) Add CTA to send users to Typeform to provide info for setting up a hosted dashboard
- [#1271](https://gitlab.com/meltano/meltano/issues/1271) Improve messaging on tap and target settings modals
- [#1246](https://gitlab.com/meltano/meltano/issues/1246) Update the [Salesforce API + Postgres](https://www.meltano.com/tutorials/salesforce-and-postgres.html) Tutorial to use Meltano UI for setting up the Extractor and Loader, running the ELT pipeline and analyzing the results.

- [#1225](https://gitlab.com/meltano/meltano/issues/1225) Update dbt docs link to be conditional so the user doesn't experience 404s

## 1.7.2 - (2019-11-26)

---

### Fixes

- [#1318](https://gitlab.com/meltano/meltano/merge_requests/1318/) Pin dbt version to `v0.14.4` to address Meltano Transformation failing when using dbt `v0.15.0`

## 1.7.1 - (2019-11-25)

---

### Fixes

- [#1184](https://gitlab.com/meltano/meltano/merge_requests/1184/) Fix `contextualModels` implementation for contextual CTAs in Job Log modal

## 1.7.0 - (2019-11-25)

---

### New

- [#1236](https://gitlab.com/meltano/meltano/issues/1236) Add contextual Analyze CTAs in the Job Log UI

### Fixes

- [#1298](https://gitlab.com/meltano/meltano/issues/1298) Let default entity selection be configured in discovery.yml under `select`
- [#1298](https://gitlab.com/meltano/meltano/issues/1298) Define default entity selection for tap-salesforce
- [#1304](https://gitlab.com/meltano/meltano/issues/1304) Fix Meltano subprocess fetching large catalogs (e.g. for Salesforce) getting stuck do to the subprocess' stderr buffer filling and the process getting deadlocked.

## 1.6.0 - (2019-11-18)

---

### New

- [#1235](https://gitlab.com/meltano/meltano/issues/1235) Add help link button in the app
- [#1285](https://gitlab.com/meltano/meltano/issues/1285) Add link to YouTube guidelines for release instructions
- [#1277](https://gitlab.com/meltano/meltano/issues/1277) Move sections that don't apply to outside contributors from Contributing and Roadmap docs to Handbook: Release Process, Release Schedule, Demo Day, Speedruns, DigitalOcean Marketplace

### Changes

- [#1257](https://gitlab.com/meltano/meltano/issues/1257) Prevent modified logo file upon each build
- [#1289](https://gitlab.com/meltano/meltano/issues/1289) Dismiss all modals when using the escape key
- [#1282](https://gitlab.com/meltano/meltano/issues/1282) Remove Entity Selection from the UI (still available in CLI) and default to "All" entities for a given data source
- [#1303](https://gitlab.com/meltano/meltano/issues/1303) Update the configuration options for the Salesforce Extractor to only include relevant properties. Remove properties like the client_id that were not used for username/password authentication.
- [#1308](https://gitlab.com/meltano/meltano/issues/1308) Update the configuration options for the Marketo Extractor to use a Start Date instead of a Start Time.

### Fixes

- [#1297](https://gitlab.com/meltano/meltano/issues/1297) Get actual latest ELT job log by sorting matches by creation time with nanosecond resolution
- [#1297](https://gitlab.com/meltano/meltano/issues/1297) Fix pipeline failure caused by jobs that require true concurrency being executed on CI runners that don't

## 1.5.0 - (2019-11-11)

---

### New

- [#1222](https://gitlab.com/meltano/meltano/issues/1222) Include static application security testing (SAST) in the pipeline
- [#1164](https://gitlab.com/meltano/meltano/issues/1164) Add "transform limitations" message to Transform UI
- [#1272](https://gitlab.com/meltano/meltano/issues/1272) Add Vuepress plugin to generate a sitemap on website build
- [meltano-marketing#89](https://gitlab.com/meltano/meltano-marketing/issues/89) Adds basic title and meta descriptions to all public-facing website & documentation pages.

### Changes

- [#1239](https://gitlab.com/meltano/meltano/issues/1239) Update header buttons layout on small viewports
- [#1019](https://gitlab.com/meltano/meltano/issues/1019) Automatically update package.json file versions
- [#1253](https://gitlab.com/meltano/meltano/issues/1253) Do not allow `meltano` command invocation without any argument
- [#1192](https://gitlab.com/meltano/meltano/issues/1192) Improve helper notes associated with each Extract, Load, and Transform step to better communicate the purpose of each
- [#1201](https://gitlab.com/meltano/meltano/issues/1201) Improved "Auto Advance" messaging regarding Entity Selection. We also doubled the default toast time to improve likelihood of reading feedback.
- [#1191](https://gitlab.com/meltano/meltano/issues/1191) update Google Analytics extractor documentation to explain how to set up the Google Analytics API, and remove duplicate instructions from the [Google Analytics API + Postgres tutorial](http://meltano.com/tutorials/google-analytics-with-postgres.html#prerequisites)
- [#1199](https://gitlab.com/meltano/meltano/issues/1199) Add example and sample CSV files to the CSV extractor documentation
- [#1247](https://gitlab.com/meltano/meltano/issues/1247) Update the [Loading CSV Files to a Postgres Database](https://www.meltano.com/tutorials/csv-with-postgres.html) Tutorial to use Meltano UI for setting up the Extractor and Loader, running the ELT pipeline and analyzing the results. Also provide all the files used in the tutorial (transformations, models, etc) as downloadable files.
- [#1279] Revise ["Roadmap" section](https://meltano.com/docs/roadmap.html) of the docs with clarified persona, mission, vision, and re-order content
- [#1134](https://gitlab.com/meltano/meltano/issues/1134) Update the [GitLab API + Postgres](https://www.meltano.com/tutorials/gitlab-and-postgres.html). Include video walk-through and update the end to end flow to only use Meltano UI.
- [#95](https://gitlab.com/meltano/meltano-marketing/issues/95) Update the DigitalOcean CTA to go to the public directory page for the Meltano droplet
- [#1270](https://gitlab.com/meltano/meltano/issues/1270) Main navigation "Pipeline" to "Pipelines" to reinforce multiple vs. singular (conflicts a bit with the verb approach of the other navigation items but we think it's worth it for now)
- [#1240](https://gitlab.com/meltano/meltano/issues/1240) Provide clarity around how Airflow can be used directly in documentation and UI
- [#1263](https://gitlab.com/meltano/meltano/issues/1263) Document lack of Windows support and suggest WSL, Docker

### Fixes

- [#1259](https://gitlab.com/meltano/meltano/issues/1259) Fix `meltano elt` not properly logging errors happening in the ELT process
- [#1183](https://gitlab.com/meltano/meltano/issues/1183) Fix a race condition causing the `meltano.yml` to be empty in some occurence
- [#1258](https://gitlab.com/meltano/meltano/issues/1258) Fix format of custom extractor's capabilities in meltano.yml
- [#1215](https://gitlab.com/meltano/meltano/issues/1215) Fix intercom documentation footer overlap issue.
- [#1215](https://gitlab.com/meltano/meltano/issues/1215) Fix YouTube iframes to be responsive (resolves unwanted side-effect of horizontal scrollbar at mobile/tablet media queries)

## 1.4.0 - (2019-11-04)

---

### New

- [#1208](https://gitlab.com/meltano/meltano/issues/1208) Add description to `Plugin` definition and updated `discovery.yml` and UI to consume it
- [#1195](https://gitlab.com/meltano/meltano/issues/1195) Add temporary message in configuration communicating their global nature until "Profiles" are implemented
- [#1245](https://gitlab.com/meltano/meltano/issues/1245) Add detailed information on the documentation about events tracked by Meltano when Anonymous Usage Data tracking is enabled.
- [#1228](https://gitlab.com/meltano/meltano/issues/1228) Add preselections of the first column and aggregate of base table to initialize Analyze with data by default.

### Changes

- [#1244](https://gitlab.com/meltano/meltano/issues/1244) Add instructions on how to deactivate a virtual environment
- [#1082](https://gitlab.com/meltano/meltano/issues/1082) Meltano will now enable automatically DAGs created in Airflow
- [#1231](https://gitlab.com/meltano/meltano/issues/1231) Update CLI output during project initialization
- [#1126](https://gitlab.com/meltano/meltano/issues/1126) Minor UI updates to improve clarity around Schedule step and Manual vs Orchestrated runs
- [#1210](https://gitlab.com/meltano/meltano/issues/1210) Improved SQLite loader configuration context (name and description)
- [#1185](https://gitlab.com/meltano/meltano/issues/1185) Remove majority of unimplemented placeholder UI buttons
- [#1166](https://gitlab.com/meltano/meltano/issues/1166) Clarify in documentation that plugin configuration is stored in the `.meltano` directory, which is in `.gitignore`.
- [#1200](https://gitlab.com/meltano/meltano/issues/1200) Link to new Getting Help documentation section instead of issue tracker where appropriate

- [#1227](https://gitlab.com/meltano/meltano/issues/1227) Update Notebook `MainNav` link to jump to our Jupyter Notebook docs

### Fixes

- [#1075](https://gitlab.com/meltano/meltano/issues/1075) Fix a bug that caused `target-csv` to fail.
- [#1233](https://gitlab.com/meltano/meltano/issues/1233) Fix the Design page failing to load a Design that has timeframes on the base table
- [#1187](https://gitlab.com/meltano/meltano/issues/1187) Updated configuration to support `readonly` kind to prevent unwanted editing
- [#1187](https://gitlab.com/meltano/meltano/issues/1187) Updated configuration to setting resets to prevent unwanted editing
- [#1187](https://gitlab.com/meltano/meltano/issues/1187) Updated configuration to conditionally reset certain settings to prevent unwanted editing
- [#1187](https://gitlab.com/meltano/meltano/issues/1187) Updated configuration to prevent unwanted editing until we handle this properly with role-based access control
- [#1187](https://gitlab.com/meltano/meltano/issues/1187) Updated certain connector configuration settings with a `readonly` flag to prevent unwanted editing in the UI. This is temporary and will be removed when we handle this properly with role-based access control.
- [#1198](https://gitlab.com/meltano/meltano/issues/1198) Fix "More Info." link in configuration to properly open a new tab via `target="_blank"`

- [#1229](https://gitlab.com/meltano/meltano/issues/1229) Improve extractor schema autodiscovery error messages and don't attempt autodiscovery when it is known to not be supported, like in the case of tap-gitlab
- [#1207](https://gitlab.com/meltano/meltano/issues/1207) Updated all screenshots in Getting Started Guide to reflect the most current UI

## 1.3.0 - (2019-10-28)

---

### New

- [#991](https://gitlab.com/meltano/meltano/issues/991) Add e2e tests for simple sqlite-carbon workflow
- [#1103](https://gitlab.com/meltano/meltano/issues/1103) Add Intercom to Meltano.com to interact with our users in real-time
- [#1130](https://gitlab.com/meltano/meltano/issues/1130) Add Tutorial for extracting data from Google Analytics and loading the extracted data to Postgres
- [#1168](https://gitlab.com/meltano/meltano/issues/1168) Speedrun video added to home page and new release issue template
- [#1182](https://gitlab.com/meltano/meltano/issues/1182) Add `null`able date inputs so optional dates aren't incorrectly required in validation
- [#1169](https://gitlab.com/meltano/meltano/issues/1169) Meltano now generates the dbt documentation automatically

### Changes

- [!1061](https://gitlab.com/meltano/meltano/merge_requests/1061) Update the Getting Started Guide and the Meltano.com documentation with the new UI and information about job logging and how to find the most recent run log of a pipeline.
- [#1213](https://gitlab.com/meltano/meltano/issues/1213) Add VuePress use and benefits to documentation
- [#922](https://gitlab.com/meltano/meltano/issues/922) Document the importance of transformations and how to get started
- [#1167](https://gitlab.com/meltano/meltano/issues/1167) Iterate on docs to improve readability and content updates

### Fixes

- [#1173](https://gitlab.com/meltano/meltano/issues/1173) Fix `sortBy` drag-and-drop bug in Analyze by properly using `tryAutoRun` vs. `runQuery`
- [#1079](https://gitlab.com/meltano/meltano/issues/1079) `meltano elt` will now run in isolation under `.meltano/run/elt`
- [#1204](https://gitlab.com/meltano/meltano/issues/1204) move project creation steps out of the local installation section of the docs and into the Getting Started Guide
- [#782](https://gitlab.com/meltano/meltano/issues/782) Update timeframe label and fix timeframe attributes to properly display in the Result Table

## 1.2.1 - (2019-10-22)

---

### New

- [#1123](https://gitlab.com/meltano/meltano/issues/1123) Add first-class "Submit Issue" CTA to help expedite resolution when a running job fails. Also updated the "Log" CTA in the Pipelines UI to reflect a failed state.

### Fixes

- [#1172](https://gitlab.com/meltano/meltano/issues/1172) Fix analytics issue related to app version

## 1.2.0 - (2019-10-21)

---

### New

- [#1121](https://gitlab.com/meltano/meltano/issues/1121) Add ability to configure listen address of Meltano and Airflow
- [#1022](https://gitlab.com/meltano/meltano/issues/1022) Add "Autorun Query" toggle and persist the user's choice across sessions
- [#1060](https://gitlab.com/meltano/meltano/issues/1060) Auto advance to Job Log from Pipeline Schedule creation
- [#1111](https://gitlab.com/meltano/meltano/issues/1111) Auto advance to Loader installation step when an extractor lacks entity selection

### Changes

- [#1013](https://gitlab.com/meltano/meltano/issues/1013) Toast initialization and analytics initialization cleanup

### Fixes

- [#1050](https://gitlab.com/meltano/meltano/issues/1050) Fix a bug where the Job log would be created before the `transform` are run.
- [#1122](https://gitlab.com/meltano/meltano/issues/1122) `meltano elt` will now properly run when using `target-snowflake`.
- [#1159](https://gitlab.com/meltano/meltano/issues/1159) Minor UI fixes (proper `MainNav` Model icon active color during Analyze route match & "Run" auto query related cleanup) and `...NameFromRoute` refactor renaming cleanup

## 1.1.0 - (2019-10-16)

---

### New

- [#1106](https://gitlab.com/meltano/meltano/issues/1106) Add description metadata to the GitLab extractor's Ultimate License configuration setting
- [#1057](https://gitlab.com/meltano/meltano/issues/1057) Auto advance to Entity Selection when an extractor lacks configuration settings
- [#51](https://gitlab.com/meltano/meltano-marketing/issues/51) Update Google Analytics to track `appVersion`, custom `projectId`, and to properly use the default `clientId`. The CLI also now uses `client_id` to differentiate between a CLI client id (not versioned) and the project id (versioned).
- [#1012](https://gitlab.com/meltano/meltano/issues/1012) Add intelligent autofocus for improved UX in both Extractor and Loader configuration
- [#758](https://gitlab.com/meltano/meltano/issues/758) Update 'meltano permissions' to add --full-refresh command to revoke all privileges prior to granting
- [#1113](https://gitlab.com/meltano/meltano/issues/1113) Update 'meltano permissions' to have the ability to find all schemas matching a partial name such as `snowplow_*`
- [#1114](https://gitlab.com/meltano/meltano/issues/1114) Update 'meltano permissions' to include the OPERATE privilege for Snowflake warehouse

### Changes

- Compress meltano-logo.png
- [#1080](https://gitlab.com/meltano/meltano/issues/1080) Temporarily disable Intercom until userId strategy is determined
- [#1058](https://gitlab.com/meltano/meltano/issues/1058) Updated the selected state of grouped buttons to fill vs. stroke. Updated the docs to reflect the reasoning to ensure consistency in Meltano's UI visual language
- [#1068](https://gitlab.com/meltano/meltano/issues/1068) Replace dogfooding term in docs to speedrun
- [#1101](https://gitlab.com/meltano/meltano/issues/1101) Add new tour video to home page
- [#1101](https://gitlab.com/meltano/meltano/issues/1101) Update design to improve readability and contrast
- [#1115](https://gitlab.com/meltano/meltano/issues/1115) Update 'meltano permissions' to not require an identially named role for a given user

### Fixes

- [#1120](https://gitlab.com/meltano/meltano/issues/1120) Fix a concurrency bug causing `meltano select` to crash.
- [#1086](https://gitlab.com/meltano/meltano/issues/1086) Fix a concurrency issue when the `meltano.yml` file was updated.
- [#1112](https://gitlab.com/meltano/meltano/issues/1112) Fix the "Run" button to improve UX by properly reflecting the running state for auto-running queries
- [#1023](https://gitlab.com/meltano/meltano/issues/1023) Fix last vuex mutation warning with editable `localConfiguration` clone approach

### Breaks

## 1.0.1 - (2019-10-07)

---

### Fixes

- Patch technicality due to PyPi limitation (v1 already existed from a publish mistake seven+ months ago) with needed changelog New/Changes/Fixes section headers

## 1.0.0 - (2019-10-07)

---

### New

- [#1020](https://gitlab.com/meltano/meltano/issues/1020) Update Command Line Tools documentation to reflect a standard format with opportunities for improvement in the future
- [#524](https://gitlab.com/meltano/meltano/issues/524) There is a new Plugins section on the site to contain all ecosystem related libraries (i.e., extractors, loaders, etc.)

### Changes

- [#1087](https://gitlab.com/meltano/meltano/issues/1087) Fix `meltano select` not seeding the database when run as the first command.
- [#1090](https://gitlab.com/meltano/meltano/issues/1090) Update the namespace for all plugins. Also the default schema used will go back to including the `tap_` prefix to avoid conflicts with existing schemas (e.g. a local `gitlab` or `salesforce` schema). This also fixes `tap-csv` and `tap-google-analytics` not properly working after the latest Meltano release.
- [#1047](https://gitlab.com/meltano/meltano-marketing/issues/1047) Fix a bug where some configuration values were not redacted

### Fixes

### Breaks

- [#1085](https://gitlab.com/meltano/meltano/issues/1085) Fix Analyze model dropdown to properly reflect installed `models`
- [#1089](https://gitlab.com/meltano/meltano/issues/1089) Properly re-initialize the Analyze page after a new analysis is selected during an existing analysis (this issue surfaced due to the recent Analyze dropdown CTAs addition which enables an analysis change during an existing one)
- [#1092](https://gitlab.com/meltano/meltano/issues/1092) Fix async condition so the design store's `defaultState` is properly applied before loading a new design via `initializeDesign`

## 0.44.1 - (2019-10-03)

---

### New

- [#51](https://gitlab.com/meltano/meltano-marketing/issues/51) Add Google Analytics tracking acknowledgment in the UI
- [#926](https://gitlab.com/meltano/meltano/issues/926) Add step-by-step intructions for using the DigitalOcean one-click installer
- [#1076](https://gitlab.com/meltano/meltano/issues/1076) Enable Log button in pipelines UI after route change or hard refresh if a matching log exists
- [#1067](https://gitlab.com/meltano/meltano/issues/1067) Add Model landing page and update Analyze main navigation to a dropdown displaying the various analysis CTAs associated with each model
- [#1080](https://gitlab.com/meltano/meltano/issues/1080) Add live chat support on Meltano.com website using Intercom.io

### Changes

- [#1069](https://gitlab.com/meltano/meltano/issues/1069) Meltano will now use the schedule's name to run incremental jobs
- [#926](https://gitlab.com/meltano/meltano/issues/926) Move manual DigitalOcean Droplet configuration instructions to advanced tutorials
- Collapse Installation docs into a single section

### Fixes

- [#1071](https://gitlab.com/meltano/meltano/issues/1071) Fix `rehydratePollers` so the UI reflects running jobs after a hard refresh or route change (this surfaced from the recent [!963](https://gitlab.com/meltano/meltano/merge_requests/963) change)
- [#1075](https://gitlab.com/meltano/meltano/issues/1075) Fix an issue where `meltano elt` would fail when a previous job was found

## 0.44.0 - (2019-09-30)

---

### New

- [#950](https://gitlab.com/meltano/meltano/issues/950) Removed the Analyze connection configuration: Meltano will now infer connections out of each loader configuration.
- [#1002](https://gitlab.com/meltano/meltano/issues/1002) Analyze UI now displays the Topic's (analysis model's) description text if applicable
- [#1032](https://gitlab.com/meltano/meltano/issues/1032) Add 'Model' and 'Notebook' to main navigation to communicate that Meltano plans to empower users with modeling and notebooking functionality
- [#949](https://gitlab.com/meltano/meltano/issues/949) Add "Log" button and dedicated sub-UI for tracking an ELT run's status more granularly

- [#932](https://gitlab.com/meltano/meltano/issues/932) Meltano can now be upgraded from the UI directly.

### Changes

- [#1045](https://gitlab.com/meltano/meltano/issues/1045) Make it clear that 'meltano add' is not hanging while installing plugins
- [#1000](https://gitlab.com/meltano/meltano/issues/1000) Update Getting Started guide with updated screenshots and content
- [#854](https://gitlab.com/meltano/meltano/issues/854) Charts now use pretty labels rather than the ID
- [#1011](https://gitlab.com/meltano/meltano/issues/1011) Removed "Catch-up Date" in favor of default "Start Date" of extractor
- [#578](https://gitlab.com/meltano/meltano/issues/578) Remove support for `tap-zuora`.
- [#1002](https://gitlab.com/meltano/meltano/issues/1002) Update `discovery.yml` with explicit `kind: password` metadata (we infer and set input types of `password` as a safeguard, but the explicit setting is preferred)
- [#1049](https://gitlab.com/meltano/meltano/issues/1049) Change default `target-sqlite` database name to `warehouse` to not conflict with system database
- [#949](https://gitlab.com/meltano/meltano/issues/949) Update the way Meltano handles logs for ELT runs: Every elt run is logged in `.meltano/run/logs/{job_id}/elt_{timestamp}.log`. That allows Meltano to keep logs for multiple, or even concurrent, elt runs with the same `job_id`.
- [#949](https://gitlab.com/meltano/meltano/issues/949) Update "Create Pipeline" redirect logic based on the previous route being 'transforms' (this is a UX win setting up the user with the sub-UI for the next logical step vs. requiring a manual "Create" click)
- [#1051](https://gitlab.com/meltano/meltano/issues/1051) Automatically set SQLALCHEMY_DATABASE_URI config to system database URI

### Fixes

- [#1004](https://gitlab.com/meltano/meltano/issues/1004) Fix error when deselecting last attribute in Analyze
- [#1048](https://gitlab.com/meltano/meltano/issues/1048) Fix various actions that should have been mutations and did minor code convention cleanup
- [#1063](https://gitlab.com/meltano/meltano/issues/1063) Fix the "Explore" button link in Dashboards to properly account for the `namespace`

### Breaks

- [#1051](https://gitlab.com/meltano/meltano/issues/1051) Remove MELTANO_BACKEND e.a. in favor of --uri CLI option and MELTANO_DATABASE_URI env var
- [#1052](https://gitlab.com/meltano/meltano/issues/1052) Move system database into `.meltano` directory to indicate it is owned by the app and not supposed to be messed with directly by users

## 0.43.0 - (2019-09-23)

---

### New

- [#1014](https://gitlab.com/meltano/meltano/issues/1014) Meltano now logs all output from each `meltano elt` run in a log file that uses the unique job*id of the run. It can be found in `.meltano/run/logs/elt*{job_id}.log`.
- [#1014](https://gitlab.com/meltano/meltano/issues/1014) Meltano now logs all output from each `meltano elt` run in a log file that uses the unique job*id of the run. It can be found in `.meltano/run/logs/elt*{job_id}.log`.
- [#1014](https://gitlab.com/meltano/meltano/issues/1014) Meltano now logs all output from each `meltano elt` run in a log file that uses the unique `job_id` of the run. It can be found in `.meltano/run/logs/elt*{job_id}.log`.
- [#955](https://gitlab.com/meltano/meltano/issues/955) Establish baseline for demo day and how they should be run

### Changes

- [#891](https://gitlab.com/meltano/meltano/issues/891) Contributors can run webapp from root directory

### Fixes

- [#1005](https://gitlab.com/meltano/meltano/issues/1005) Fix installed plugins endpoints listing identically named plugins of different types under wrong type

## 0.42.1 - (2019-09-19)

---

### Changes

- [#987](https://gitlab.com/meltano/meltano/issues/987) Update routing to match labels (verbs vs. nouns) in effort to subtly reinforce action taking vs. solely "thing" management
- [#960](https://gitlab.com/meltano/meltano/issues/960) Improve UX by instantly displaying extractor and loader configuration UIs based on "Install" or "Configure" interaction as opposed to the prior delay (side effect of async `addPlugin`)
- [#996](https://gitlab.com/meltano/meltano/issues/996) Update conditional UI analytics stats tracking at runtime vs. build-time by sourcing state from the same backend `send_anonymous_usage_stats` flag

### Fixes

- [#992](https://gitlab.com/meltano/meltano/issues/992) Fix missing GA scripts
- [#989](https://gitlab.com/meltano/meltano/issues/989) Fix UI/UX documentation regarding recent removal of `view-header`
- [#994](https://gitlab.com/meltano/meltano/issues/994) Fix stale Pipelines Count in main navigation Pipeline badge
- [#999](https://gitlab.com/meltano/meltano/issues/999) Update yarn dependencies to resolve peer dependency warning
- [#1008](https://gitlab.com/meltano/meltano/issues/1008) Fix error on "Create Pipeline Schedule" modal when no plugins have been installed
- [#1015](https://gitlab.com/meltano/meltano/issues/1008) Support SQLite database name with and without '.db' extension
- [#1007](https://gitlab.com/meltano/meltano/issues/1007) Fix pipeline with failed job not being regarded as having completed
- [#998](https://gitlab.com/meltano/meltano/issues/998) Update Analyze UI with conditional loading indicator to prevent query generation prior to connection dialects being loaded (this solution is still useful for when inference supercedes our current manual dialect selection solution)
- [#1009](https://gitlab.com/meltano/meltano/issues/1009) Fix default ConnectorSettings validation to account for `false` (unchecked) checkbox values

### Breaks

## 0.42.0 - (2019-09-16)

---

### New

- [#976](https://gitlab.com/meltano/meltano/issues/976) Route changes will update page title in the web app

### Changes

- [Marketing #48](https://gitlab.com/meltano/meltano-marketing/issues/48) Update newsletter subscription links to redirect to our new newsletter [hosted by Substack](https://meltano.substack.com)

### Fixes

- [#965](https://gitlab.com/meltano/meltano/issues/965) Fix a regression that prevented the Meltano UI to reach the Meltano API when using an external hostname.
- [#986](https://gitlab.com/meltano/meltano/issues/986) Fix an issue where the Orchestration page would not show Airflow even when it was installed.
- [#969](https://gitlab.com/meltano/meltano/issues/969) Fix an issue where the Meltano Analyze connection would not respect the `port` configuration.
- [#964](https://gitlab.com/meltano/meltano/issues/964) Fix copy button overlap issue with top navigation
- [#970](https://gitlab.com/meltano/meltano/issues/970) Fix Meltano's m5o parser and compiler to properly namespace and isolate the definitions of different custom and packaged Topics.

## 0.41.0 - (2019-09-09)

---

### New

- [#980](https://gitlab.com/meltano/meltano/issues/980) Add Cypress for e2e testing pipeline
- [#579](https://gitlab.com/meltano/meltano/issues/579) Add `meltano schedule list` to show a project's schedules
- [#942](https://gitlab.com/meltano/meltano/issues/942) Add progress bars on various routes to improve UX feedback
- [#779](https://gitlab.com/meltano/meltano/issues/779) Add various UI polish details regarding iconography use, preloading feedback, breadcrumbs, container styling, navigation, and sub-navigation

### Changes

- [#906](https://gitlab.com/meltano/meltano/issues/906) `meltano ui` will now run in `production` per default

- [#942](https://gitlab.com/meltano/meltano/issues/942) Update Analyze Connections UI to match configuration-as-modal pattern for UX consistency regarding configuration
- [#779](https://gitlab.com/meltano/meltano/issues/779) Update all "This feature is queued..." temporary UI buttons to link to the Meltano repo issues page with a contextual search term

## 0.40.0 - (2019-09-04)

---

### New

- [#927](https://gitlab.com/meltano/meltano/issues/927) Document how to manually set up a Meltano Droplet on DigitalOcean

- [#916](https://gitlab.com/meltano/meltano/issues/916) Add Transform step as first-class and adjacent step to Extract and Load
- [#916](https://gitlab.com/meltano/meltano/issues/916) Improve Create Pipeline Schedule default selection UX by leveraging "ELT recents" concept
- [#936](https://gitlab.com/meltano/meltano/issues/936) Add "Refresh Airflow" button in Orchestrate to bypass route change or full-page refresh when iframe doesn't initially inflate as expected (this will likely be automated once the root cause is determined)
- [#899](https://gitlab.com/meltano/meltano/issues/899) Add deep linking improvements to reports and dashboards to better facilitate sharing
- [#899](https://gitlab.com/meltano/meltano/issues/899) Add "Edit" and "Explore" buttons to each report instance displayed in a dashboard to enable editing said report and exploring a fresh and unselected analysis of the same model and design
- [!546](https://gitlab.com/meltano/meltano/merge_requests/546) Add new Advanced Tutorial on how to Load CSV files to Postgres

### Changes

- [#909](https://gitlab.com/meltano/meltano/issues/909) Default names will be generated for Reports and Dashboards
- [#892](https://gitlab.com/meltano/meltano/issues/892) Improve experience for parsing Snowflake URL for ID by showing processing step
- [#935](https://gitlab.com/meltano/meltano/issues/935) Update Entity Selection to be nested in the Extract step so each ELT step is consecutive
- [#886](https://gitlab.com/meltano/meltano/issues/886) Add validation for grouping settings as the next iteration of improved form validation for generated connector settings

### Fixes

- [#931](https://gitlab.com/meltano/meltano/issues/931) Fix Analyze Connections identifier mismatch resulting from recent linting refactor
- [#919](https://gitlab.com/meltano/meltano/issues/919) Fix Airflow iframe automatic UI refresh
- [#937](https://gitlab.com/meltano/meltano/issues/937) Fix Chart.vue prop type error

## 0.39.0 - (2019-08-26)

---

### New

- [#838](https://gitlab.com/meltano/meltano/issues/838) Add indicator for speed run plugins
- [#870](https://gitlab.com/meltano/meltano/issues/870) Add global footer component in docs
- [#871](https://gitlab.com/meltano/meltano/issues/871) Add contributing link in footer of docs
- [#908](https://gitlab.com/meltano/meltano/issues/908) Add auto installation for Airflow Orchestrator for improved UX
- [#912](https://gitlab.com/meltano/meltano/issues/912) Auto run the ELT of a saved Pipeline Schedule by default
- [#907](https://gitlab.com/meltano/meltano/issues/907) Add auto select of "All" for Entities Selection step and removed the performance warning (a future iteration will address the "Recommended" implementation and the display of a resulting performance warning when "All" is selected and "Recommended" ignored)
- [#799](https://gitlab.com/meltano/meltano/issues/799) Standardized code conventions on the frontend and updated related documentation (issues related to further linting enforcement will soon follow)

### Changes

- [#838](https://gitlab.com/meltano/meltano/issues/838) Speed run plugins prioritized to top of the list
- [#896](https://gitlab.com/meltano/meltano/issues/896) Add documentation for how to do patch releases
- [#910](https://gitlab.com/meltano/meltano/issues/910) Update linting rules to enforce better standards for the frontend code base
- [#885](https://gitlab.com/meltano/meltano/issues/885) Add docs for all extractors and loaders
- [#885](https://gitlab.com/meltano/meltano/issues/885) All plugin modal cards show docs text if they have docs
- [#733](https://gitlab.com/meltano/meltano/issues/733) Improve error feedback to be more specific when plugin installation errors occur

### Fixes

- [#923](https://gitlab.com/meltano/meltano/issues/923) Fix contributing release docs merge conflict issue

## 0.38.0 - (2019-08-21)

---

### New

- [#746](https://gitlab.com/meltano/meltano/issues/746) Add CTA to specific dashboard in "Add to Dashboard" sub-UI
- [#746](https://gitlab.com/meltano/meltano/issues/746) Add toast feedback on success, update, or error for schedules, reports, and dashboards
- [#814](https://gitlab.com/meltano/meltano/issues/814) Install Airflow via the Orchestration UI (we may do this in the background automatically in the future)

### Changes

- [#901](https://gitlab.com/meltano/meltano/issues/901) Update entities plugins to be alphabetically sorted for consistency with extractors ordering

### Fixes

- [#746](https://gitlab.com/meltano/meltano/issues/746) Prevent duplicate schedule, report, and dashboard creation if there is an existing item
- [#976](https://gitlab.com/meltano/meltano/issues/900) Fix fallback v976e Route changes will update page title in the web appfor Iso8601 dates/times
- [#903](https://gitlab.com/meltano/meltano/issues/903) Fix columns display issue for the base table in Analyze

### Breaks

## 0.37.2 - (2019-08-19)

---

### Fixes

- [#894](https://gitlab.com/meltano/meltano/issues/894) Fix issue with static asset paths

## 0.37.1 - (2019-08-19)

---

### Fixes

- [#894](https://gitlab.com/meltano/meltano/issues/894) Fix build issues with new Vue CLI 3 build process

## 0.37.0 - (2019-08-19)

---

### New

- [#763](https://gitlab.com/meltano/meltano/issues/763) Add inference to auto install related plugins after a user installs a specific extractor
- [#867](https://gitlab.com/meltano/meltano/issues/867) Add fallback values (if they aren't set in the `discovery.yml`) for `start date`, `start time`, and `end date` for all connectors so the user has potentially one less interaction to make per connector configuration

### Changes

- [#342](https://gitlab.com/meltano/meltano/issues/342) Swap UI app directory "webapp" and upgrade to Vue CLI 3
- [#882](https://gitlab.com/meltano/meltano/issues/882) Update navigation and subnavigation labels to verbs vs. nouns to inspire action and productivity when using the UI
- [#700](https://gitlab.com/meltano/meltano/issues/700) Update documentation to remove "\$" and trim spaces to make CLI command copy/paste easier
- [#878](https://gitlab.com/meltano/meltano/issues/878) Write a [tutorial to help users get started with PostgreSQL](http://www.meltano.com/docs/loaders.html#postgresql-database)
- [#883](https://gitlab.com/meltano/meltano/issues/883) Break Extractors and Loaders sections out in the docs
- [#889](https://gitlab.com/meltano/meltano/issues/889) Allow for githooks to lint on commit
- [#835](https://gitlab.com/meltano/meltano/issues/835) Pipeline name in Schedule creation will have an automatic default

### Fixes

- [#872](https://gitlab.com/meltano/meltano/issues/872) Updated `tap-marketo` and `tap-stripe` to leverage password input type while also improving the input type password fallback
- [#882](https://gitlab.com/meltano/meltano/issues/882) Fix recent minor regression regarding `Dashboard` routing
- [#858](https://gitlab.com/meltano/meltano/issues/858) Fix `job_state` bug so that ELT run status polling can properly resume as expected
- [#890](https://gitlab.com/meltano/meltano/issues/890) Fix implementation of default configuration setting to use less code

## 0.36.0 - (2019-08-12)

---

### New

- [#793](https://gitlab.com/meltano/meltano/issues/793) Add introduction module to Connector Settings to allow for helper text as far as signup and documentation links
- [#796](https://gitlab.com/meltano/meltano/issues/796) Add dropdown option to Connector Settings to allow for more defined UI interactions
- [#802](https://gitlab.com/meltano/meltano/issues/802) Add support for Query Filters over columns that are not selected
- [#855](https://gitlab.com/meltano/meltano/issues/855) Add empty state to Dashboards and cleaned up styling for consistency with Analyze's layout
- [#856](https://gitlab.com/meltano/meltano/issues/856) Add contextual information to the Analyze Connection UI to aid user understanding
- [#800](https://gitlab.com/meltano/meltano/issues/800) Add save success feedback for connectors, entities, and connections
- [#817](https://gitlab.com/meltano/meltano/issues/817) Add [Meltano explainer video](https://www.youtube.com/watch?v=2Glsf89WQ5w) to the front page of Meltano.com

### Changes

- [#794](https://gitlab.com/meltano/meltano/issues/794) Update Snowflake fields to have descriptions and utilize tooltip UI
- [#853](https://gitlab.com/meltano/meltano/issues/853) Improve UX for multi-attribute ordering (wider sub-UI for easier reading, clear drop target, and clearer drag animation for reenforcing sorting interaction)
- [#735](https://gitlab.com/meltano/meltano/issues/735) Update Entities UI to only display entity selection "Configure" CTAs for installed (vs. previously all) extractors
- [#548](https://gitlab.com/meltano/meltano/issues/548) Update Meltano mission, vision and path to v1 on [roadmap page](https://meltano.com/docs/roadmap.html) of Meltano.com
- [#824](https://gitlab.com/meltano/meltano/issues/824) Update `meltano select` to use the unique `tap_stream_id` instead of the `stream` property for filtering streams. This adds support for taps with multiple streams with the same name, like, for example, the ones produced by `tap-postgres` when tables with the same name are defined in different schemas.
- [#842](https://gitlab.com/meltano/meltano/issues/842) Collapse Deployment section in the docs to be under [Installation](https://meltano.com/docs/installation.html)

### Fixes

- [#855](https://gitlab.com/meltano/meltano/issues/855) Fix bug that duplicated a dashboard's `reportIds` that also prevented immediate UI feedback when reports were toggled (added or removed) from a dashboard via Analyze's "Add to Dashboard" dropdown
- [#851](https://gitlab.com/meltano/meltano/issues/851) Fix report saving and loading to work with filters and sortBy ordering
- [#852](https://gitlab.com/meltano/meltano/issues/852) Update Scheduling UI to have "Run" button at all times vs conditionally to empower users to run one-off ELT pipelines even if Airflow is installed
- [#852](https://gitlab.com/meltano/meltano/issues/852) Update Scheduling UI "Interval" column with CTA to install Airflow while communicating why via tooltip
- [#852](https://gitlab.com/meltano/meltano/issues/852) Fix initial Orchestration page hydration to properly reflect Airflow installation status
- [#831](https://gitlab.com/meltano/meltano/issues/831) Update `meltano elt` to exit with 1 and report dbt's exit code on an error message when dbt exits with a non-zero code.
- [#857](https://gitlab.com/meltano/meltano/issues/857) Update PluginDiscoveryService to use the cached `discovery.yml` when Meltano can not connect to `meltano.com` while trying to fetch a fresh version of the discovery file.
- [#850](https://gitlab.com/meltano/meltano/issues/850) Fix entities response so entities display as expected (as assumed this simple fix was due to our recent interceptor upgrade)
- [#800](https://gitlab.com/meltano/meltano/issues/800) Fix connector and connection settings to display saved settings by default while falling back and setting defaults if applicable

## 0.35.0 - (2019-08-05)

---

### New

- [!781](https://gitlab.com/meltano/meltano/merge_requests/781) Add new Advanced Tutorial on how to use tap-postgres with Meltano
- [#784](https://gitlab.com/meltano/meltano/issues/784) Add multiple attribute ordering with drag and drop ordering in the UI

### Changes

- [#784](https://gitlab.com/meltano/meltano/issues/784) As part of multiple attribute sorting and keeping the attributes and results sub-UIs in sync, we know autorun queries based on user interaction after the initial explicit "Run" button interaction

## 0.34.2 - (2019-08-01)

---

### Fixes

- [#821](https://gitlab.com/meltano/meltano/issues/821) Fix `meltano config` not properly loading settings defined in the `meltano.yml`
- [#841](https://gitlab.com/meltano/meltano/issues/841) Fix a problem when model names were mangled by the API

## 0.34.1 - (2019-07-30)

---

### Fixes

- [#834](https://gitlab.com/meltano/meltano/issues/834) Fixed a problem with the Meltano UI not having the proper API URL set

## 0.34.0 - (2019-07-29)

---

### New

- [#757](https://gitlab.com/meltano/meltano/issues/757) Update 'meltano permissions' to add support for GRANT ALL and FUTURE GRANTS on tables in schemas
- [#760](https://gitlab.com/meltano/meltano/issues/760) Update 'meltano permissions' to add support for granting permissions on VIEWs
- [#812](https://gitlab.com/meltano/meltano/issues/812) `meltano ui` will now stop stale Airflow workers when starting
- [#762](https://gitlab.com/meltano/meltano/issues/762) Added run ELT via the UI (manages multiple and simultaneous runs)
- [#232](https://gitlab.com/meltano/meltano/issues/232) Meltano now bundles Alembic migrations to support graceful database upgrades

### Changes

- [#828](https://gitlab.com/meltano/meltano/issues/828) Docker installation instructions have been dogfooded, clarified, and moved to Installation section
- [#944](https://gitlab.com/meltano/meltano/issues/944) Update the Transform step's default to "Skip"

### Fixes

- [#807](https://gitlab.com/meltano/meltano/issues/807) Fix filter input validation when editing saved filters
- [#822](https://gitlab.com/meltano/meltano/issues/822) Fix pipeline schedule naming via slugify to align with Airflow DAG naming requirements
- [#820](https://gitlab.com/meltano/meltano/issues/820) Fix `meltano select` not properly connecting to the system database
- [#787](https://gitlab.com/meltano/meltano/issues/787) Fix results sorting to support join tables
- [#832](https://gitlab.com/meltano/meltano/issues/832) Fix schedule creation endpoint to return properly typed response (this became an issue as a result of our recent case conversion interceptor)
- [#819](https://gitlab.com/meltano/meltano/issues/819) Running the Meltano UI using gunicorn will properly update the system database

## 0.33.0 - (2019-07-22)

---

### New

- [#788](https://gitlab.com/meltano/meltano/issues/788) Reydrate filters in Analyze UI after loading a saved report containing filters

### Changes

- [#804](https://gitlab.com/meltano/meltano/issues/804) Connection set in the Design view are now persistent by Design

### Fixes

- [#788](https://gitlab.com/meltano/meltano/issues/788) Properly reset the default state of the Analyze UI so stale results aren't displayed during a new analysis
- [!806](https://gitlab.com/meltano/meltano/merge_requests/806) Fix filters editing to prevent input for `is_null` and `is_not_null` while also ensuring edits to existing filter expressions types adhere to the same preventitive input.
- [#582](https://gitlab.com/meltano/meltano/issues/582) Remove the `export` statements in the default `.env` initialized by `meltano init`.
- [#816](https://gitlab.com/meltano/meltano/issues/816) Fix `meltano install` failing when connections where specified in the `meltano.yml`
- [#786](https://gitlab.com/meltano/meltano/issues/786) Fixed an issue with the SQL engine would mixup table names with join/design names
- [#808](https://gitlab.com/meltano/meltano/issues/808) Fix filter aggregate value with enforced number via `getQueryPayloadFromDesign()` as `input type="number"` only informs input keyboards on mobile, and does not enforce the Number type as expected

## 0.32.2 - (2019-07-16)

---

### New

- [#759](https://gitlab.com/meltano/meltano/issues/759) Added filtering functionality to the Analyze UI while additionally cleaning it up from a UI/UX lens

## 0.32.1 - (2019-07-15)

---

### Fixes

- [#792](https://gitlab.com/meltano/meltano/issues/792) Fix an error when trying to schedule an extractor that didn't expose a `start_date`.

## 0.32.0 - (2019-07-15)

---

### New

- [!718](https://gitlab.com/meltano/meltano/merge_requests/718) Add support for filters (WHERE and HAVING clauses) to MeltanoQuery and Meltano's SQL generation engine
- [#748](https://gitlab.com/meltano/meltano/issues/748) Added the `Connections` plugin to move the Analyze connection settings to the system database
- [#748](https://gitlab.com/meltano/meltano/issues/748) Added the `meltano config` command to manipulate a plugin's configuration

### Fixes

[!726](https://gitlab.com/meltano/meltano/merge_requests/726) Fixed InputDateIso8601's default value to align with HTML's expected empty string default

## 0.31.0 - (2019-07-08)

---

### New

- [#766](https://gitlab.com/meltano/meltano/issues/766) Add Codeowners file so that the "approvers" section on MRs is more useful for contributors
- [#750](https://gitlab.com/meltano/meltano/issues/750) Various UX updates (mostly tooltips) to make the configuration UI for scheduling orchestration easier to understand
- [#739](https://gitlab.com/meltano/meltano/issues/739) Updated `discovery.yml` for better consistency of UI order within each connector's settings (authentication -> contextual -> start/end dates). Improved various settings' `kind`, `label`, and `description`. Added a `documentation` prop to provide a documentation link for involved settings (temp until we have better first class support for more complex setting types)

### Fixes

- [#737](https://gitlab.com/meltano/meltano/issues/737) Fixed UI flash for connector settings when installation is complete but `configSettings` has yet to be set
- [#751](https://gitlab.com/meltano/meltano/issues/751) Fixed the Orchestrations view by properly checking if Airflow is installed so the correct directions display to the user

## 0.30.0 - (2019-07-01)

---

### New

- [#736](https://gitlab.com/meltano/meltano/issues/736) Add "Cancel", "Next", and a message to the entities UI when an extractor doesn't support discovery and thus entity selection
- [#730](https://gitlab.com/meltano/meltano/issues/730) Updated Analyze Models page UI with improved content organization so it is easier to use
- [#710](https://gitlab.com/meltano/meltano/issues/710) Updated connector (extractor and loader) settings with specific control type (text, password, email, boolean, and date) per setting, added form validation, and added an inference by default for password and token fields as a protective measure
- [#719](https://gitlab.com/meltano/meltano/issues/719) Added InputDateIso8601.vue component to standardize date inputs in the UI while ensuring the model data remains in Iso8601 format on the frontend.
- [#643](https://gitlab.com/meltano/meltano/issues/643) Updated `minimallyValidated` computeds so that new users are intentionally funneled through the pipelines ELT setup UI (previously they could skip past required steps)
- [#752](https://gitlab.com/meltano/meltano/issues/752) Fix the schedule having no start_date when the extractor didn't expose a `start_date` setting

### Fixes

- [!703](https://gitlab.com/meltano/meltano/merge_requests/703) Fix `ScheduleService` instantiation due to signature refactor

## 0.29.0 - (2019-06-24)

---

### New

- [#724](https://gitlab.com/meltano/meltano/issues/724) Add the `model-gitlab-ultimate` plugin to Meltano. It includes .m5o files for analyzing data available for Gitlab Ultimate or Gitlab.com Gold accounts (e.g. Epics, Epic Issues, etc) fetched using the Gitlab API. Repository used: https://gitlab.com/meltano/model-gitlab-ultimate
- [#723](https://gitlab.com/meltano/meltano/issues/723) Add proper signage and dedicated sub-navigation area in views/pages. Standardized the view -> sub-view markup relationships for consistent layout. Directory refactoring for improved organization.
- [#612](https://gitlab.com/meltano/meltano/issues/612) Move the plugins' configuration to the database, enabling configuration from the UI

### Changes

- [#636](https://gitlab.com/meltano/meltano/issues/636) Refactored connector logo related logic into a ConnectorLogo component for code cleanliness, reusability, and standardization
- [#728](https://gitlab.com/meltano/meltano/issues/728) Change error notification button link to open the bugs issue template

### Fixes

- [#718](https://gitlab.com/meltano/meltano/issues/718) Fix dynamically disabled transforms always running. Transforms can now be dynamically disabled inside a dbt package and Meltano will respect that. It will also respect you and your time.
- [#684](https://gitlab.com/meltano/meltano/issues/684) Enables WAL on SQLite to handle concurrent processes gracefully
- [#732](https://gitlab.com/meltano/meltano/issues/732) Fix plugin installation progress bar that wasn't updating upon installation completion

## 0.28.0 - (2019-06-17)

---

### New

- [!683](https://gitlab.com/meltano/meltano/issues/683) Add `--start-date` to `meltano schedule` to give the control over the catch up logic to the users
- [#651](https://gitlab.com/meltano/meltano/issues/651) Added model installation in the Analyze UI to bypass an otherwise "back to the CLI step"
- [#676](https://gitlab.com/meltano/meltano/issues/676) Add pipeline schedule UI for viewing and saving pipeline schedules for downstream use by Airflow/Orchestration

### Changes

- [#708](https://gitlab.com/meltano/meltano/issues/708) Enable `tap-gitlab` to run using Gitlab Ultimate and Gitlab.com Gold accounts and extract Epics and Epic Issues.
- [#711](https://gitlab.com/meltano/meltano/issues/711) Add new call to action for submitting an issue on docs site
- [#717](https://gitlab.com/meltano/meltano/issues/717) Enable `dbt-tap-gitlab` to run using Gitlab Ultimate and Gitlab.com Gold accounts and generate transformed tables that depend on Epics and Epic Issues.

### Fixes

- [#716](https://gitlab.com/meltano/meltano/issues/716) Fix entities UI so only installed extractors can edit selections
- [#715](https://gitlab.com/meltano/meltano/issues/715) Remove reimport of Bulma in `/orchestration` route to fix borked styling

## 0.27.0 - (2019-06-10)

---

### New

- [!640](https://gitlab.com/meltano/meltano/merge_requests/640) Google Analytics logo addition for recent tap-google-analytics Extractor addition
- [#671](https://gitlab.com/meltano/meltano/issues/671) Add the `tap-google-analytics` transform to Meltano. It is using the dbt package defined in https://gitlab.com/meltano/dbt-tap-google-analytics
- [#672](https://gitlab.com/meltano/meltano/issues/672) Add the `model-google-analytics` plugin to Meltano. It includes .m5o files for analyzing data fetched from the Google Analytics Reporting API. Repository used: https://gitlab.com/meltano/model-google-analytics
- [#687](https://gitlab.com/meltano/meltano/issues/687) Implemented a killswitch to prevent undefined behaviors when a Meltano project is not compatible with the installed `meltano` version

### Fixes

- [#661](https://gitlab.com/meltano/meltano/issues/661) Fixed empty UI for extractors that lack configuration settings by providing feedback message with actionable next steps
- [#663](https://gitlab.com/meltano/meltano/issues/663) Fixed Airflow error when advancing to Orchestration step after installing and saving a Loader configuration
- [#254](https://gitlab.com/meltano/meltano/issues/254) Fixed `meltano init` not working on terminal with cp1252 encoding
- [#254](https://gitlab.com/meltano/meltano/issues/254) Fixed `meltano add/install` crashing on Windows
- [#664](https://gitlab.com/meltano/meltano/issues/664) Minor CSS fix ensuring Airflow UI height is usable (side-effect of recent reparenting)
- [#679](https://gitlab.com/meltano/meltano/issues/679) Fix an issue with `meltano select` emitting duplicate properties when the property used the `anyOf` type
- [#650](https://gitlab.com/meltano/meltano/issues/650) Add `MELTANO_DISABLE_TRACKING` environment variable to disable all tracking
- [#670](https://gitlab.com/meltano/meltano/issues/670) Update tests to not send tracking events

## 0.26.0 - (2019-06-03)

---

### New

- [#603](https://gitlab.com/meltano/meltano/issues/603) `meltano select` now supports raw JSON Schema as a valid Catalog
- [#537](https://gitlab.com/meltano/meltano/issues/537) Add Extractor for Google Analytics (`tap-google-analytics`) to Meltano. It uses the tap defined in https://gitlab.com/meltano/tap-google-analytics/

### Changes

- [#621](https://gitlab.com/meltano/meltano/issues/621) Added new tutorial for tap-gitlab
- [#657](https://gitlab.com/meltano/meltano/issues/657) Update Analyze page to have single purpose views

### Fixes

- [#645](https://gitlab.com/meltano/meltano/issues/645) Fixed confusion around Loader Settings and Analytics DB Connector Settings
- [#580](https://gitlab.com/meltano/meltano/issues/580) Fixed `project_compiler` so the Analyze page can properly display custom topics
- [#658](https://gitlab.com/meltano/meltano/issues/658) Fixed the Analyze page when no models are present
- [#603](https://gitlab.com/meltano/meltano/issues/603) Fix an issue where `meltano select` would incorrectly report properties as excluded
- [#603](https://gitlab.com/meltano/meltano/issues/603) Fix an issue where `meltano select` incorrectly flatten nested properties
- [#553](https://gitlab.com/meltano/meltano/issues/553) Fix an issue where running `meltano select --list` for the first time would incorrectly report properties

### Break

## 0.25.0 - (2019-05-28)

---

### New

- [#586](https://gitlab.com/meltano/meltano/issues/586) `meltano ui` now automatically start Airflow if installed; Airflow UI available at `Orchestration`.
- [#592](https://gitlab.com/meltano/meltano/issues/592) Added baseline UX feedback via toast for uncaught API response errors with a link to "Submit Bug"
- [#642](https://gitlab.com/meltano/meltano/issues/642) Improved UX during extractor plugin installation so settings can be configured _during_ installation as opposed to waiting for the (typically lengthy) install to complete
- [!647](https://gitlab.com/meltano/meltano/merge_requests/647) Added preloader for occasional lengthy extractor loading and added feedback for lengthy entities loading
- [#645](https://gitlab.com/meltano/meltano/issues/645) Added an Analyze landing page to facilitate future sub-UIs including the Analyze database settings; Added proper Loader Settings UI.

### Fixes

- [#645](https://gitlab.com/meltano/meltano/issues/645) Fixed confusion around Loader Settings and Analyze database settings

## 0.24.0 - (2019-05-06)

---

### New

- [#622](https://gitlab.com/meltano/meltano/issues/622) Added ELT flow UI Routes & Deep Linking to advance user through next steps after each step's save condition vs. requiring them to manually click the next step to advance
- [#598](https://gitlab.com/meltano/meltano/issues/598) Updated color and greyscale use in the context of navigation and interactive elements to better communicate UI hierarchy
- [#607](https://gitlab.com/meltano/meltano/issues/607) Add "All/Default/Custom" button bar UI for improved entities selection UX
- [#32](https://gitlab.com/meltano/meltano-marketing/issues/32) Integrate Algolia Search for docs
- [#590](https://gitlab.com/meltano/meltano/issues/590) Add documentation for deploying Meltano in ECS
- [#628](https://gitlab.com/meltano/meltano/issues/628) Add documentation for tap-mongodb
- [!605](https://gitlab.com/meltano/meltano/merge_requests/605) Added tooltips for areas of UI that are WIP for better communication of a feature's status

### Changes

- [375](https://gitlab.com/meltano/meltano/issues/375) Meltano can now run on any host/port

### Fixes

- [#595](https://gitlab.com/meltano/meltano/issues/595) Fix `meltano invoke` not working properly with `dbt`
- [#606](https://gitlab.com/meltano/meltano/issues/606) Fix `SingerRunner.bookmark_state()` to properly handle and store the state output from Targets as defined in the Singer.io Spec.

## 0.23.0 - (2019-04-29)

---

### New

- [#32](https://gitlab.com/meltano/meltano-marketing/issues/32) Integrate Algolia Search for docs

### Changes

- [#522](https://gitlab.com/meltano/meltano/issues/522) Update Carbon tutorial with new instructions and screenshots

## 0.22.0 - (2019-04-24)

---

### New

- [#477](https://gitlab.com/meltano/meltano/issues/477) Add ability for users to sign up for email newsletters
- [!580](https://gitlab.com/meltano/meltano/merge_requests/580) Add sorting to plugins for improved UX, both UI via extractors/loaders/etc. and `meltano discover all` benefit from sorted results
- [!528](https://gitlab.com/meltano/meltano/issues/528) Add documentation for RBAC alpha feature and environment variables

### Changes

- [#588](https://gitlab.com/meltano/meltano/issues/588) Updated core navigation and depth hierarchy styling to facilitate main user flow and improved information architecture
- [#591](https://gitlab.com/meltano/meltano/issues/591) Revert #484: remove `meltano ui` being run outside a Meltano project.
- [#584](https://gitlab.com/meltano/meltano/issues/584) Initial v1 for enabling user to setup ELT linearly through the UI via a guided sequence of steps

### Fixes

- [#600](https://gitlab.com/meltano/meltano/issues/600) Fix a bug with meltano select when the extractor would output an invalid schema
- [#597](https://gitlab.com/meltano/meltano/issues/597) Automatically open the browser when `meltano ui` is run

## 0.21.0 - (2019-04-23)

---

### New

- [#477](https://gitlab.com/meltano/meltano/issues/477) Add ability for users to sign up for email newsletters

### Changes

- [#591](https://gitlab.com/meltano/meltano/issues/591) Revert #484: remove `meltano ui` being run outside a Meltano project.

## 0.20.0 - (2019-04-15)

---

### New

- Add documentation on custom transformations and models. Link to Tutorial: https://www.meltano.com/tutorials/create-custom-transforms-and-models.html

## 0.19.1 - (2019-04-10)

---

### New

- [#539](https://gitlab.com/meltano/meltano/issues/539) Add Tutorial for "Using Jupyter Notebooks" with Meltano
- [#534](https://gitlab.com/meltano/meltano/issues/534) Add UI entity selection for a given extractor
- [#520](https://gitlab.com/meltano/meltano/issues/520) Add v1 UI for extractor connector settings
- [#486](https://gitlab.com/meltano/meltano/issues/486) Add the `model-gitlab` plugin to Meltano. It includes .m5o files for analyzing data fetched using the Gitlab API. Repository used: https://gitlab.com/meltano/model-gitlab
- [#500](https://gitlab.com/meltano/meltano/issues/500) Add the `model-stripe` plugin to Meltano. It includes .m5o files for analyzing data fetched using the Stripe API. Repository used: https://gitlab.com/meltano/model-stripe
- [#440](https://gitlab.com/meltano/meltano/issues/440) Add the `model-zuora` plugin to Meltano. It includes .m5o files for analyzing data fetched using the Zuora API. Repository used: https://gitlab.com/meltano/model-zuora
- [#541](https://gitlab.com/meltano/meltano/issues/541) Add a 404 page for missing routes on the web app

### Fixes

- [#576](https://gitlab.com/meltano/meltano/issues/576) Fix switching between designs now works
- [#555](https://gitlab.com/meltano/meltano/issues/555) Fix `meltano discover` improperly displaying plugins
- [#530](https://gitlab.com/meltano/meltano/issues/530) Fix query generation for star schemas
- [#575](https://gitlab.com/meltano/meltano/issues/575) Move Airflow configuration to .meltano/run/airflow
- [#571](https://gitlab.com/meltano/meltano/issues/571) Fix various routing and API endpoint issues related to recent `projects` addition

## 0.19.0 - (2019-04-08)

---

### New

- [#513](https://gitlab.com/meltano/meltano/issues/513) Added initial e2e tests for the UI
- [#431](https://gitlab.com/meltano/meltano/issues/431) Add the `tap-zendesk` transform to Meltano. It is using the dbt package defined in https://gitlab.com/meltano/dbt-tap-zendesk
- [484](https://gitlab.com/meltano/meltano/issues/484) Updated `meltano ui` to automatically launch the UI, and projects from the UI (previously only an option in the CLI)
- [#327](https://gitlab.com/meltano/meltano/issues/327) Add `meltano add --custom` switch to enable integration of custom plugins
- [#540](https://gitlab.com/meltano/meltano/issues/540) Add CHANGELOG link in intro section of the docs
- [#431](https://gitlab.com/meltano/meltano/issues/431) Add the `model-zendesk` plugin to Meltano. It includes .m5o files for analyzing data fetched using the Zendesk API. Repository used: https://gitlab.com/meltano/model-zendesk
- [!544](https://gitlab.com/meltano/meltano/merge_requests/544) Add support for extracting data from CSV files by adding [tap-csv](https://gitlab.com/meltano/tap-csv) to Meltano
- [#514](https://gitlab.com/meltano/meltano/issues/514) Add 'airflow' orchestrators plugin to enable scheduling
- Add the `tap-zuora` transform to Meltano. It is using the dbt package defined in https://gitlab.com/meltano/dbt-tap-zuora

### Changes

- [#455](https://gitlab.com/meltano/meltano/issues/455) Add documentation about `target-snowflake`

### Fixes

- [#507](https://gitlab.com/meltano/meltano/issues/507) Ensure design name and table name don't need to match so multiple designs can leverage a single base table
- [#551](https://gitlab.com/meltano/meltano/issues/551) Fix HDA queries generated when an attribute is used both as a column and as an aggregate.
- [#559](https://gitlab.com/meltano/meltano/issues/559) Add support for running custom transforms for taps without default dbt transforms.

## 0.18.0 - (2019-04-02)

---

### New

- [#432](https://gitlab.com/meltano/meltano/issues/432) Add the `tap-zuora` transform to Meltano. It is using the dbt package defined in https://gitlab.com/meltano/dbt-tap-zuora

### Changes

- Remove Snowflake references from advanced tutorial.
- [#2 dbt-tap-zuora](https://gitlab.com/meltano/dbt-tap-zuora/issues/2) Remove custom SFDC related attributes from Zuora Account and Subscription Models
- Update [Contributing - Code Style](https://meltano.com/docs/contributing.html#code-style) documentation to including **pycache** troubleshooting

### Fixes

- [#529](https://gitlab.com/meltano/meltano/issues/529) Resolve "SFDC Tutorial - ELT Fails due to invalid schema.yml" by [#4 dbt-tap-salesforce](https://gitlab.com/meltano/dbt-tap-salesforce/issues/4) removing the schema.yml files from the dbt models for tap-salesforce.
- [#502](https://gitlab.com/meltano/meltano/issues/502) Fix the situation where an m5o has no joins, the design still will work.

## 0.17.0 - (2019-03-25)

---

### New

- [#485](https://gitlab.com/meltano/meltano/issues/485) Added various UI unit tests to the Analyze page
- [#370](https://gitlab.com/meltano/meltano/issues/370) Enabled authorization using role-based access control for Designs and Reports

### Changes

- [#283](https://gitlab.com/meltano/meltano/issues/283) Silence pip's output when there is not error
- [#468](https://gitlab.com/meltano/meltano/issues/468) Added reminder in docs regarding the need for `source venv/bin/activate` in various situations and added minor copy updates

### Fixes

- [#433](https://gitlab.com/meltano/meltano/issues/433) Add the `sandbox` configuration to `tap-zuora`.
- [#501](https://gitlab.com/meltano/meltano/issues/501) Fix `meltano ui` crashing when the OS ran out of file watcher.
- [#510](https://gitlab.com/meltano/meltano/issues/510) Fix an issue when finding the current Meltano project in a multi-threaded environment.
- [#494](https://gitlab.com/meltano/meltano/issues/494) Improved documentation around tutorials and Meltano requirements
- [#492](https://gitlab.com/meltano/meltano/issues/492) A few small contextual additions to help streamline the release process
- [#503](https://gitlab.com/meltano/meltano/issues/503) Fix a frontend sorting issue so the backend can properly generate an up-to-date query

## 0.16.0 - (2019-03-18)

---

### New

- Add support for extracting data from Gitlab through the updated tap-gitlab (https://gitlab.com/meltano/tap-gitlab)
- Add the `tap-gitlab` transform to Meltano. It is using the dbt package defined in https://gitlab.com/meltano/dbt-tap-gitlab
- Add "Copy to Clipboard" functionality to code block snippets in the documentation
- Add the `tap-stripe` transform to Meltano. It is using the dbt package defined in https://gitlab.com/meltano/dbt-tap-stripe
- Add new command `meltano add model [name_of_model]`
- Add models to the available plugins

### Changes

- Various documentation [installation and tutorial improvements](https://gitlab.com/meltano/meltano/issues/467#note_149858308)
- Added troubleshooting button to help users add context to a pre-filled bug issue

### Fixes

- Fix the API database being mislocated
- Replaced the stale Meltano UI example image in the Carbon Emissions tutorial
- 473: Fix the docker image (meltano/meltano) from failing to expose the API

## 0.15.1 - (2019-03-12)

---

### Fixes

- locks down dependencies for issues with sqlalchemy snowflake connector

## 0.15.0 - (2019-03-11)

---

### New

- Add Salesforce Tutorial to the docs
- Add documentation for the permissions command
- Add tracking for the `meltano ui` command

### Fixes

- Updated analytics to properly recognize SPA route changes as pageview changes

## 0.14.0 - (2019-03-04)

---

### New

- Update stages table style in docs
- Add custom transforms and models tutorial to the docs

### Changes

- Add api/v1 to every route
- Update DbtService to always include the my_meltano_project model when transform runs

### Fixes

- Resolved duplicate display issue of Dashboards and Reports on the Files page
- Removed legacy `carbon.dashboard.m5o` (regression from merge)
- Updated dashboards and reports to use UI-friendly name vs slugified name
- Fix minor clipped display issue of right panel on `/settings/database`
- Fix minor display spacing in left panel of Settings
- Fix dashboard page to properly display a previously active dashboard's updated reports
- Fix pre-selected selections for join aggregates when loading a report
- Fix charts to display multiple aggregates (v1)
- Fix 404 errors when refreshing the frontend
- Fix a regression where the Topics would not be shown in the Files page

## 0.13.0 - (2019-02-25)

---

### New

- Add the `tap-salesforce` transform to Meltano. It is using the dbt package defined in https://gitlab.com/meltano/dbt-tap-salesforce
- Add m5o model and tables for tap-salesforce
- Updated the deep-link icon (for Dashboards/Reports on the Files page)

### Changes

- Polished the RBAC view, making it clearer the feature is experimental.
- Rename "Models" to "Topics"
- Use the current connection's schema when generating queries at run time for Postgres Connections.
- Add support for multiple Aggregates over the same attribute when generating HDA queries.

## 0.12.0 - (2019-02-21)

---

### New

- UI cleanup across routes (Analyze focus) and baseline polish to mitigate "that looks off comments"
- Update installation and contributing docs
- Meltano implement role-based access control - [!368](https://gitlab.com/meltano/meltano/merge_requests/368)
- Add version CLI commands for checking current Meltano version
- Add deep linking to dashboards
- Add deep linking to reports

### Fixes

- Fixed a problem when environment variables where used as default values for the CLI - [!390](https://gitlab.com/meltano/meltano/merge_requests/390)
- Fixed dashboards initial load issue due to legacy (and empty) `carbon.dashboard.m5o` file
- New standardized approach for `.m5o` id generation (will need to remove any dashboard.m5o and report.m5o)

## 0.11.0 - (2019-02-19)

---

### New

- Update installation and contributing docs
- Add support for generating Hyper Dimensional Aggregates (HDA)
- Add internal Meltano classes for representing and managing Designs, Table, Column, Aggregate, Definitions, and Query definitions

### Changes

- Move core functionality out of `api/controllers` to `/core/m5o` (for m5o and m5oc management) and `/core/sql` (for anything related to sql generation)

### Fixes

- Fixed a problem when environment variables where used as default values for the CLI - [!390](https://gitlab.com/meltano/meltano/merge_requests/390)

## 0.10.0 - (2019-02-12)

---

### New

- Add gunicorn support for Meltano UI as a WSGI application - [!377](https://gitlab.com/meltano/meltano/merge_requests/377)
- Meltano will now generate the minimal joins when building SQL queries - [!382](https://gitlab.com/meltano/meltano/merge_requests/382)

### Changes

- Add analytics to authentication page
- Meltano will now use SQLite for the job log. See https://meltano.com/docs/architecture.html#job-logging for more details.
- Removed manual `source .env` step in favor of it running automatically

### Fixes

- Meltano will correctly source the `.env`
- fixed charts to render as previously they were blank
- Fixed Analyze button groupd CSS to align as a single row

### Breaks

- Meltano will now use SQLite for the job log. See https://meltano.com/docs/architecture.html#job-logging for more details.
- URL routing updates ('/model' to '/files', removed currently unused '/extract', '/load', '/transform' and '/project/new')

## 0.9.0 - (2019-02-05)

---

### New

- add ability to save reports
- add ability to update an active report during analysis
- add ability to load reports
- add dashboards page and related add/remove report functionality

### Changes

- Generate default `Meltano UI` connection for the `meltano.db` SQLite DB when a new project is created with `meltano init`
- updated main navigation to Files, Analysis, and Dashboards
- Update the `meltano permissions grant` command to fetch the existing permissions from the Snowflake server and only return sql commands for permissions not already assigned
- Add `--diff` option to the `meltano permissions grant` command to get a full diff with the permissions already assigned and new ones that must be assigned

### Fixes

- Entry model definition correctly defines `region_id`.
- Updated the Fundamentals documentation section regarding reports
- Fixed Files page for empty state of Dashboards and Reports
- Fixed Analyze page's left column to accurately preselect columns and aggregates after loading a report

## 0.8.0 - (2019-01-29)

---

### New

- Add tracking of anonymous `meltano cli` usage stats to Meltano's Google Analytics Account
- Add `project_config.yml` to all meltano projects to store concent for anonymous usage tracking and the project's UUID

### Changes

- Add `--no_usage_stats` option to `meltano init <project_name>` to allow users to opt-out from anonymous usage stats tracking
- Bundled Meltano models are now SQLite compatible.

## 0.7.0 - (2019-01-22)

---

### New

- Added basic authentication support for meltano ui.
- Meltano will now automatically source the .env
- Updated docs with `.m5o` authoring requirements and examples
- add support for timeframes in tables
- add basic analytics to understand usage
- add disabled UI for the lack of timeframes support in sqlite
- update Results vs. SQL UI focus based on a results response or query update respectively

### Changes

- Meltano will now discover components based on `https://meltano.com/discovery.yml`
- sample designs are now packaged with meltano

### Fixes

- Updated mobile menu to work as expected
- Updated tutorial docs with improved CLI commands and fixed the host setting to `localhost`

## 0.6.1 - (2019-01-15)

---

## 0.6.0 - (2019-01-15)

---

### New

- add new command `meltano add transform [name_of_dbt_transformation]`
- add transforms to the available plugins

### Changes

- Auto install missing plugins when `meltano elt` runs
- Terminology updates for simpler understanding

### Fixes

- Edit links on the bottom of doc pages are working now

### Breaks

- Updated docs tutorial bullet regarding inaccurate "Validate" button

## 0.5.0 - (2019-01-09)

---

### New

- ensure `meltano init <project-name>` runs on windows
- settings ui now provides sqlite-specific controls for sqlite dialect
- add `target-sqlite` to available loaders for meltano projects
- add new command `meltano add transformer [name_of_plugin]`
- add transformers (dbt) to the available plugins

### Changes

- extractors and loaders are arguments in the elt command instead of options
- `meltano www` is now `meltano ui`
- remove dbt installation from `meltano init`
- move everything dbt related under `transform/`
- update `meltano elt` to not run transforms by default
- update `meltano elt` to auto generate the job_id (job_id has been converted to an optional argument)

### Fixes

- left joins now work correctly in analyze.
- fixed broken sql toggles in analyze view
- fixed sql output based on sql toggles in analyze view

## 0.4.0 - (2019-01-03)

---

### New

- add Using Superset with Meltano documentation

## 0.3.3 - (2018-12-21)

---

## 0.3.2 - (2018-12-21)

---

## 0.3.1 - (2018-12-21)

---

### Changes

- add default models for 'tap-carbon-intensity'.
- Meltano Analyze is now part of the package.
- removes database dependency from Meltano Analyze and uses .ma files
- update the error message when using Meltano from outside a project - [!238](https://gitlab.com/meltano/meltano/merge_requests/238)

## 0.3.0 - (2018-12-18)

---

### New

- updated Settings view so each database connection can be independently disconnected
- add `meltano select` to manage what is extracted by a tap.

### Changes

- documentation site will utilize a new static site generation tool called VuePress

- meltano.com will be deployed from the meltano repo

### Fixes

- model dropdown now updates when updating database (no longer requires page refresh)
- prevent model duplication that previously occurred after subsequent "Update Database" clicks

## 0.2.2 - (2018-12-11)

---

### Changes

- documentation site will utilize a new static site generation tool called VuePress
- first iteration of joins (working on a small scale)

## 0.2.1 - (2018-12-06)

---

### Fixes

- resolve version conflict for `idna==2.7`
- fix the `discover` command in the docker images
- fix the `add` command in the docker images
- fix module not found for meltano.core.permissions.utils

## 0.2.0 - (2018-12-04)

---

### New

- add `meltano permissions grant` command for generating permission queries for Postgres and Snowflake - [!90](https://gitlab.com/meltano/meltano/merge_requests/90)
- add 'tap-stripe' to the discovery

### Changes

- demo with [carbon intensity](https://gitlab.com/meltano/tap-carbon-intensity), no API keys needed
- .ma file extension WIP as alternative to lkml

### Fixes

- fix order in Meltano Analyze

## 0.1.4 - (2018-11-27)

### Fixes

- add default values for the 'www' command - [!185](https://gitlab.com/meltano/meltano/merge_requests/185)
- add CHANGELOG.md
- fix a problem with autodiscovery on taps - [!180](https://gitlab.com/meltano/meltano/merge_requests/180)

### Changes

- move the 'api' extra package into the default package
- add 'tap-fastly' to the discovery

---

## 0.1.3

### Changes

- remove `setuptools>=40` dependency
- `meltano` CLI is now in the `meltano` package

## 0.1.2

### Fixes

- target output state is now saved asynchronously

## 0.1.1

### Changes

- initial release
