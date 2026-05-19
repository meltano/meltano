---
title: DatasetML
description: Reference documentation for dataset definition model.
permalink: /dataml/datasetml/
nav_order: 2
parent: DataML
has_children: true
---

# {{page.title}}

---

Examples and reference documentation for datasets and visualisation.
{: .fs-5 }

Use the Matatika dataset YAML to create and format insights in your workspace as code.
{: .fs-5 }

Our dataset files are stored as YAML files, you can read more about the YAML format and its syntax [here](https://yaml.org/){:target="_blank"}.
{: .fs-5 }

---

### Example: `analyze/datasets/tap-google-analytics/google_analytics_daily_users_last_14_days.yml`

```yaml
version: datasets/v0.2
source: Google Analytics
title: "Google Analytics Daily Users Last 14 Days"
questions: ‘How many users has there been over the last 14 days?’
description: |-
    Daily users over the last 14 days.

    #google-analytics
metadata: |-
    {
        "name": "google_analytics_locations",
        "label": "Daily Users",
        "related_table": {
        "columns": [
            {"name": "report_date", "label": "Date", "description": "Date"}
        ], 
        "aggregates": [
            {"name": "total_users", "label": "Total Users", "description": "Total Users"}
        ]
        }
    }
visualisation: |-
    {"chartjs-chart": {"chartType": "bar"}}
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

### Key Information

Path | JSON Type | Description
---- | --------- | -----------
`version` | `string` | The version determines how the CLI handles publishing the dataset. 
`source` | `string`  | A channel name to be used to group up related datasets in your workspace.
`title` | `string` | The title at the top of the insight.
`questions` | `string` | Questions that your dataset answers, so people can find the dataset just by asking questions.
`description` | `string` | Information about what the dataset is, how it's being filtered or displayed and other relevant information. You can also add `#tags`.
`metadata` | `string` of JSON | Details about how the dataset's chart is laid out. [More Info]({{site.baseurl}}/dataml/datasetml/metadata)
`visulisation` | `string` of JSON | Details about the precise visualisation of the datasets chart. [More Info]({{site.baseurl}}/dataml/datasetml/visualisation)
`query` | `string` of SQL | The query that returns the data from your datastore for use in the dataset's chart and related table. [More Info]({{site.baseurl}}/dataml/datasetml/query)
`rawData` | `string` of a List | The rawData key allows you to hard-code data directly into your dataset.

## String Formatting

You may use any of the following string formats:
```yaml
title: Google Analytics Daily Users Last 14 Days

title: 'Google Analytics Daily Users Last 14 Days'

title: "Google Analytics Daily Users Last 14 Days"

title: |-
    Google Analytics Daily Users Last 14 Days
    Multi-line string, remember to indent
```

The multiline string is generally the best way to display the `string` of JSON or SQL.

---

Further Reading: 

- [API Datasets]({{site.baseurl}}/api/resources/datasets)
- [Example Charts]({{site.baseurl}}/dataml/datasetml/basic-examples)