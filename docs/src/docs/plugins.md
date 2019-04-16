---
sidebarDepth: 2
---

# Plugins

## Extractors

Extractors are defined as the component that pulls data out of a data source, using the best integration for extracting bulk data.
Currently, Meltano supports [Singer.io](https://singer.io) taps as extractors.

### tap-zuora

<table>
  <tr>
    <th>Data Source</th>
    <td><a target="_blank" href="https://www.zuora.com/">https://www.zuora.com</a></td>
  </tr>
  <tr>
    <th>Repository</th>
    <td><a target="_blank" href="https://github.com/singer-io/tap-zuora">https://github.com/singerio/tap-zuora</a></td>
  </tr>
</table>

#### Default configuration

**.env**
```bash
ZUORA_USERNAME
ZUORA_PASSWORD
ZUORA_API_TOKEN   # preferred to ZUORA_PASSWORD
ZUORA_API_TYPE    # specifically 'REST' or 'AQuA'
ZUORA_PARTNER_ID  # optional, only for the 'AQuA` API type
ZUORA_START_DATE
ZUORA_SANDBOX     # specifically 'true' or 'false'
```

### tap-csv

<table>
  <tr>
    <th>Data Source</th>
    <td>Traditionally-delimited CSV files (commas separated columns, newlines indicate new rows, double quoted values) as defined by the defaults of the python csv library.</td>
  </tr>
  <tr>
    <th>Repository</th>
    <td><a target="_blank" href="https://gitlab.com/meltano/tap-csv">https://gitlab.com/meltano/tap-csv</a></td>
  </tr>
</table>

#### Default configuration

**.env**
```bash
export TAP_CSV_FILES_DEFINITION="files_def.json"
```

Where `files_def.json` is a json file with all the CSV files to be loaded:

**files_def.json**
```json
[
  { "entity" : "leads",
    "file" : "/path/to/leads.csv",
    "keys" : ["Id"]
  },
  { "entity" : "opportunities",
    "file" : "/path/to/opportunities.csv",
    "keys" : ["Id"]
  }
]
```

Description of available options:
  - entity: The entity name to be passed to singer (i.e. the table name).
  - file: Local path to the file to be ingested. Note that this may be a directory, in which case all files in that directory and any of its subdirectories will be recursively processed.
  - keys: The names of the columns that constitute the unique keys for that entity.

## Loaders

A loader is a component for the bulk import of data. Currently, Meltano supports [Singer.io](https://singer.io) targets as loaders.

### target-snowflake

::: warning
This plugin will enable data to be loaded in a [Snowflake](https://www.snowflake.com) database. Please note that querying in the Meltano UI is not supported, yet.
You can follow the progress on this feature in this issue: [meltano/meltano#428](https://gitlab.com/meltano/meltano/issues/428)
:::

<table>
  <tr>
    <th>Database</th>
    <td><a target="_blank" href="https://www.snowflake.com/">https://www.snowflake.com</a></td>
  </tr>
</table>

#### Default configuration

**.env**
```bash
SF_ACCOUNT
SF_USER
SF_PASSWORD
SF_ROLE       # in UPPERCASE
SF_DATABASE   # in UPPERCASE
SF_WAREHOUSE  # in UPPERCASE
```
