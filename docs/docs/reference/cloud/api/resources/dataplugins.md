---
title: Dataplugins
description: Matatika Dataplugins resource reference documentation
permalink: /api/resources/dataplugins
parent: Resources
grand_parent: API
nav_order: 11
components: request-md-components/dataplugins
---

# {{page.title}}

Dataplugins simply define a source of data from a given repository. Matatika provides a number of pre-configured platform-wide dataplugins out-the-box, as well as the ability to create custom dataplugins through the API. From these, [pipeline](pipelines) jobs can be run to inject data into a workspace.
{: .fs-5 }

---

## Objects
{: .no_toc}

### Dataplugin

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`id` | `string` | Version 4 UUID | The dataplugin ID
`name` | `string` | | The dataplugin name
`description` | `string` | | A description of the dataplugin
`repositoryUrl` | `string` | URL | The dataplugin repository URL
`settings` | `object[]` | Array of [`Setting`](#setting)s | The dataplugin settings

{% include snippets/api/dataplugins/view-a-dataplugin/response-body.md %}

### Setting

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`name` | `string` | | The setting name
`value` | `string` | | The setting default value
`label` | `string` | | The setting label
`protected` | `bool` | | The setting protection status
`kind` | `string` | [Setting Kind](#setting-kind) | The setting kind
`description` | `string` | | A description of the setting
`placeholder` | `string` | | The setting placeholder text
`envAliases` | `string[]` | | Environment variable aliases for the setting
`documentation` | `string` | URL | The setting documentation URL
`oauth` | [`OAuth`](#oauth) | | The setting OAuth configuration
`env` | `string` | | 

### OAuth

Path | JSON Type | Format | Description
---- | ---- | ------- | -----------
`provider` | `string` | | The OAuth provider

## Formats
{: .no_toc}

### Setting Kind
{: .d-inline-block }

`string`
{: .float-right .mt-5 }

Value | Description
----- | -----------
`STRING` | String setting
`INTEGER` | Integer setting
`PASSWORD` | Password setting 
`HIDDEN` | Hidden setting
`BOOLEAN` | Boolean setting
`DATE_ISO8601` | ISO 8601 date setting
`EMAIL` | Email setting
`OAUTH` | OAuth setting
`FILE` | File setting
`ARRAY` | Array setting

---

#### Requests

- TOC
{: toc }

---

{% include {{ page.components }}/view-all-supported-dataplugins.md %}
{% include {{ page.components }}/view-the-matatika-discovery-yml.md %}
{% include {{ page.components }}/view-all-workspace-dataplugins.md %}
{% include {{ page.components }}/view-a-workspace-discovery-yml.md %}
{% include {{ page.components }}/view-a-dataplugin.md %}
{% include {{ page.components }}/initialise-a-new-dataplugin.md %}
{% include {{ page.components }}/publish-dataplugins-from-a-discovery-yml.md %}
{% include {{ page.components }}/create-a-dataplugin.md %}
{% include {{ page.components }}/update-a-dataplugin.md %}
{% include {{ page.components }}/delete-a-dataplugin.md %}
