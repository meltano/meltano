---
title: Query
description: Reference documentation for dataset queries.
permalink: /dataml/datasetml/query
parent: DatasetML
grand_parent: DataML 
nav_order: 3
---

# {{page.title}}

---

You select the data for your chart by using the `query` key of the [Matatika dataset YAML file]({{site.baseurl}}/dataml/datasetml/).
{: .fs-5 }

The `query` key in the dataset file is the sql query that is run against your chosen data store to retrieve data for use in displaying the insight.
{: .fs-5 }

You use the [`metadata`](metadata) key to format how you are displaying the returned information.
{: .fs-5 }

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

- [API Datasets]({{site.baseurl}}/api/resources/datasets)