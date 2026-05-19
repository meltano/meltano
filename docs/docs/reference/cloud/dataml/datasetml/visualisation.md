---
title: Visualisation
description: Reference documentation for dataset visualisation customisation.
permalink: /dataml/datasetml/visualisation
parent: DatasetML
grand_parent: DataML 
nav_order: 1
---

# {{page.title}}

---

You can use different chart types by utilizing the `visualisation` key of the [Matatika dataset YAML file]({{site.baseurl}}/dataml/datasetml/).
{: .fs-5 }

The `visualisation` key contains information about displaying the chart for the insight.
{: .fs-5 }

### Example

```yaml
visualisation: |-
    {"chartjs-chart": {"chartType": "bar"}}
```

---

## ChartJS charts

Beautiful ChartJS data visualisations can be achieved with the `chartjs-chart` visualisation type.

```yaml
visualisation: |-
    {"chartjs-chart": {"chartType": "bar"}}
```

Value | Description
----- | -----------
`bar` | Bar Chart
`line` | Line Chart.
`doughnut` | Doughnut Chart.
`pie` | Pie Chart.
`bubble` | Bubble Chart.
`scatter` | Scatter Chart.
`treemap` | Treemap Chart.

For more information on Chart.js, see their documentation at [https://www.chartjs.org/docs/latest/](https://www.chartjs.org/docs/latest/){:target="_blank"}

---

## Mermaid diagrams

[Mermaid diagrams](https://mermaid.js.org/intro/#diagram-types){:target="_blank"} are supported with the `mermaid` visualisation type. The [diagram syntax](https://mermaid.js.org/intro/syntax-reference.html){:target="_blank"} should be provided in `rawData`.

```yaml
visualisation: |-
    {"mermaid": {}}
rawData: |-
    erDiagram
        CUSTOMER }|..|{ DELIVERY-ADDRESS : has
        CUSTOMER ||--o{ ORDER : places
        CUSTOMER ||--o{ INVOICE : "liable for"
        DELIVERY-ADDRESS ||--o{ ORDER : receives
        INVOICE ||--|{ ORDER : covers
        ORDER ||--|{ ORDER-ITEM : includes
        PRODUCT-CATEGORY ||--|{ PRODUCT : contains
        PRODUCT ||--o{ ORDER-ITEM : "ordered in"
```

---

## Carousel

You can display images side-by-side with back/next buttons using the `carousel` visualisation type.

```yaml
visualisation: |-
    {"carousel": {}}
```

### Options

#### `style`

CSS overrides to set on the main carousel container element, to override its default styling.

Type: object
Default: none

```yaml
visualisation: |-
    {"carousel": {"style": {
        "max-width": "600px",
        "padding": "12px",
        "background-color": "rgba(0, 0, 0, 0.1)"
    }}}
```

---

## HTML table

Basic table layout for datasets can be achieved with the `html-table` visualisation type.

```yaml
visualisation: |-
    {"html-table": {}}
```

---

## HTML metric

Metric layout for datasets can be achieved with the `html-metric` visualisation type.

```yaml
visualisation: |-
    {"html-metric": {}}
```

This visualisation is designed to be used as either a single metric of a total, or to display a total and its breakdown.

The first value you pass will be displayed as a big centered value, and every subsequent value will be smaller and in a row below the first. This lets you do things like show the total number of tests run, then the number of passed and failed below.

### Color Options

By default the background is white and the text is black, but in all our datasets you can pass a `palette` setting through the chart's `metadata`:

```yaml
metadata: |-
  {
      "name": "elementary_test_results", 
      "label": "metric", 
      "related_table": {
        "columns": [
        ], 
        "aggregates": [
            {"name": "total", "label": "Total", "description": "Total"},
            {"name": "pass", "label": "Pass", "description": "Pass"},
            {"name": "fail", "label": "Fail", "description": "Fail"}
        ]
      },
    "palette": [[255, 255, 255],[0, 0, 0],[0, 255, 0],[255, 0, 0]]
  }

```

For our `html-metric`, the first color is always the background, then every other color will apply in order to each of the aggregates you are visualising. If you only provide 2 colors and 2 aggregates then you get:
- The first color as background
- The second color on the first aggregate
- The default black text color for the second aggregate

---

Further Reading: 

- [API Datasets]({{site.baseurl}}/api/resources/datasets)
- [Example Charts](basic-examples)