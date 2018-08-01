[![pipeline status](https://gitlab.com/meltano/meltano/badges/master/pipeline.svg)](https://gitlab.com/meltano/meltano/commits/master)

# Meltano

Meltano is an open source convention-over-configuration product for the data lifecycle, all the way from loading it to analizing it.
It does [data ops](https://en.wikipedia.org/wiki/DataOps), data engineering, analytics, business intelligence, and data science. It leverages open source software and software development best practices including version control, CI, CD, and review apps.

Meltano stands for the [steps of the data science life-cycle](#data-engineering-lifecycle): Model, Extract, Load, Transform, Analyze, Notebook, and Orchestrate.

## Data Science Lifecycle

| Stage     | Meltano selected | OSS considered but not selected | Proprietary alternatives |
| --------- | ------------ | -------------- | --------------------- |
| Model | [dbt](https://blog.fishtownanalytics.com/how-do-you-decide-what-to-model-in-dbt-vs-lookml-dca4c79e2304) | [Open ModelSphere](http://www.modelsphere.com/org/) | [LookML](https://looker.com/platform/data-modeling), [Matillion](http://www.stephenlevin.co/data-modeling-layer-startup-analytics-dbt-vs-matillion-vs-lookml/) |
| Extract   | [Meltano Extract](#meltano-extract) | [Pentaho DI](http://www.pentaho.com/product/data-integration), [Talend](https://www.talend.com/), [Singer Tap](https://www.singer.io/#taps) | [Alooma](https://www.alooma.com/) |
| Load      | [Meltano Load](#meltano-load) | [Pentaho DI](http://www.pentaho.com/product/data-integration), [Talend](https://www.talend.com/), [Singer Target](https://www.singer.io/#targets) | [Alooma](https://www.alooma.com/) |
| Transform | [dbt](https://www.getdbt.com/), [Python scripts](#python-scripts) | [Stored procedures](#stored-procedures), [Pentaho DI](http://www.pentaho.com/product/data-integration) | [Alooma](https://www.alooma.com/) |  
| Analyze | [Meltano Analysis](https://gitlab.com/meltano/meltano/tree/master/src/melt) | [D3.js](https://d3js.org/) | [Looker](https://looker.com/), [Periscope](https://www.periscopedata.com/) |
| Notebooks | [JupyterHub](https://github.com/jupyterhub/jupyterhub) | [Metabase](https://www.metabase.com/) | [Nurtch](https://www.nurtch.com/), [Datadog notebooks](https://www.datadoghq.com/blog/data-driven-notebooks/) |
| Orchestrate | [GitLab CI](https://about.gitlab.com/features/gitlab-ci-cd/) | [Luigi](https://github.com/spotify/luigi), [Airflow](https://airflow.apache.org/) | [Fivetran](https://fivetran.com/) |

## Principles

We believe that information is the foundation of good decisions, and that companies of all sizes deserve insights into their operations. So Meltano provides broad, democratized access to detailed operational metrics, thereby driving better decisions and shortening decision cycle time across the entire enterprise.

In addition, believe that the information a business uses to make decisions must come from all parts of that business. Meltano joins data from multiple systems used by Sales, Marketing, Product and others, thereby providing a comprehensive view of the relationship between business activities, associated costs, and customer long-term value.

## Media

- [Google Docs Meeting Agenda](https://docs.google.com/document/d/1nayKquFLL8DN3h8mnLo3pVZsEKyPcBgQm2mqc5GggPA)
- [Youtube Channel](https://www.youtube.com/channel/UCmp7zJAZEC7I_n9BEydH8XQ/videos)
- [Issue board](https://gitlab.com/meltano/meltano/boards/528368?=)
- [Functional Group Update (PDF format)](https://drive.google.com/open?id=1oNiCtHkorYKq19kx8CwGr8Z7QCjVQiOj)  
- [Functional Group Update (Keynote format)](https://drive.google.com/open?id=1WmleHjP41nsxszGV50ionZKx-b2X3PvF)

## Approach

### Meltano is the market (data science) lifecycle, just like GitLab is the product (DevOps) lifecycle.

For many companies GitLab serves as the single data store for their engineering organization, shepherding their ideas all the way through to delivering them to customers. There are key gaps however in understanding the effectiveness of sales and marketing. By expanding the common data store to include go to market information, additional insights can be drawn across the customer lifecycle. This evolution is as follows:

1. Business intelligence, this is the current state of the project.
2. Data science, add more machine learning (ML) and Artificial Intelligence (AI)
3. Market lifecycle, the complete go-to-market lifecycle with the user/customer jouney.

### Meltano is business intelligence (BI) as code.
Meltano uses GitLab CI/CD to setup and maintain its stack, so software and scripts required are checked into SCM with the attendant benefits: full version control, history, easy collaboration and reviews. Automated management of the BI environment means it is easy to make alterations, re-deploy in the event of an issue or outage, as well as provision new environments for different uses like a staging server.

### Evolution from an internal project, to a community, to open core

1. We are building Meltano to solve a problem that GitLab share with all other software companies - how to acquire the highest-value customers at the lowest cost of acquisition?  We are solving this problem for ourselves first, incorporating what we learn along the way into a product that delivers practical and quantifiable value to our customers.
2. Next we'll focus on building a community around Meltano with more users and regular contributors to the code base.
3. Right now Meltano is completely open source. After we have a community we'll introduce propietary features to have a sustainable business model to do quality control, marketing, security, dependency upgrades, and performance improvements. We'll always be good [stewards similar to GitLab](https://about.gitlab.com/stewardship/).

## Roadmap

1. [MVC](https://gitlab.com/meltano/meltano/issues/10)
  * [Horizontal slice of ELT sources](https://gitlab.com/meltano/meltano/issues?scope=all&utf8=✓&state=opened&label_name[]=elt): Salesforce, Marketo, NetSuite, Zuora, etc.
  * [Data Pipeline](https://gitlab.com/meltano/meltano/issues?label_name[]=pipeline): container, CI pipeline, review apps
2. Data Model and Visualization
  * [Common Data Model](https://gitlab.com/meltano/meltano/issues?label_name[]=data-model): Conventions for common table and field names (but it allows you to make it organization specific)
  * [Field Mapping](https://gitlab.com/meltano/meltano/issues/121): Mapping of user fields to common data model, if required
  * [Visualization Sample](https://gitlab.com/meltano/meltano/issues/122): Documentation and samples for connecting a visualization engine
  * [JupyterHub deployment](https://gitlab.com/meltano/jupyter-hub): Easily deploy JupyterHub for data exploration
3. [Ease of use & Automation](https://gitlab.com/meltano/meltano/issues?label_name%5B%5D=ease-of-use)
  * Seamless handle some schema changes, like a field rename
  * Match user fields to common data model, without intervention

## Data security and privacy

When using Meltano, like any data science tool, it is important to consider the security and privacy implications.

* Meltano expects the required credentials for each extractor to be stored as a project variable. Project members with the role [`Maintainer` or `Owner`](https://docs.gitlab.com/ee/user/permissions.html#project-members-permissions) will be able to see these in plaintext, as well as any instance wide administrators. If you are using GitLab.com, this includes select GitLab employees responsible for the service.
  * Support for KMS systems is being considered for a future release.
* Because these variables are passed to GitLab CI jobs, it is possible to accidentally or maliciously compromise them. 
  * For example a developer who normally cannot see the variables in project settings, could accidentally print the environment variables when debugging a CI job, causing them to be readable by a wider audience than intended.
  * Similarly it is possible for a malicious developer to utilize the variables to extract data from a source, then send it to an unauthorized destination.
  * These risks can be mitigated by [restricting the production variables](https://docs.gitlab.com/ee/ci/variables/#protected-variables) to only protected branches, so code is reviewed before it is able run with access to the credentials. It is also possible to set job logs to be available to only those with `Developer` roles or above, in CI/CD settings.
* When designing your data warehouse, consider any relevant laws and regulations, like GDPR. For example, historical data being retained as part of a snapshot could present challenges in the event a user requests to be forgotten.

### Competition & Value

This should be a replacement for other ELT & Data Integration tools: [Boomi](https://boomi.com/), [Informatica Cloud](https://www.informatica.com/products/cloud-integration/cloud-data-integration.html), and [Alooma](https://www.alooma.com/).

## At GitLab

Meltano is a separate product made by a separate team. The goal is at some point to spin it out of GitLab as a new company.

For now we use [PostgreSQL](https://www.postgresql.org/) as the warehouse but we're open to support others such as [MariaDB AX](https://mariadb.com/products/solutions/olap-database-ax), [Redshift](https://aws.amazon.com/redshift/), [MemSQL](https://www.memsql.com/), and [Snowflake](https://www.snowflake.net/).

We use dbt for testing too, instead of [Great Expectations](https://github.com/great-expectations/great_expectations), [Hypothesis](https://hypothesis.readthedocs.io/en/latest/), or closed source options such as [Informatica](https://marketplace.informatica.com/solutions/informatica_data_validation), [iCEDQ](https://icedq.com/), and [QuerySurge](http://www.querysurge.com/).

At GitLab we're using Looker instead of Superset, for sure for the rest of 2018.
If we switch we'll want to make sure that most of the functionality can be replicated in Superset, and the switch will be gradual.
For now try to keep as much functionality as possible in DBT instead of Looker.

### Meltano data security and privacy at GitLab

We take user security and privacy seriously at GitLab. We internally use Meltano to learn about how users interact with GitLab.com, build a better product, and efficiently run our organization. We adhere to the following guidelines:

1. GitLab employees have access to the data warehouse and can see pseudonymized data. In some cases due to public projects, it is possible to tie a pseudonymized account to a public account. It is not possible to learn the private projects a user is working on or contents of their communications.
1. We will never release the pseudonymized data set publicly, in the event it is possible to reverse engineer unintended content.
1. Select GitLab employees have administrative access to GitLab.com, and the credentials used for our extractors. As [noted above](#data-security-and-privacy), developers on the Meltano project could maliciously emit credentials into a job log, however the logs are not publicly available.

## Metrics

We are targeting analytics for sales and marketing performance first. We plan to track the following metrics, in order of priority. These results will be able to reviewed over various time periods. Initially we will support single touch attribution, with support for multitouch in a [later sprint](doc/development_plan.md#backlog).

1. SAOs by source
  1. Aggregated (SDR / BDR / AE generated / Other)
  1. Campaign level (AWS Reinvent / etc.)
1. SAOs by source by week and/or month
2. Aquisition cost per SAO
  * Cost per lead = dollar spend / number of attributed leads
3. Estimated IACV and LTV per SAO based on history (can do IACV if LTV is hard to calculate)
  * Estimated IACV = 2 *  IACV at median conversion time
  * LTV = IACV * margin * average retention time
4. Estimated IACV / marketing ratio.
  * CAC = cost per lead * conversion from lead to IACV
  * ROI = LTV / CAC

In the future, we plan to expand support to other areas of an organization like Customer Success, Human Resources, and Finance.

## Data sources

To achieve this, we bring data from all [data sources](data_sources.md) to a [common data model](doc/data_model.md) (that can and likely will be different for every organization) so it can be used easily and consistently across tools and teams. For example something as simple as unique customer ID, product or feature names/codes.

### Personally Identifiable Information

It is important to be cognizant of the personally identifiable information which is extracted into the data warehouse. Warehouses are at their best when they are leveraged across many parts of the organization, and therefore it is hard to predict which users will ultimately have access and how each user will treat the data.

We recommend the following best practices:
1. Avoid extracting any personally identifable information in the first place. For example, consider extracting only company names from your CRM and avoid extracting individual contact details.
1. If it is important to collect data about individual users, for example to learn more about user behavior, pseudonymize the data prior to writing it into the data warehouse.
1. Consider how you are persisting any PII data, and it's impact on compliance requirements like GDPR.

## Tools

We want the tools to be open source so we can ship this as a product.

1. Extract and Load (EL): Python scripts, [Singer taps](https://www.singer.io/).
1. Transformation: [dbt](https://docs.getdbt.com/) to handle transforming the raw data into a normalized data model within PG.
1. Warehouse: Any SQL based data warehouse. We recommend [PostgeSQL](https://www.postgresql.org/) and include it in the Meltano pipeline. Postgres cloud services like [Google Cloud SQL](https://cloud.google.com/sql/) are also supported, for increased scalability and durability.
1. Orchestration/Monitoring: [GitLab CI](https://about.gitlab.com/features/gitlab-ci-cd/) for scheduling, running, and monitoring the ELT jobs. In the future, [DAG](https://gitlab.com/gitlab-org/gitlab-ce/issues/41947) support will be added. Non-GitLab alternatives are [Airflow](https://airflow.incubator.apache.org) or [Luigi](https://github.com/spotify/luigi). GitLab CI can handle 1000's of distributed runners to run for example Python scripts.
1. Visualization/Dashboard: Meltano is compatible with nearly all visualization engines, due to the SQL based data store. For example commercial products like [Looker](https://looker.com/) or [Tableau](https://www.tableau.com/), as well as open-source products like [Superset](https://github.com/airbnb/superset) or [Metabase](https://metabase.com) can be used.

## How to use
> Notes:
> * Most implementations of SFDC, and to a lesser degree Zuora, require custom fields. You will likely need to edit the transformations to map to your custom fields.
> * The sample Zuora python scripts have been written to support GitLab's Zuora implementation. This includes a workaround to handle some subscriptions that should have been created as a single subscription.

The Meltano product consists of three key components:

1. A SQL based data store, for example [PostgreSQL](https://www.postgresql.org/) or [Cloud SQL](https://cloud.google.com/sql/). We recommend using Postgres for [review apps](https://about.gitlab.com/features/review-apps/) and a more durable and scalable service for production.
1. This project, [`meltano`](https://gitlab.com/meltano/meltano), which contains the ELT scripts and CI jobs to refresh the data warehouse from the [configured sources](doc/data_sources.md). Typically configured to run on a [scheduled CI job](https://docs.gitlab.com/ce/user/project/pipelines/schedules.html) to refresh the data warehouse from the configured sources.
1. The [`meltano-elt`](https://gitlab.com/meltano/meltano-elt) container, which includes the necessary dependencies for the ELT scripts. Used as the base image for the CI jobs.

As development progresses, additional documentation on getting started along with example configuration and CI scripts will become available.

It is expected that the Meltano project will have many applications managed in the top level of the project. Some or parts of these applications could be useful to many organizations, and some may only be useful within GitLab. We have no plans on weighing the popularity of an individual application at the top level of the Meltano project for inclusion/exclusion. 

### Meltano Extract

_Meltano Extract is under development, consider it a moving target: API breakage are frequent and spontaneous._

To satisfy our data integration needs, we started working on custom EL scripts, creating the Meltano fuse `meltano-extract-common` python module. 

Features include:

  - Automatic schema creation
  - Automatic schema mutation
  - Fields whitelisting
  - Fields pseudonymization
  - Job logging (recovery)
  - CLI configuration
  - REST data source
  - SOAP data source
  - SQL data source
  
Currently we are using these tools to extract data from the following data sources:
  
  - Zendesk
  - Zuora
  - NetSuite
  - Marketo
  - Lever
  - Google Sheets/CSV
  
#### Architecture

The `meltano-extract-common` is currently only a set of tools to help build EL scripts. It enforces very little structure on how the process should be handled.

EL scripts should describe the `Schema` or the data source they try to integrate data from. This schema can then be applied to the data warehouse, if possible.

EL scripts are responsible for extracting data that complies for the specified configuration options (incremental, full) and save them to an intermediary format (currently CSV).

Then, using PostgreSQL `COPY FROM ...`, EL scripts should insert/upsert into the backend (warehouse).

Job logging can also be provided to make the run persistent and recoverable.

### Meltano Load

Right now Meltano Load is part of the code of [Meltano Extract](#meltano-extract).
We're planning on splitting it into a separate piece of code.

### Python scripts

Some transformations can't be done with DBT like API calls.

### Stored procedures

We don't use stored procedures because they are hard to keep under version control.

### Local environment

#### On the host machine

The local environment might differ for different ELT processes.
The most standard setup uses Python 3.5.

Customize the `.env.example` file according to your needs.

```
$ cp .env.example .env
```

Then, create the virtualenv using `pipenv`:
```
$ pipenv install --skip-lock
$ pipenv shell
```

This installs the python dependencies that the ELT process needs.

#### Using the docker stack

A docker-compose configuration is also provided to start:

  - a PostgreSQL instance (bizops-dw) for the data warehousing needs
  - a Python3 container with the 
  
These containers will use environment variables defined in the Meltano project.
To run:

```
$ docker-compose up -d
$ docker-compose exec elt pipenv shell
Loading .env environment variables…
Spawning environment shell (/bin/bash). Use 'exit' to leave.
source /root/.local/share/virtualenvs/bizops-YMzVKlMq/bin/activate
(bizops-YMzVKlMq) root@b9951069d9cf:/bizops#
```

You should be ready to go!

### Managing API requests and limits

Many of the SaaS sources have various types of API limits, typically a given quota per day. If you are nearing the limit of a given source, or are iterating frequently on your repo, you may need to implement some additional measures to manage usage.

### How to Use Sub pipelines to Effectively Create a DAG like Architecture

An example of this can be seen in the [gitlab-ci.yml](https://gitlab.com/gitlab-org/gitlab-ce/blob/master/.gitlab-ci.yml#L251) which is being used to trigger the gitlab-qa project. This will trigger a [`SCRIPT_NAME`:`trigger-build`](https://gitlab.com/gitlab-org/gitlab-ce/blob/master/scripts/trigger-build) which has the API calls written in Ruby, for which we can use Python. From there the sky is the limit.

#### Reducing API usage by review apps

One of the easiest ways to reduce consumption of API calls for problematic ELT sources is to make that job manual for branches other than `master`. This way when iterating on a particular branch, this job can be manually run only if it specifically needs to be tested.

We don't want the job on `master` to be manual, so we will need to create two jobs. The best way to do this is to convert the existing job into a template, which can then be referenced so we don't duplicate most of the settings.

For example take a sample Zuora ELT job:

```yaml
zuora:
  stage: extract
  image: registry.gitlab.com/meltano/meltano-elt/extract:latest
  script:
    - set_sql_instance_name
    - setup_cloudsqlproxy
    - envsubst < "elt/config/environment.conf.template" > "elt/config/environment.conf"
    - python3 elt/zuora/zuora_export.py
    - stop_cloudsqlproxy
```

The first thing to do would to convert this into an anchor, and preface the job name with `.` so it is ignored:

```yaml
.zuora: &zuora
  stage: extract
  image: registry.gitlab.com/meltano/meltano-elt/extract:latest
  script:
    - set_sql_instance_name
    - setup_cloudsqlproxy
    - envsubst < "elt/config/environment.conf.template" > "elt/config/environment.conf"
    - python3 elt/zuora/zuora_export.py
    - stop_cloudsqlproxy
```

Next, we can define two new jobs. One for `master` and another manual job for any review branches:

```yaml
zuora_prod:
  <<: *zuora
  only:
    - master

zuora_review:
  <<: *zuora
  only:
    - branches
  except:
    - master
  when: manual
```

## Pipeline configuration

Data integration stages are configurable using `Project variables` for the CI/CD pipeline. The following variables may help you control what needs to run:

  - `EXTRACT_SKIP`: either `all` (to skip the `extract` stage) or job names, like `marketo,zendesk,zuora` to be skipped from the pipeline.
  - `UPDATE_SKIP`: either `all` (to skip the `update` stage) or job names, like `sfdc_update`.

## Spreadsheet Loader Utility

Spreadsheets can be loaded into the DW (Data Warehouse) using `elt/util/spreadsheet_loader.py`. Local CSV files can be loaded as well as spreadsheets in Google Sheets.
A file will only be loaded if there has been a change between the current and existing data in the DW.

Loading a CSV:

  - Start the cloud sql proxy
  - The naming format for the file must be `<schema>.<table>.csv`. This pattern is required and will be used to create/update the table in the DW.
  - Run the command `python3 elt/util/spreadsheet_loader.py csv <path>/<to>/<csv>/<file_name>.csv` Multiple paths can be used, use spaces to separate.
  - Logging from the script will tell you table successes/failures and the number of rows uploaded to each table.


Loading a Google Sheet:

  - Share the sheet with the required service account (if being used in automated CI, use the runner service account)
  - The file will be located and loaded based on its name. The names of the sheets shared with the runner must be unique and in the `<schema>.<table>` format
  - Run the command `python3 elt/util/spreadsheet_loader.py sheet <file_name>` Multiple names can be used, use spaces to separate.
  - Logging from the script will tell you table successes/failures and the number of rows uploaded to each table.

Further Usage Help:

  - Run the following command(s) for additional usage info `python3 elt/util/spreadsheet_loader.py <csv|sheet> -- --help`

## GitLab Data and Analytics - Internal

### Charter/Goals
* Build a centralized data warehouse that can support data analysis requirements from all functional groups within the company.
* Create a common data framework and governance practice.
* Establish the single source of truth for company metrics.
* Establish a change management processes for source systems.
* Develop a Data Architecture plan (in conjunction with functional teams).
* Develop a roadmap for systems evolution in alignment with the Company’s data architecture plan.

### GitLab Internal Analytics Architecture

![GitLab Internal Analytics Architecture](img/WIP_ GitLab_Analytics_Architecture.jpg)

#### Data Warehouse

* Using Cloud SQL.
* Consolidated repository of all source data - scrubbed and modeled into a format optimized for analytic workloads (Dimensional model).
* Serves as the Single Source of Truth for reporting, analysis, and visualization applications.
* Will need to be audited regularly back to the source.
* Should not be generally available - will require strict access controls for direct querying not done through a controlled application such as metabase.

#### Accessing the Data Warehouse
If you want direct access to the data warehouse (outside of Looker or JupyterHub), follow these steps.

* Request an account (username and password) from Taylor Murphy or Joshua Lambert through Slack.
* Verify your Google account is associated with the `gitlab-analysis` project, it should have the `Cloud SQL Client` role.
* Set up your local machine by installing the [gcloud SDK](https://cloud.google.com/sdk/docs/).
* Run `gcloud config set project gitlab-analysis`
* Run `gcloud auth application-default login`
* Connect to cloudsqlproxy `./cloud_sql_proxy -instances=gitlab-analysis:us-west1:dev-bizops=tcp:5432`
* Connect to the Data Warehouse through the terminal (a separate tab) with `psql "host=127.0.0.1 sslmode=disable dbname=dw_production user=<username>`
* Alternatively, use your favorite database tool with `host=127.0.0.1` and `dbname=dw_production`

#### Hosts Records Dataflow

From our on-premises installations, we recieve [version and ping information](https://docs.gitlab.com/ee/user/admin_area/settings/usage_statistics.html) from the software. This data is currently imported once a day from a PostgreSQL database into our enterprise data warehouse (EDW). We use this data to feed into Salesforce (SFDC) to aid our sales representatives in their work.

The domains from all of the pings are first cleaned by standardizing the URL using a package called [tldextract](https://github.com/john-kurkowski/tldextract). Each cleaned ping type is combined into a single host record. We make a best effort attempt to align the pings from the same install of the software. 

This single host record is then enriched with data from three sources: DiscoverOrg, Clearbit, and WHOIS. If DiscoverOrg has no record of the domain we then fallback to Clearbit, with WHOIS being a last resort. Each request to DiscoverOrg and Clearbit is cached in the database and is updated no more than every 30 days. The cleaning and enrichment steps are all accomplished using Python.

We then take all of the cleaned records and use dbt to make multiple transformations. The last 60 days of pings are aligned with Salesforce accounts using the account name or the account website. Based on this, tables are generated of host records to upload to SFDC. If no accounts are found, we then generate a table of accounts to create within SFDC. 

Finally, we use Python to generate SFDC accounts and to upload the host records to the appropriate SFDC account. We also generate any accounts necessary and update any SFDC accounts with DiscoverOrg, Clearbit, and WHOIS data if any of the relevant fields are not already present in SFDC.

#### Updating SFDC Extract
[Taylor explains Pentaho Data Integration](https://drive.google.com/open?id=1OD7QQ2aD-4LWL-ExM8WAyyeuBm2bTRa6) GitLab internal because of credentials being viewable.

As of 2018-05-24:

If removing a field from the extract, delete the fields from the `.ktr` file, similar to what was done in [this commit](https://gitlab.com/meltano/meltano/commit/0a76c160816d2505105eb4c2642b6b82ca9b1350).

If adding a field, take the following steps:

* Add to the appropriate `.ktr` file for the given object, similar to what was done [here](https://gitlab.com/meltano/meltano/commit/6b89bb592ee2389f91ebcb86102028ab87bb77d9)
* Add the column to the appropriate table in the database (requires access to `gitlab` user)
* Update all of the objects from SFDC because the database will have `null` for every row
  * Use Pentaho Data Integration locally to run the job based on query condition of `Your_added_field__c != null`
* Check for any snapshots of that table, if they exist, add the column to the tables as well.

#### Managing Roles

All role definitions are in [/elt/config/pg_roles/](https://gitlab.com/meltano/meltano/tree/master/elt/config)

Ideally we'd be using [pgbedrock](https://github.com/Squarespace/pgbedrock) to manage users. Since internally we are using CloudSQL, we're not able to access the superuser role which pgbedrock requires. However, the YAML format of the role definitions is convenient for reasoning about privileges and it's possible the tool could evolve to validate privileges against a given spec, so we are using the pgbedrock definition syntax to define roles here. 

The `readonly` role was generated using the following commands:

```sql
CREATE ROLE readonly;

GRANT USAGE on SCHEMA analytics, customers, gitlab, historical, lever, license, mkto, public, sandbox, sfdc, sfdc_derived, version, zuora to readonly;

GRANT SELECT on ALL TABLES IN SCHEMA analytics, customers, gitlab, historical, lever, license, mkto, public, sandbox, sfdc, sfdc_derived, version, zuora to readonly;

-- Ensures all future tables are available to the role
ALTER DEFAULT PRIVILEGES IN SCHEMA analytics, customers, gitlab, historical, lever, license, mkto, public, sandbox, sfdc, sfdc_derived, version, zuora 
  GRANT SELECT ON TABLES TO readonly;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA sandbox TO readonly;

```

The `analytics` role was generated using the following commands:

```sql

CREATE ROLE analytics;

GRANT USAGE on SCHEMA analytics, customers, gitlab, historical, lever, license, mkto, public, sandbox, sfdc, sfdc_derived, version, zuora to analytics;

GRANT SELECT on ALL TABLES IN SCHEMA analytics, customers, gitlab, historical, lever, license, mkto, public, sandbox, sfdc, sfdc_derived, version, zuora to analytics;

-- Ensures all future tables are available to the role
ALTER DEFAULT PRIVILEGES IN SCHEMA analytics, customers, gitlab, historical, lever, license, mkto, public, sandbox, sfdc, sfdc_derived, version, zuora 
  GRANT SELECT ON TABLES TO analytics;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA analytics, public, sandbox TO analytics;

``` 

New user roles are added to a specific role via:

```sql
CREATE ROLE newrole WITH PASSWORD 'tmppassword' IN ROLE metarole;

ALTER ROLE newrole WITH LOGIN;
```

New readonly and analytics users are then given instructions via Google Drive on how to connect their computer to the CloudSQL Proxy and on how to change their password once they login.

By default, roles can login to the main production instance of the data warehouse. Any password updates will propagate to `dev-bizops` and review instances when they are next refreshed.

Both readonly and analytics roles are not able to alter data in load only schemas. Currently, analytics, public, and sandbox are the only schemas which the `analytics` role can fully manipulate. Both roles have the ability to select from all schemas and tables. 

### Accessing peered VPCs

Some of the GitLab specific ELTs connect to databases which are in peered GCP projects, such as the usage ping. To allow connections, a few actions have been taken:
1. The Kubernetes cluster where the runner executes has been setup to use [IP aliasing](https://cloud.google.com/kubernetes-engine/docs/how-to/ip-aliases), so each pod gets a real routable IP within GCP.
1. A [VPC peering relationship](https://cloud.google.com/vpc/docs/vpc-peering) has been established between the two projects and their networks.
1. A firewall rule has been created in the upstream project to allow access from the runner Kubernetes cluster's pod subnet.

### dbt Coding Conventions

At Gitlab we use dbt for data transformation, as referenced in "Tools" above. What follows are the conventions we use internally. *Inspired by [Fishtown Analytics](https://github.com/fishtown-analytics/corp/blob/master/dbt_coding_conventions.md)*


#### Policy & Procedure

- Reviewers should have 48 hours to complete a review, so plan ahead with the end of your sprint.
- When possible, questions/problems should be discussed with your reviewer before MR time. MR time is by definition the worst possible time to have to make meaningful changes to your models, because you’ve already done all of the work!

#### Model Configuration

- Model-specific attributes (like sort/dist keys) should be specified in the model.
- If a particular configuration applies to all models in a directory, it should be specified in the project.
- In-model configurations should be specified like this:

```python
{{
  config(
    materialized = ’table’,
    sort = ’id’,
    dist = ’id’
  )
}}
```

#### Base Models

- Only base models should select from source tables / views.
- Only a single base model should be able to select from a given source table / view.
- Base models should be placed in a `base/` directory.
- Base models should perform all necessary data type casting.
- Base models should perform all field naming to force field names to conform to standard field naming conventions.
- Source fields that use reserved words must be renamed in base models.

#### Field Naming Conventions

- TBD

#### CTEs (Common Table Expressions)

- All `{{ ref('...') }}` statements should be placed in CTEs at the top of the file.
- Where performance permits, CTEs should perform a single, logical unit of work.
- CTE names should be as verbose as needed to convey what they do.
- CTEs with confusing or noteable logic should be commented.
- CTEs that are duplicated across models should be pulled out into their own models.
- CTEs should be formatted like this:

``` sql
WITH events AS (

  ...

),

-- CTE comments go here
filtered_events AS (

  ...

)

SELECT * 
FROM filtered_events
```

#### Style Guide

- Indents should be four spaces (except for predicates, which should line up with the `where` keyword).
- Lines of SQL should be no longer than 80 characters.
- Field names should all be lowercased.
- Function names should all be capitalized.
- The `as` keyword should be used when projecting a field or table name.
- Fields should be stated before aggregates / window functions.
- Ordering and grouping by a number (eg. group by 1, 2) is ok.
- When possible, take advantage of `using` in joins.
- Prefer `union all` to `union` [*](http://docs.aws.amazon.com/redshift/latest/dg/c_example_unionall_query.html).
- *DO NOT OPTIMIZE FOR A SMALLER NUMBER OF LINES OF CODE. NEWLINES ARE CHEAP, BRAIN TIME IS EXPENSIVE*

##### Example Code
```sql
with my_data as (

    SELECT * 
    FROM {{ ref('my_data') }}

),

some_cte as (

    SELECT * 
    FROM {{ ref('some_cte') }}

)

SELECT [distinct]
    field_1,
    field_2,
    field_3,
    CASE
        WHEN cancellation_date is null and expiration_date is not null then expiration_date
        WHEN cancellation_date is null then start_date+7
        ELSE cancellation_date
    END AS canellation_date

    SUM(field_4),
    MAX(field_5)

FROM my_data
JOIN some_cte USING (id)

WHERE field_1 = ‘abc’
  AND (
    field_2 = ‘def’ OR
    field_2 = ‘ghi’
  )

GROUP BY 1, 2, 3
HAVING count(*) > 1
```

#### Testing

- Every model should be tested in a `schema.yml` file
- At minimum, unique, not nullable fields, and foreign key constraints should be tested (if applicable)
- The output of dbt test should be pasted into MRs
- Any failing tests should be fixed or explained prior to requesting a review

# Contributing to Meltano

We welcome contributions and improvements, please see the [contribution guidelines](CONTRIBUTING.md)

# License

This code is distributed under the MIT license, see the [LICENSE](LICENSE) file.
