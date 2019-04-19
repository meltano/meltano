# Concepts

Below are common terms used within the Meltano ecosystem arranged alphabetically.

## Aggregate

An `Aggregate` relates to a calculable column, via `count`, `sum` or other (i.e., aggregate definitions). These are limited to predefined methods with no custom SQL as well since custom SQL will be handled through transforms with dbt.

## Collection

A `Collection` is a group of one or many `Designs` that determines how they will be mapped together.

A `Collection` can be identified by the naming schema: `collection-name.collection.m5o` and should be stored in the `/collections` directory.

## Column

A `Column` relates directly to a column in a table of a database. Some limitations of this are that it will be limited to column only and no custom SQL.

## Dashboard

A `Dashboard` is a group of many `Reports`.

A `Dashboard` is identified by the file naming schema: `set-name.dashboard.m5o` and should be stored in the `/dashboards` directory.

## Design

A `Design` maps multiple tables together via joins. It points to many tables by names and can also add filters. At a high level, it does the following:

1. Takes selected columns to generate SQL from the `.m5oc` file
1. Runs the SQL query
1. Outputs the desired graph

In addition, a `Design` is the file that you would use to do the actual analysis because it defines the relationship between the tables.

A `Design` can be identified by the file naming schema: `design-name.design.m5o` and should be stored in the `/collections` directory.

## M5O Files

There are two types of `.m5o` files:

1. `.m5o` are user defined files that model the data in your database
2. `.m5oc` are compiled files generated from multiple `m5o` files

The `.m5o` files are based on the JSON-like HOCON syntax and serve as input for the compiled `.m5oc` files that Meltano UI then leverages.

## Report

A `Report` is a saved state of selecting and analyzing a `Design`. It contains a subset of fields that you select from multiple tables and is ultimately the selected analysis. It can also be generated from raw SQL.

A `Report` can be identified by the file naming schema: `report-name.report.m5o` and should be stored in the `/reports` directory.

## Table

A `Table` relates to a table in a database. It defines a direct link to a table in the database. In addition, it also defines and contains `columns` and `aggregates` so you can select which you want to show.

A `Table` can be identified by the file naming schema: `table-name.table.m5o` and should be stored in the `/tables` directory.

## Taps

A `Tap` is an application that pulls data out of a data source by using the best integration for extracting bulk data.

For example, it takes data from sources like databases or web service APIs and converts them in a format that can be used for data integration or an ETL (Extract Transform Load) pipeline. 

Meltano's `taps` is part of the Extractor portion of the data workflow and are based on the [Singer specification](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md).

## Targets

A `Target` is an application that has the responsibility of consuming data from `taps` and perform a task with it. Examples include loading it into a file (i.e., CSV), API, or database. 

Meltano `targets` is part of the Loader portion of the data workflow.
