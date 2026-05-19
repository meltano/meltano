---
title: Metadata
description: Reference documentation for dataset metadata.
permalink: /dataml/datasetml/metadata
parent: DatasetML
grand_parent: DataML 
nav_order: 2
---

# {{page.title}}

---

You can change the format and display of your chart by using the `metadata` key of the [Matatika dataset YAML file]({{site.baseurl}}/dataml/datasetml/).
{: .fs-5 }

The `metadata` key relates to how the data from the [`query`](query) within the dataset is displayed as an insight.
{: .fs-5 }

### Example

```yml
metadata: |-
    {
        "name": "google_analytics_locations",
        "label": "Daily Users",
        "related_table": {
            "columns": [
                {
                    "name": "report_date",
                    "label": "Date",
                    "description": "Date"
                }
            ], 
            "aggregates": [
                {
                    "name": "total_users",
                    "label": "Total Users",
                    "description": "Total Users"
                }
            ]
        }
    }
```

---

Metadata Key | Details
------------ | -------
`name` | Name of the sql table you are querying, or it alias if assigned.
`label` | Chart label.
`related_table` | Columns and aggregates to display in the chart.
`columns` | x-axis catagories, usually dates or groups.
`aggregates` | Bars, Points, Lines that show the information over the `columns` catagories.
`links` | Can be defined to connect datasets or external links, either by clicking on specific aggregates, or defining a link globally.


## Post-processing
`columns` and `aggregates` support post-processing to modify values before they are rendered by the visualisation. This can be supplied in one of two ways:

- A named post-processor: `post_process` 
- An expression: `post_process_expr`

When both `post_process` and `post_process_expr` are supplied for a single column or aggregate, `post_process_expr` will take precedence.

### Named post-processors
Named post-processors are aliases for common processing methods. A named post-processor can be specified using `post_process`. 

Name | Description
--- | ---
`json_parse` | Parse a JSON string

```yml
metadata: |-
    {
        "name": "test_failures",
        "label": "Test failures",
        "related_table": {
            "columns": [
                {
                    "name": "rows_json",
                    "label": "Rows JSON",
                    "post_process": "json_parse"
                }
            ]
        }
    }
```

### Expressions
Expressions can be used to modify values with a JavaScript function that accepts a single argument as the value and returns the processed value. This function can be named (e.g. [`JSON.parse`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/JSON/parse)) or anonymous (e.g. `value => value.toUpperCase()`). An expression can be specified using `post_process_expr`.

```yml
metadata: |-
    {
        "name": "test_failures",
        "label": "Test failures",
        "related_table": {
            "columns": [
                {
                    "name": "rows_json",
                    "label": "Rows JSON",
                    "post_process_expr": "JSON.parse"
                }
            ]
        }
    }
```

## Examples of Links

### Global Link Example (Dataset)

With a global link, if you click on any of the data in the visualisation you have to option of viewing what is linked. You can use a global link to drill-down to another dataset, or link to an external source.

```yaml
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
        },
        "links": [{"dataset": "another_datasets_file_name_without_file_extension"}]
    }
```

### Aggregate Link Example (External Link)

With an aggregate link, if you click on the specific aggregate data in the visualisation you have to option of viewing what is linked. You can use a aggregate link to drill-down to another dataset, or link to an external source.

```yaml
metadata: |-
    {
        "name": "google_analytics_locations",
        "label": "Daily Users",
        "related_table": {
        "columns": [
            {"name": "report_date", "label": "Date", "description": "Date"}
        ], 
        "aggregates": [
            {"name": "total_users", "label": "Total Users", "description": "Total Users", "links": [
                    {"href": "https://developers.google.com/analytics", "target": "_blank"}]
            }
        ]
        }
    }
```
---

Further Reading: 

- [API Datasets]({{site.baseurl}}/api/resources/datasets)
- [Example Charts](basic-examples)