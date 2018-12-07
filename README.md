[![pipeline status](https://gitlab.com/meltano/meltano/badges/master/pipeline.svg)](https://gitlab.com/meltano/meltano/commits/master)

# Meltano

Meltano is an open source convention-over-configuration product for the whole data lifecycle, all the way from loading data to analyzing it.

It does [data ops](https://en.wikipedia.org/wiki/DataOps), data engineering, analytics, business intelligence, and data science. It leverages open source software and software development best practices including version control, CI, CD, and review apps.

Meltano stands for the [steps of the data science life-cycle](#data-science-lifecycle): Model, Extract, Load, Transform, Analyze, Notebook, and Orchestrate.

## How to Install and Run Meltano  

Check out our [guide](https://meltano.com/guide/#getting-started) to getting started with Meltano.

## Contributing

### Code style

Meltano uses [Black](https://github.com/ambv/black) to enforce a consistent code style. You may use `make lint` to automatically lint all your code, or `make show_lint` if you only want to see what needs to change.

You can also have black run automatically using a `git` hook. See https://github.com/ambv/black#version-control-integration for more details.

### Changelog

Meltano uses [changelog-cli](https://github.com/mc706/changelog-cli) to populate the CHANGELOG.md

#### Manual



#### Script

Use `changelog (new|change|fix|breaks) MESSAGE` to describe your current work in progress.

```bash
$ changelog new "add an amazing feature"
$ git add CHANGELOG.md
```

Make sure to add CHANGELOG entries to your merge requests.

### Merge Requests

Meltano uses an approval workflow for all merge requests.

  1. Create your merge request
  1. Assign the merge request to any Meltano maintainer for a review cycle
  1. Once the review is done the reviewer should approve the merge request
  1. Once approved, the merge request can be merged by any Meltano maintainer
  
## Release

Meltano uses [semver](https://semver.org/) as its version number scheme.
Meltano adheres to [Keep a Changelog](http://keepachangelog.com/) for changes tracking.

### Requirements

Meltano has a number of dependencies for the deployment toolchain that are required when performing a release. If you haven't already, please run the following command to install everything:

```bash
pip install '.[dev]'
```

### Release process

Meltano uses tags to create its artifacts. Pushing a new tag to the repository will publish it as docker images and a PyPI package.

```bash
$ git fetch origin
$ git checkout -b release-next origin/master
$ changelog view ;; make sure to validate the CHANGELOG changes
$ make release
$ git push --tags
$ git push origin release-next
```

Create a merge request from `release-next` targeting `master` and make sure to `delete the source branch when the changes are merged`.

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

This single host record is then enriched with data from three sources: DiscoverOrg, Clearbit, and WHOIS. If DiscoverOrg has no record of the domain we then fall back to Clearbit, with WHOIS being a last resort. Each request to DiscoverOrg and Clearbit is cached in the database and is updated no more than every 30 days. The cleaning and enrichment steps are all accomplished using Python.

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

New readonly and analytics users are then given instructions via Google Drive on how to connect their computer to the CloudSQL Proxy and on how to change their password once they log in.

By default, roles can log in to the main production instance of the data warehouse. Any password updates will propagate to `dev-bizops` and review instances when they are next refreshed.

Both readonly and analytics roles are not able to alter data in load only schemas. Currently, analytics, public, and sandbox are the only schemas which the `analytics` role can fully manipulate. Both roles have the ability to select from all schemas and tables. 

### Accessing peered VPCs

Some of the GitLab specific ELTs connect to databases which are in peered GCP projects, such as the usage ping. To allow connections, a few actions have been taken:
1. The Kubernetes cluster where the runner executes has been set up to use [IP aliasing](https://cloud.google.com/kubernetes-engine/docs/how-to/ip-aliases), so each pod gets a real routable IP within GCP.
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
- CTEs with confusing or notable logic should be commented.
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
- Field names should all be lowercase.
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

#### Docker Compose

1. Clone the repo
1. Customize the MELTANO directories as needed
1. From the main project directory, run `docker-compose up`
1. In your browser, navigate to `localhost:5000/drop_it_like_its_hot` to reset the schema of the database
1. Then navigate to `localhost:5000`. Click on add project, and specify `/meltano/model`

# Contributing to Meltano

We welcome contributions and improvements, please see the [contribution guidelines](https://meltano.com/docs/contributing.html)

# License

This code is distributed under the MIT license, see the [LICENSE](LICENSE) file.

[docker-compose]: https://docs.docker.com/compose/
