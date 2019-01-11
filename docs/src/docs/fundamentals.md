# Fundamentals

Within the Meltano ecosystem, here are some commmon terms that you will encounter and what they mean:

## Column

A Column relates directly to a column in a table of a database. Relieving us for a sql field. AKA column definitions. Limited to column only. No custom SQL.

## Aggregate 

An Aggregate relates to a calculatable column, via count, sum or other. AKA aggregate definitions. Limited to predefined methods, no custom SQL. Custom SQL done via transforms through DBT.

## Table 

A Table relates to a table in a database. It defines a direct link to a table in the database. In addition, it also defines and contains columns and aggregates so you can select which you want to show.

It can be identified by the file naming schema: `table-name.table.m5o` and should be stored in the `/tables` directory.

## Design

An Design maps multiple tables together via joins. It points to many tables by names and can also add filters. 

In addition, it is the file that you'd use to do the actual analysis because it defines the relationship between the tables. 

It can be identified by the file naming schema: `design-name.design.m5o`.

## Collection 

A Collection is a group of designs together. 

It can be identified by the naming schema: `collection-name.collection.m5o` and should be stored in the `/collections` directory.

## Report

A Report is a saved state of selecting and analyzing a design. Can also be generated from raw SQL.

## Dashboard

A Dashboard is a group of many reports.

It is identified by the file naming schema: `set-name.dashboard.m5o` and is stored in the `/dashboards` directory.