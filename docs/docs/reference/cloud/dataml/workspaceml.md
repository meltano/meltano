---
title: WorkspaceML
description: Reference documentation for workspace definition model.
permalink: /dataml/workspaceml/
nav_order: 5
parent: DataML
has_children: true
---

# {{page.title}}

---

Reference documentation for the workspace configuration file.
{: .fs-5 }

Use the Matatika workspace YAML to configure your workspace as code.
{: .fs-5 }

The workspace file is stored in YAML file format, you can read more about the YAML format and its syntax [here](https://yaml.org/){:target="_blank"}.
{: .fs-5 }

---

### Example: `workspace.yml`

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
  WELCOME_DATASET_ALIAS: analyze/datasets/welcome
  WELCOME_MESSAGE: Welcome to the workspace
  FEED_VIEW_DEFAULT: listView
  DATASET_WATCH_ALERTS_ALT_TEXT: Select to receive summary of dataset updates
  DATASET_WATCH_ALL_ACTIVITY_ALT_TEXT: Select to receive updates and discussion from this dataset
  DATASET_ASSISTANT_TAB_ALERTS_ALT_TEXT: Updates
  DATASET_ASSISTANT_NO_ALERTS_ALT_TEXT: No updates
  NEWS_DATASET_ALERT_ALT_TEXT: Update
  HELP_DATASET_ALIAS: analyze/datasets/more_information
  TOOLBAR_SEARCH_ALT_TEXT: Search all datasets...
  HOME_PAGE: news
  MENU_ITEM_HOME_ALT_TEXT: My Updates
  MENU_ITEM_CHANNELS_ALT_TEXT: Lists
  MENU_ITEM_HELP_ALT_TEXT: More Information
  HELP_CUSTOM_FA_MENU_ICON: acorn
  ALERTS_HELP_TEXT: Watch for alerts or all activity.
  DISCUSSION_HELP_TEXT: Talk about this dataset!
  RELATED_HELP_TEXT: Datasets related to this one.
  DATASET_VIEW_TABS: alerts,discussion,related
  APP_MENU_ITEMS: '[{"name": "explore", "faIcon": "users", "label": "Profiles"}, {"name": "library", "faIcon": "list"}, {"name": "starred", "faIcon": "star"}]'
  LIBRARY_LIST_INFO_ITEM_TEXT: Profile(s)
  DATASET_ACTIONS: star,share,table,save
  MEMBER_COMMENTS_READ_ONLY: true
  MEMBER_COMMENTS_READ_ONLY_MESSAGE: Comments are set to read-only
  INVITATION_EMAIL_RESULT_URL: https://meltano.com/slack
  INVITATION_EMAIL_SUBJECT: You have been invited to a workspace
  INVITATION_EMAIL_TEMPLATE: |-
    <!DOCTYPE html>
    <html xmlns:th="http://www.thymeleaf.org">
    <head>
    </head>
    <body>
      <h2 th:inline="text">[[${invitationCreatorName}]] ([[${invitationCreatorEmail}]]) has
        invited you to the '[[${workspaceName}]]' Workspace.</h2>

      <p>
        <a th:href="${passwordResetTicketUrl}">Accept invitation</a>
      </p>

      <br />
      <hr style="border: 2px solid #EAEEF3; border-bottom: 0;" />
    </body>
    </html>
  DASHBOARD_PAGE_TITLE: Data Observability Dashboard
  DASHBOARD_CONTENT: |-
    <div style={{'display':'flex', 'justify-content': 'center'}}>
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
```
{% endraw %}

### Key Information

Path | JSON Type | Description
---- | --------- | -----------
`version`            | `string`   | The version identifies this artifact type.
`name`               | `string`   | Name of your workspace.
`default_data_store` | `string`   | Name of your workspace's default data store. (See [Data Store ML]({{site.baseurl}}/dataml/datastoreml)).  This controls the default for loading, query, transformation, and state (unless overridden with `state_data_store`).
`state_data_store`   | `string`   | Name of your workspace's state data store. (See [Data Store ML]({{site.baseurl}}/dataml/datastoreml)). This controls where pipeline state is stored and **must** reference a Postgres, BigQuery or Snowflake database (defaults to the managed warehouse data store, same as `default_data_store`).
`pipelines_image`    | `string`   | The path name of an image to run pipelines from
`image_url`          | `string`   | The Meltano tasks that will be run.
`dataset_paths`      | `string[]` | Paths for your workspace to deploy datasets from.
`channel_paths`      | `string[]` | Paths for your workspace to deploy channels from.
`pipeline_paths`     | `string[]` | Paths for your workspace to deploy pipelines from.
`plugin_paths`       | `string[]` | Paths for your workspace to deploy plugins from.
`app_properties`     | `object`   | A map of optional properties to customize your workspace. (See the example above).

---

### Environment-specific workspace configuration
Workspace configuration files with a `-*` suffix (e.g. `workspace-dev.yml`) define environment-specific workspace configuration. During deployment of a workspace, the base `workspace.yml` configuration is loaded, followed by a `workspace-*.yml` matching the active environment (if present).

Environment-specific workspace configuration files only need to contain the properties a user wants to override from the `workspace.yml` (`version` is required regardless).

`workspace.yml`
{: .tab .tabs-section-start}

```yml
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
```

`workspace-dev.yml`
{: .tab}

```yml
version: workspaces/v0.2
name: My workspace (dev)
pipelines_image: my-workspace-image:latest-dev
```
{: .tabs-section-end}


Further Reading: 

- [API Workspaces]({{site.baseurl}}/api/resources/workspaces)
- [Data Store ML]({{site.baseurl}}/dataml/datastoreml)
