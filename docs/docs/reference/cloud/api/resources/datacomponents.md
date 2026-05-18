---
title: Datacomponents
description: Matatika Datacomponents resource reference documentation
permalink: /api/resources/datacomponents
parent: Resources
grand_parent: API
nav_order: 11
components: request-md-components/datacomponents
---

# {{page.title}}

Datacomponents hold configuration for [dataplugins](dataplugins), and are the building blocks for constructing [pipelines](pipelines). One dataplugin may be referenced by many datacomponents, each with a different set of `properties` for the dataplugin [`settings`](dataplugins#setting). One pipeline may reference multiple datacomponents.
{: .fs-5 }

---

## Objects
{: .no_toc}

### Datacomponent

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`id` | `string` | Version 4 UUID | The datacomponent ID
`created` | `string` | ISO 8601 timestamp | When the datacomponent was created
`lastModified` | `string` | ISO 8601 timestamp | When the datacomponent was last modified
`name` | `string` | | The datacomponent name
`dataPlugin` | `string` | | Create / update with [dataplugin](dataplugins#dataplugin) `fullyQualifiedName`
`properties` | `object` | [`Properties`](#properties) | The datacomponent properties, defined by the [dataplugin](dataplugins) [`settings`](dataplugins#setting)<br>Properties are key-value pairs, where keys reference setting `name`s

{% include snippets/api/datacomponents/view-a-datacomponent/response-body.md %}

#### Extractor Datacomponent
Datacomponents that are backed by [dataplugins](dataplugins) of `type` `EXTRACTOR` expose the following additional configuration:

Path | JSON Type | Format | Description
---- | --------- | ------ | -----------
`streams` | `object[]` | Array of [Stream](#stream)s | The available streams (populated after [verifying a pipeline](pipelines#verify-a-pipeline) that references this datacomponent)

{% include snippets/api/jobs/view-an-extractor-datacomponent/response-body.md %}

### Properties

For each setting in the [dataplugin](dataplugins) [`settings`](dataplugins#setting):

Path | JSON Type | Format | Description
---- | --------- | ------ | -----------
Refer to setting `name` | Refer to setting `kind` | Refer to setting `kind` | Refer to setting `description`

#### Reserved Properties for Extractor Datacomponents

Path | JSON Type | Format | Description
---- | --------- | ------ | -----------
`_select` | `string` | JSON array | Meltano [stream and property selection rules](https://docs.meltano.com/concepts/plugins#select-extra)
`_metadata` | `string` | JSON object | Meltano [stream and property metadata rules](https://docs.meltano.com/concepts/plugins#metadata-extra)

### Stream

Path | JSON Type | Format | Description
---- | --------- | ------ | -----------
`name` | `string` | | The stream name
`selected` | `string` | [Entity Selection](#entity-selection) | The stream entity selection type
`fields` | `object[]` | Array of [Field](#fields)s | The available stream fields

### Field

Path | JSON Type | Format | Description
---- | --------- | ------ | -----------
`name` | `string` | | The field name
`selected` | `string` | [Entity Selection](#entity-selection) | The field entity selection type

## Formats
{: .no_toc}

### Entity Selection
{: .d-inline-block }

Value | Description
----- | -----------
`AUTOMATIC` | The entity is automatically selected by the underlying [extractor](https://docs.meltano.com/concepts/plugins#extractors){:target="_blank"} and will always be synced
`SELECTED` | The entity is selected and will be synced
`EXCLUDED` | The entity is excluded and will not be synced

---

#### Requests

- TOC
{: toc }

---

{% include {{ page.components }}/view-all-datacomponents-in-a-workspace.md %}
{% include {{ page.components }}/view-a-datacomponent.md %}
{% include {{ page.components }}/initialise-a-new-datacomponent-in-a-workspace.md %}
{% include {{ page.components }}/create-or-update-a-datacomponent-in-a-workspace.md %}
{% include {{ page.components }}/update-a-datacomponent.md %}
{% include {{ page.components }}/delete-a-datacomponent.md %}
