---
title: Basic Examples
description: Dataset basic examples.
permalink: /dataml/datasetml/basic-examples
parent: DatasetML
grand_parent: DataML 
nav_order: 4
---

# {{page.title}}

---

These charts are the output of the [Matatika dataset YAML file]({{site.baseurl}}/dataml/datasetml/) listed below each of them.
{: .fs-5 }

You can find the original YAML files in our [examples github repo](https://github.com/Matatika/matatika-examples/tree/master/example_datasets){:target="_blank"}.
{: .fs-5 }

---

## Basic Bar Chart

{% include example_charts/basic_charts/Example_Basic_Bar_Chart.html %}

```yaml
version: datasets/v0.2
title: Example Basic Bar Chart
questions: How many Earth-years does it take for Jupiter to orbit the sun?
description: |-
  #Example

  Sun orbit data for some planets within our solar system.
metadata: |-
  {
    "name": "planet", 
    "related_table": {
      "columns": [
        {"name": "name", "label": "Planet Name", "description": "Planet Name"}
      ], 
      "aggregates": [
        {"name": "orbitduration", "label": "Orbit Duration (Earth Years)", "description": "Orbit Duration (Earth Years)"}
      ]
    }
  }
rawData: |-
  [
    {"planet.name": "Earth", "planet.orbitduration": 1},
    {"planet.name": "Mars", "planet.orbitduration": 1.9167},
    {"planet.name": "Jupiter", "planet.orbitduration": 11.8333},
    {"planet.name": "Saturn", "planet.orbitduration": 29.5}
  ]
visualisation: '{"chartjs-chart": {"chartType": "bar"}}'
```
---

## Grouped Bar Chart

{% include example_charts/basic_charts/Example_Grouped_Bar_Chart.html %}


```yaml
version: datasets/v0.2
title: Example Grouped Bar Chart
questions: How many Earth-years does it take for Jupiter to orbit the sun?
description: |-
  #Example
  
  Sun orbit data for some planets within our solar system.
metadata: |-
  {
    "name": "planet",
    "related_table": {
      "columns": [
        {"name": "name", "label": "Planet Name", "description": "Planet Name"}
      ], 
      "aggregates": [
        {"name": "orbitduration", "label": "Orbit Duration (Earth Years)", "description": "Orbit Duration (Earth Years)"},
        {"name": "orbitdistance", "label": "Orbit Distance (Light Years)", "description": "Orbit Distance (Light Years)"}
      ]
    }
  }
rawData: |-
  [
    {"planet.name": "Earth", "planet.orbitdistance": 0.8708, "planet.orbitduration": 1},
    {"planet.name": "Mars", "planet.orbitdistance": 1.3242, "planet.orbitduration": 1.9167},
    {"planet.name": "Jupiter", "planet.orbitdistance": 4.5287, "planet.orbitduration": 11.8333},
    {"planet.name": "Saturn", "planet.orbitdistance": 8.2997, "planet.orbitduration": 29.5}
  ]
visualisation: '{"chartjs-chart": {"chartType": "bar"}}'
```
---

## Stacked Bar Chart

{% include example_charts/basic_charts/Example_Stacked_Bar_Chart.html %}

```yaml
version: datasets/v0.2
title: Example Stacked Bar Chart
questions: How many Earth-years does it take for Jupiter to orbit the sun?
description: |-
  #Example

  Sun orbit data for some planets within our solar system.
metadata: |-
  {
    "name": "planet",
    "related_table": {
      "columns": [
        {"name": "name", "label": "Planet Name", "description": "Planet Name"}
      ], 
      "aggregates": [
        {"name": "orbitduration", "label": "Orbit Duration (Earth Years)", "description": "Orbit Duration (Earth Years)"},
        {"name": "orbitdistance", "label": "Orbit Distance (Light Years)", "description": "Orbit Distance (Light Years)"}
      ]
    }
  }
rawData: |-
  [
    {"planet.name": "Earth", "planet.orbitdistance": 0.8708, "planet.orbitduration": 1},
    {"planet.name": "Mars", "planet.orbitdistance": 1.3242, "planet.orbitduration": 1.9167},
    {"planet.name": "Jupiter", "planet.orbitdistance": 4.5287, "planet.orbitduration": 11.8333},
    {"planet.name": "Saturn", "planet.orbitdistance": 8.2997, "planet.orbitduration": 29.5}
  ]
visualisation: |-
  {
    "chartjs-chart": {
      "chartType": "bar", 
      "options": {
        "scales": {
          "x": {
            "stacked": true
          }
        }
      }
    }
  }
```
---

## Doughnut Chart

{% include example_charts/basic_charts/Example_Basic_Doughnut_Chart.html %}

```yaml
version: datasets/v0.2
title: Example Basic Doughnut Chart
questions: What shop had the most visitors?
description: |-
  #Example
  
  Stats for shops and visitor amount.
metadata: |-
  {
    "name": "customer", 
    "related_table": {
      "columns": [
      ], 
      "aggregates": [
        {"name": "visitors", "label": "Visitors", "description": "Number of Visitors"},
        {"name": "sales", "label": "Sales", "description": "Number of Sales"}
      ]
    }
  }
rawData: |-
  [
    {"customer.visitors": 1150, "customer.sales": 1040}
  ]
visualisation: '{"chartjs-chart": {"chartType": "doughnut"}}'
```
---

## Pie Chart

{% include example_charts/basic_charts/Example_Basic_Pie_Chart.html %}

```yaml
version: datasets/v0.2
title: Example Basic Pie Chart
questions: For the last 7 days, how many visitors did Shop One have?
description: |-
  #Example
  
  Shop One visitors for the last 7 days.
metadata: |-
  {
    "name": "customer", 
    "related_table": {
      "columns": [
      ], 
      "aggregates": [
        {"name": "visitors_monday", "label": "Monday Visitors", "description": "Monday Visitors"},
        {"name": "visitors_tuesday", "label": "Tuesday Visitors", "description": "Tuesday Visitors"},
        {"name": "visitors_wednesday", "label": "Wednesday Visitors", "description": "Wednesday Visitors"},
        {"name": "visitors_thursday", "label": "Thursday Visitors", "description": "Thursday Visitors"},
        {"name": "visitors_friday", "label": "Friday Visitors", "description": "Friday Visitors"},
        {"name": "visitors_saturday", "label": "Saturday Visitors", "description": "Saturday Visitors"},
        {"name": "visitors_sunday", "label": "Sunday Visitors", "description": "Sunday Visitors"}
      ]
    }
  }
rawData: |-
  [
    {"customer.visitors_monday": 1090,
    "customer.visitors_tuesday": 980,
    "customer.visitors_wednesday": 1020,
    "customer.visitors_thursday": 1030,
    "customer.visitors_friday": 1150,
    "customer.visitors_saturday": 1430,
    "customer.visitors_sunday": 1290}
  ]
visualisation: '{"chartjs-chart": {"chartType": "doughnut"}}'
```
---

## Line Chart

{% include example_charts/basic_charts/Example_Basic_Line_Chart.html %}

```yaml
version: datasets/v0.2
title: Example Basic Line Chart
questions: Which shop had the most sales?
description: |-
  #Example
  
  Stats for shops, visitor amount, and sales.
metadata: |-
  {
    "name": "customer", 
    "related_table": {
      "columns": [
        {"name": "name", "label": "Shop Name", "description": "Shop Name"}
      ], 
      "aggregates": [
        {"name": "visitors", "label": "Visitors", "description": "Number of Visitors"},
        {"name": "sales", "label": "Sales", "description": "Number of Sales"}
      ]
    }
  }
rawData: |-
  [
    {"customer.name": "Shop One", "customer.visitors": 1150, "customer.sales": 1040},
    {"customer.name": "Shop Two", "customer.visitors": 980, "customer.sales": 670},
    {"customer.name": "Shop Three", "customer.visitors": 1020, "customer.sales": 990},
    {"customer.name": "Shop Four", "customer.visitors": 1410, "customer.sales": 1020},
    {"customer.name": "Shop Five", "customer.visitors": 890, "customer.sales": 800}
  ]
visualisation: '{"chartjs-chart": {"chartType": "line"}}'
```
---
