# GitLab Data and Analytics

This repository is for the storage of Looker view, model, and dashboard files. Use the issue tracker to request new data visualizations, suggest improvements to exisiting ones, report errors in underlying data, or request new data sources and features.

## Getting Started

The information below will get help you understand GitLab's data infrastructure and tools used to produce GitLab's internal data products and insights.

## Prerequisites

All GitLab employees have access to our Looker instance. We do not use Google Authentication so each person will need to request access. This can be done in bulk by making an issue in this project and including the following:

   * Email addresses to be added
   * Functional Group (Sales, Finance, Engineering, etc.) for each user
   * Whether Developer or View-Only Access is required
   * Assign the issue to @tayloramurphy
   * Add the Looker label
​

## Department Spaces, Dashboards & Looks

### Primary Corporate Dashboard https://gitlab.looker.com/dashboards/15

Functional Group|Dashboards|Looks|
-- | -- | -- |			
[Engineering](https://gitlab.looker.com/spaces/24)|[Dashboard 1]()|[Look 1]()|
[Finance ](https://gitlab.looker.com/spaces/16)|[Dashboard 1]()|[Look 1]()|
[Investor ](https://gitlab.looker.com/spaces/20)|[Dashboard 1]()|[Look 1]()|
[Marketing ]|[Dashboard 1]()|[Look 1]()|
[PeopleOps ]|[Dashboard 1]()|[Look 1]()|
[Product ](https://gitlab.looker.com/spaces/18)|[Dashboard 1]()|[Look 1]()|
[Sales ](https://gitlab.looker.com/spaces/28)|<ul><li>[Sales Forecast](https://gitlab.looker.com/dashboards/25)</li><li>[Sales Metrics](https://gitlab.looker.com/dashboards/28)</li><li>[Sales Rep & Manager 1:1](https://gitlab.looker.com/dashboards/29)</li></ul>|
[Support |[Dashboard 1]()|[Look 1]()|

### GitLab Looker Help
- Slack - #analytics


## Core Data and Analytics Toolset

### Looker

[Looker](https://docs.looker.com) is a business intelligence software and big data analytics platform that helps users explore, analyze and share real-time business analytics easily.

### Adding Users
* All GitLab Employees should be a part of their respective team group as well as the `GitLab Employee` group.

#### Training Sessions
* [Looker Codev Training 1](https://drive.google.com/file/d/1sKHbARpIfHKGpTChuqZSagnfh8Vt7_ml/view?usp=sharing)
* [Looker Codev Training 2](https://drive.google.com/file/d/1wNM-xnkDOBXce-M0cX16pkiFjsf3woma/view?usp=sharing)
* [Looker Codev Training 3](https://drive.google.com/file/d/1bKBtrCGxVRwXpYuYMXoD4XAqM1lzgdqL/view?usp=sharing)
* [Looker Codev Training 4](https://drive.google.com/file/d/1xZbXVG85tA388r57QpRPR4-eLi54ixhL/view?usp=sharing)
* [Looker Codev Training 5](https://drive.google.com/file/d/1RS3ALTjxh8VaNwt-q94Wbv_OYibsPzeR/view?usp=sharing)
* [Looker Business User Training](https://drive.google.com/file/d/19RzwdtRDNWvDL7W81_CfjX6sWDo_nP2w/view?usp=sharing)

#### Core Looker Definitions & Structure

**LookML** - is a Looker proprietary language for describing dimensions, aggregates, calculations and data relationships in a SQL database. The Looker app uses a model written in LookML to construct SQL queries against a particular database.

**LookML Project** - A LookML project is a collection of LookML files that describe a set of related models, explores, views, and LookML dashboards.

By convention, LookML code is segregated into three types of files: model files, view files, and dashboard files. In new LookML, these files have the following extensions: .model.lkml, .view.lkml, and .dashboard.lookml, respectively.

**Model** - A model is a customized portal into the database, designed to provide intuitive data exploration for specific business users. Multiple models can exist for the same database connection in a single LookML project. Each model can expose different data to different users. For example, sales agents need different data than company executives, and so you would probably develop two models to offer views of the database appropriate for each user. A model, in turn, is essentially metadata about the source database.

**View** - A view declaration defines a list of fields (dimensions or measures) and their linkage to an underlying table or derived table. In LookML a view typically references an underlying database table, but it can also represent a derived table.

A view may join to other views. The relationship between views is typically defined as part of a explore declaration in a model file.

**Explore** - An explore is a view that users can query. You can think of the explore as a starting point for a query, or in SQL terms, as the FROM in a SQL statement. An explore declaration specifies the join relationships to other views.

**Derived Table** - A derived table is a table comprised of values from other tables, which is accessed as though it were a physical table with its own set of columns. A derived table is exposed as its own view using the derived_table parameter, and defines dimensions and measures in the same manner as conventional views. Users can think of a derived table similar to a **view**, not to be confused with a Looker view, in a database.

**Dimension Group** - The dimension_group parameter is used to create a set of time-based dimensions all at once. For example, you could easily create a date, week, and month dimension based on a single timestamp column.

### Google Cloud SQL

[Cloud SQL](https://cloud.google.com/sql/docs/postgres/) - is a fully-managed database service that makes it easy to set up, maintain, manage, and administer GitLab's PostgreSQL relational databases on Google Cloud Platform.

### JupyterHub

[JupyterHub](https://jupyterhub.readthedocs.io/en/latest/) - a multi-user Hub that spawns, manages, and proxies multiple instances of the single-user Jupyter notebook server. The Jupyter Notebook is an open-source web application that allows you to create and share documents that contain live code, equations, visualizations and explanatory text.

## Guidelines

For effective development and consistency, general guidelines have been added below for reference.

### General Guidelines

- Percentages should appear as integer values
  - ```ex: 30% ```

### Dashboards
- Chart Titles should exist to explain the chart
- Fields should be define based on the business, not how it is labeled in a database table
  - ```ex: TCV or Total Contract Value, not tcv_value```

## Best Practices

### dbt

- Watch [this video (GitLab internal)](https://drive.google.com/open?id=1ZuieqqejDd2HkvhEZeOPd6f2Vd5JWyUn) on how to use dbt
- Use dbt for as much modeling as possible - see this [blog post](https://blog.fishtownanalytics.com/how-do-you-decide-what-to-model-in-dbt-vs-lookml-dca4c79e2304) from Fishtown Analytics.

### Looker

- Make mulitple small explores intead of one big one
- Design each explore to answer a specific set of questions. Single-view explores are fine!
- 5 to 6 view joins should be the limit. Otherwise, the underlying data may need to be modeled more effectively
- Only include specific fields that answer the question needed for analysis. Do not include fields that won't be used
- Don't use full outer joins
- Don’t use many-to-many joins
- Default colors are `#4b4ba3, #7c7ccc, #e05842, #fca121, #2e87e0, #37b96d, #707070, #bababa, #494C5` based on the GitLab [style guide](https://design.gitlab.com/styles/colors).
- Max of 2 decimal places for numbers
- `$#,##0` is an appropriate format for most dollar values.
- Each dashboard should only be focused on one time frame and a date filter should apply to every visualization equally. 
- A visualization looking at historical data, for example by month, should not include the present month (because it's not a comparison of apples to apples). 
- Allow the consumer of a visualization to do some work but not so much that it would dissuade them from consuming the visualization. Reduce clutter/labels where their presence will be redundant (e.g. where the Y axis already has numbers, it may be redundant to also label it "Count of X").
- Definitions should be established and then applied to dashboard/looks/explores equally everywhere. Definitions should be done at the upper-most level, so that business-logic changes in the future do not need to be maintained in multiple places.
- Comparisons of bookings values should be against Plan (Company-approved plan), Target (Goal based on industry benchmarks), or Forecast (Approved forecast, if different from Plan.)


#### Spaces
There are two primary spaces from a user perspective: "Shared" and your personal space named after your user. Access these via the "Browse" dropdown. It is strongly recommended that you initially develop all looks and dashboards in your personal space first and then move or copy them to a relevant sub-space within the "Shared" space when they're ready.

The Shared space should be for looks and dashboards that you want for your team or for the whole company. Do not create dashboards or looks within the top-level Shared space - alwyays put them in a subspace of Shared. Think of "Shared" as the root folder and each sub-space as a folder within root. Each subspace can have as many sub-spaces as a team wants. Initially, there will be a subspace within shared for each functional group and we can iterate from there.

## Resources
- [Looker Documentation](https://docs.looker.com)
- [Fishtown Analytics Blog](https://blog.fishtownanalytics.com)
- [Data Science Roundup Newsletter](http://roundup.fishtownanalytics.com/)
- [Mode Analytics Blog](https://blog.modeanalytics.com/)
- [Looker Blog](https://looker.com/blog)
- [Periscope Data Blog](https://www.periscopedata.com/blog)
- [Yhat Blog](http://blog.yhat.com/)
- [Wes McKinney Blog](http://wesmckinney.com/archives.html)


# License

This code is distributed under the MIT license, see the [LICENSE](LICENSE.mdf) file.
