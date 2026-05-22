---
title: Query
description: Reference documentation for dataset queries.
sidebar_position: 3
---

You select the data for your chart by using the `query` key of the [dataset YAML file](.).

The `query` key in the dataset file is the sql query that is run against your chosen data store to retrieve data for use in displaying the insight.

You use the [`metadata`](metadata) key to format how you are displaying the returned information.

### Example

```yaml
query: |-
    SELECT
    report_date "google_analytics_locations.report_date"
    , sum(users) "google_analytics_locations.total_users"
    FROM google_analytics_locations
    WHERE report_date >= current_date - interval '14' day
    AND report_date < current_date
    GROUP BY report_date
    ORDER BY report_date
```
---

Further Reading:

- [API Datasets](/reference/cloud/api/resources/datasets)
