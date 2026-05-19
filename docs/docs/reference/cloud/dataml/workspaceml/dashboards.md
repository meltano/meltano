---
title: Dashboards
description: Reference documentation for workspace dashboard customisation.
permalink: /dataml/workspaceml/dashboards/
nav_order: 2
parent: WorkspaceML
grand_parent: DataML
---

# {{page.title}}

---

Dashboards allow you to design a layout for data and datasets in your workspace. These are fully customizable and render custom HTML and CSS, letting you format them as required.
{: .fs-5 }

---

You can create dashboards of your datasets in the Matataika app, by defining a few settings and then providing your dashboard content in your workspace's `workspace.yml` file.

### Example `workspace.yml`:

{% raw %}
```yaml
version: workspaces/v0.2
name: My workspace
domains:
  - matatika.com
  - example.co.uk
default_data_store: Warehouse
state_data_store: Warehouse
dataset_paths:
  - analyze/datasets
  - .meltano/analyze/datasets
channel_paths:
  - analyze/channels
pipeline_paths:
  - pipelines
plugin_paths:
  - plugins
data_store_paths:
  - datastores
app_properties:
  WELCOME_DATASET_ALIAS: welcome
  DASHBOARD_PAGE_TITLE: Data Observability Dashboard
  DASHBOARD_CONTENT: |-
    <div style={{'display':'flex', 'padding-bottom': '30px', 'justify-content': 'center'}}>
        <div style={{'border-right': '2px solid #D3D3D3'}}>
            <h2>Test results breakdown</h2>
            <DatasetChart alias="data-observability/test-results-breakdown"/>
        </div>
        <div>
            <h2>Tables health</h2>
            <DatasetLink alias="data-observability/table-health-breakdown">
                <DatasetChart alias="data-observability/tables-health" />
            </DatasetLink>
        </div>
    </div>
  APP_MENU_ITEMS: |-
    [
      {"name": "dashboard", "faIcon": "chart-bar", "label": "Dashboard"},
      {"name": "explore", "faIcon": "hashtag", "label": "Explore"},
      {"name": "channels", "faIcon": "database", "label": "Channels"},
      {"name": "library", "faIcon": "list", "label": "Library"},
      {"name": "starred", "faIcon": "star", "label": "Starred"},
      {"name": "help", "faIcon": "question-circle", "label": "Help"}
    ]
default_data_store: Warehouse
dataset_paths:
  - analyze/datasets
  - .meltano/analyze/datasets
channel_paths:
  - analyze/channels
pipeline_paths:
  - pipelines
plugin_paths:
  - plugins
data_store_paths:
  - datastores
```
{% endraw %}

### Dashboard Settings

Note that these settings are nested under `app_properties`.

Setting | Description 
----------- | --------
`DASHBOARD_PAGE_TITLE` | Dashboard page title
`DASHBOARD_CONTENT` | Your dashboard content as HTML
`APP_MENU_ITEMS` | Currently you have to provide an override for all pages showing in the app, including your new dashboard page. 

A list of `faIcons` for your Dashboard can be found here: [FontAwesome Icons v5](https://fontawesome.com/v5/search). You can use any free icons as your dashboard icon, or to change the icon of an existing page.

### Dashboard Components

#### `DatasetChart`
Allows you to choose any dataset in your workspace by its alias, and render it on your dashboard.

Prop | Type | Description | Required | Default
--- | --- | --- | ---
`alias` | String | The dataset alias to fetch for render | If `dataset` not specified |
`dataset` | Object | The dataset to render | If `alias` not specified |
`showTable` | Boolean | Show the dataset data as a table | No | `false`

#### `DatasetData`
Allows you to render custom JSX in the context of a dataset and its data.

Prop | Type | Description | Required | Default
--- | --- | --- | --- | ---
`alias` | String | The dataset alias to fetch for render | If `dataset` not specified |
`dataset` | Object | The dataset to render | If `alias` not specified |
`render` | Function | The JSX content to render (args: `dataset`, `data`) | Yes | |

#### `DatasetLink`
Wraps elements or text and create an internal link to a dataset in your workspace (no page reload).

Prop | Type | Description | Required | Default
--- | --- | --- | --- | ---
`alias` | String | The dataset alias | Yes |

#### `Back`
Renders a back button.

#### `DownloadDataset`
Download a dataset from the workspace. 

Prop | Type | Description | Required | Default
--- | --- | --- | --- | ---
`alias` | String | The dataset alias to fetch for render | If `dataset` not specified |
`dataset` | Object | The dataset to render | If `alias` not specified |
`tooltip` | String | The text displayed on hover | No | `Download {dataset title OR dataset alias}`

#### `DownloadResource`
Download a resource from the workspace. 

Prop | Type | Description | Required | Default
--- | --- | --- | --- | ---
`path` | String | The resource path | Yes |
`tooltip` | String | The text displayed on hover | No | `Download {path}`
