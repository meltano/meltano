# Fundamentals

Below are common terms used within the Meltano ecosystem. Many of these terms have associated `.m5o` (Meltano model) files, so we'll cover those first.

## Aggregate

An `Aggregate` relates to a calculable column, via `count`, `sum` or other (i.e., aggregate definitions). These are limited to predefined methods with no custom SQL as well since custom SQL will be handled through transforms with dbt.

## Collection

A `Collection` is a group of one or many `Designs` that determines how they will be mapped together.

A `Collection` can be identified by the naming schema: `collection-name.collection.m5o` and should be stored in the `/collections` directory.

### Column

A `Column` relates directly to a column in a table of a database. This relieves us for a SQL field since we will have `column definitions`. Some limitations of this are that it will be limited to column only and no custom SQL.

## Dashboard

A `Dashboard` is a group of many `Reports`.

A `Dashboard` is identified by the file naming schema: `set-name.dashboard.m5o` and is stored in the `/dashboards` directory.

## Design

A `Design` maps multiple tables together via joins. It points to many tables by names and can also add filters. At a high level, it does the following:

1. Takes selected columns to generate SQL from the `.m5oc` file
1. Runs the SQL query
1. Outputs the desired graph

In addition, a `Design` is the file that you would use to do the actual analysis because it defines the relationship between the tables.

A `Design` can be identified by the file naming schema: `design-name.design.m5o` and should be stored in the `/collections` directory.

## M5O Files

There are two types of `.m5o` files:

1. `.m5o` are uncompiled files that users define based on a schema
2. `.m5oc` are compiled files generated from multiple `m5o` files

The `.m5o` files are based on the JSON-like HOCON syntax and serve as input for the compiled `.m5oc` files that Meltano Analyze then leverages.

## Table

A `Table` relates to a table in a database. It defines a direct link to a table in the database. In addition, it also defines and contains `columns` and `aggregates` so you can select which you want to show.

A `Table` can be identified by the file naming schema: `table-name.table.m5o` and should be stored in the `/tables` directory.

## Report

A `Report` is a saved state of selecting and analyzing a `Design`. It contains a subset of fields that you select from multiple tables and is ultimately the selected analysis. It can also be generated from raw SQL.

A `Report` can be identified by the file naming schema: `report-name.report.m5oc`
