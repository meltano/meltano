# Fundamentals

Within the Meltano ecosystem, here are some commmon terms that you will encounter and what they mean:

## Column

A Column relates directly to a column in a table of a database. Relieving us for a sql field. AKA column definitions. Limited to column only. No custom SQL.

## Aggregate 

An Aggregate relates to a calculatable column, via count, sum or other. AKA aggregate definitions. Limited to predefined methods, no custom SQL. Custom SQL done via transforms through dbt.

## Table 

A Table relates to a table in a database. It defines a direct link to a table in the database. In adition, it also defines and contains columns and aggregates so you can sdelect which you want to show.

It can be identified by the file naming schema: `table-name.table.m5o` and should be stored in the `/tables` directory.

## Design

An Design maps multiple tables together via joins. It points to many tables by names and can also add filters. At a high level, it does the following:

1. Takes selected columns to generate SQL from the `.m5oc` file
1. Runs the SQL query
1. Outputs the desired graph

In addition, it is the file that you'd use to do the actual analysis because it defines the relationship between the tables. 

It can be identified by the file naming schema: `design-name.design.m5o`.

## Collection 

A Collection is a single of group of designs together. It also determines how they will be mapped together.

It can be identified by the naming schema: `collection-name.collection.m5o` and should be stored in the `/collections` directory.

## Report

A Report is a saved state of selecting and analyzing a design. It contains a subset of fields that you select from multiple tables and is ultimately the selected analysis. It can also be generated from raw SQL.

It can be identified by the file naming schema: `report-name.report.m5oc`

## Dashboard

A Dashboard is a group of many reports.

It is identified by the file naming schema: `set-name.dashboard.m5o` and is stored in the `/dashboards` directory.

## M5O Files

There are two primary types of `.m5o` files:

1. `.m5o` are uncompiled files that users will normally interact with
2. `.mtoc` are compiled and are not typically modified manually

`.m5o` is based on HOCON syntax and serve as input for the compiled files that contain JSON.


