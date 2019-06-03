---
sidebarDepth: 1
---

# Extractors & Loaders

## Extractors

Meltano Extractors are commonly prefixed with [tap](/docs/architecture.html#taps). 

::: tip 
If you can't find the extractor you need below, we have a [tutorial for creating your extractor](/docs/tutorial.html#advanced-create-a-custom-extractor). We are constantly working to build new extractors, and our current roadmap includes: Google Analytics, Google Ads, and Facebook Ads as next up on the list.
:::

### Carbon Intensity

`tap-carbon-intensity` pulls data from the Official Carbon Emissions Intensity API for Great Britain, which was developed by the [National Grid](https://www.nationalgrid.com/uk). For more information, check out [http://carbonintensity.org.uk/](http://carbonintensity.org.uk/).

#### Info

- Data Source: [Carbon Intensity API](https://api.carbonintensity.org.uk/)
- Repository: [https://gitlab.com/meltano/tap-carbon-intensity](https://gitlab.com/meltano/tap-carbon-intensity)

#### Install

1. Navigate to your Meltano project in the terminal
2. Run the following command:

```bash
meltano add extractor tap-carbon-intensity
```

If you are successful, you should see `Added and installed extractors 'tap-carbon-intensity'` in your terminal.

### CSV

`tap-csv` is a CSV reader that is optimized for tasks where the file structure is highly predictable. 

#### Info

- **Data Source**: Traditionally-delimited CSV files (commas separated columns, newlines indicate new rows, double quoted values) as defined by the defaults of the python csv library.
- **Repository**: [https://gitlab.com/meltano/tap-csv](https://gitlab.com/meltano/tap-csv)

#### Install

1. Navigate to your Meltano project in the terminal
2. Run the following command:

```bash
meltano add extractor tap-csv
```

If you are successful, you should see `Added and installed extractors 'tap-csv'` in your terminal.

#### Configuration

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

  - **entity**: The entity name to be passed to singer (i.e. the table name).
  - **file**: Local path to the file to be ingested. Note that this may be a directory, in which case all files in that directory and any of its subdirectories will be recursively processed.
  - **keys**: The names of the columns that constitute the unique keys for that entity.

### Fastly

`tap-fastly` pulls raw data from Fastly and produces JSON-formatted data per the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

#### Info

- **Data Source**: [Fastly](https://www.fastly.com/)
- **Repository**: [https://gitlab.com/meltano/tap-fastly](https://gitlab.com/meltano/tap-fastly)

#### Install

1. Navigate to your Meltano project in the terminal
2. Run the following command:

```bash
meltano add extractor tap-fastly
```

If you are successful, you should see `Added and installed extractors 'tap-fastly'` in your terminal.

#### Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

```bash
export FASTLY_API_TOKEN="yourFastlyApiToken"
# The date uses ISO-8601 and supports time if desired
export FASTLY_START_DATE="YYYY-MM-DD"
```

### GitLab

`tap-gitlab` pulls raw data from GitLab's [REST API](https://docs.gitlab.com/ee/api/README.html) and extracts [the following resources](https://gitlab.com/meltano/tap-gitlab#tap-gitlab) from GitLab. It then outputs the schema for each resource
and incrementally pulls data based on the input state
#### Info

- **Data Source**: [GitLab's REST API](https://docs.gitlab.com/ee/api/README.html)
- **Repository**: [https://gitlab.com/meltano/tap-gitlab](https://gitlab.com/meltano/tap-gitlab)

#### Install

1. Navigate to your Meltano project in the terminal
1. Run the following command:

```bash
meltano add extractor tap-gitlab
```

If you are successful, you should see `Added and installed extractors 'tap-gitlab'` in your terminal.

3. Get your GitLab access token
    - Login to your GitLab account
    - Navigate to your profile page
    - Create an access token

# Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

```bash
export GITLAB_API_TOKEN="access token from step 3"
export GITLAB_API_GROUPS="myorg mygroup"
export GITLAB_API_PROJECTS="myorg/repo-a myorg-repo-b"
# The date uses ISO-8601 and supports time if desired
export GITLAB_API_START_DATE="YYYY-MM-DD"
```

::: info
  - Either groups or projects need to be provided
  - Filling in 'groups' but leaving 'projects' empty will sync all group projects.
  - Filling in 'projects' but leaving 'groups' empty will sync selected projects.
  - Filling in 'groups' and 'projects' will sync selected projects of those groups.
:::
    
::: warning
Currently, groups don't have a date field which can be tracked
:::

### Marketo

`tap-marketo` pulls raw data from Marketo's REST API and extracts activity types, activites, and leads from Marketo.

#### Info

- **Data Source**: [Marketo's REST API](http://developers.marketo.com/rest-api/)
- **Repository**: [https://gitlab.com/meltano/tap-marketo](https://gitlab.com/meltano/tap-marketo)

#### Install

1. Navigate to your Meltano project in the terminal
2. Run the following command:

```bash
meltano add extractor tap-marketo
```

If you are successful, you should see `Added and installed extractors 'tap-marketo'` in your terminal.

#### Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

```bash
export MARKETO_CLIENT_ID="yourClientId"
export MARKETO_CLIENT_SECRET="yourClientSecret"
export MARKETO_ENDPOINT="yourEndpointUrl"
export MARKETO_IDENTITY="yourIdentity"
export MARKETO_START_TIME="yourStartTime"
```

### MongoDB

::: warning
This tap is currently a proof of concept and may have limited utility, but feedback is always welcome on [issue #631](https://gitlab.com/meltano/meltano/issues/631)
:::

`tap-mongodb` pulls raw data from a MongoDB source.  

#### Info

- **Data Source**: [MongoDB](https://www.mongodb.com/) source
- **Repository**: [https://github.com/singer-io/tap-mongodb](https://github.com/singer-io/tap-mongodb)

#### Install

1. Navigate to your Meltano project in the terminal
2. Run the following command:

```bash
meltano add extractor tap-mongodb
```

If you are successful, you should see `Added and installed extractors 'tap-mongodb'` in your terminal.

#### Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

```bash
# MongoDB databse host URI
export MONGODB_HOST=""
# MongoDB database port
export MONGODB_PORT=""
# MongoDB database username
export MONGODB_USERNAME=""
# MongoDB database password
export MONGODB_PASSWORD=""
# MongoDB database name
export MONGODB_DBNAME=""
```

### Salesforce

`tap-salesforce` is an extractor that pulls data from a Salesforce database and produced JSON-formatted data following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

#### Info

- **Data Source**: [Salesforce](https://www.salesforce.com/)
- **Repository**: [https://gitlab.com/meltano/tap-salesforce](https://gitlab.com/meltano/tap-salesforce)

#### Install

1. Navigate to your Meltano project in the terminal
2. Run the following command:

```bash
meltano add extractor tap-salesforce
```

If you are successful, you should see `Added and installed extractors 'tap-salesforce'` in your terminal.

#### Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

```bash
export SFDC_CLIENT_ID="yourSalesforceClientId"
export SFDC_PASSWORD="yourSalesforcePassword"
export SFDC_SECURITY_TOKEN="yourSalesforceSecurityToken"
export SFDC_START_DATE="yourSalesforceStartDate"
export SFDC_USERNAME="yourSalesforceUsername"
```

### Stripe

`tap-stripe` is an extractor that pulls data from Stripe's API and produces JSON-formatted data following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

#### Info

- **Data Source**: [Stripe's API](https://stripe.com/docs/api)
- **Repository**: [https://github.com/meltano/tap-stripe](https://github.com/meltano/tap-stripe)

#### Install

1. Navigate to your Meltano project in the terminal
2. Run the following command:

```bash
meltano add extractor tap-stripe
```

If you are successful, you should see `Added and installed extractors 'tap-stripe'` in your terminal.

#### Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

```bash
export STRIPE_API_KEY="yourStripeApiKey"
# The date uses ISO-8601 and supports time if desired
export STRIPE_START_DATE="YYYY-MM-DD"
```

### Zendesk

`tap-zendesk` is an extractor that pulls data from a Zendesk REST API and produces JSON-formatted data following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

#### Info

- **Data Source**: [Zendesk REST API](https://developer.zendesk.com/rest_api)
- **Repository**: [https://github.com/meltano/tap-zendesk](https://github.com/meltano/tap-zendesk)

#### Install

1. Navigate to your Meltano project in the terminal
2. Run the following command:

```bash
meltano add extractor tap-zendesk
```

If you are successful, you should see `Added and installed extractors 'tap-zendesk'` in your terminal.

#### Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

```bash
export ZENDESK_EMAIL="yourZendeskEmail"
export ZENDESK_API_TOKEN="yourZendeskApiToken"
export ZENDESK_SUBDOMAIN="yourZendeskSubdomain"
# The date uses ISO-8601 and supports time if desired
export ZENDESK_START_DATE="yourZendeskStartDate"
```

### Zuora

`tap-zuora` is an extractor that pulls data from a Zuora REST API and produces JSON-formatted data following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

#### Info

- **Data Source**: [Zuora REST API](https://www.zuora.com/developer/API-Reference/)
- **Repository**: [https://github.com/singer-io/tap-zuora](https://github.com/singer-io/tap-zuora)

#### Install

1. Navigate to your Meltano project in the terminal
2. Run the following command:

```bash
meltano add extractor tap-zuora
```

If you are successful, you should see `Added and installed extractors 'tap-zuora'` in your terminal.

#### Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

```bash
export ZUORA_USERNAME=""
export ZUORA_PASSWORD=""
export ZUORA_API_TOKEN=""   # preferred to ZUORA_PASSWORD
export ZUORA_API_TYPE=""    # specifically 'REST' or 'AQuA'
export ZUORA_PARTNER_ID=""  # optional, only for the 'AQuA` API type
export ZUORA_START_DATE=""
export ZUORA_SANDBOX=""     # specifically 'true' or 'false'
```

## Loaders

A loader is a component for the bulk import of data. Currently, Meltano supports [Singer.io](https://singer.io) targets as loaders.

### CSV

`target-csv` is a loader that works with other extractors in order to move data into CSV-formatted files. 

#### Info

- **Data Warehouse**: CSV Files
- **Repository**: [https://gitlab.com/meltano/target-csv](https://gitlab.com/meltano/target-csv)

#### Install

1. Navigate to your Meltano project in the terminal
2. Run the following command:

```bash
meltano add loader target-csv
```

If you are successful, you should see `Added and installed loaders 'target-csv'` in your terminal.

#### Configuration

If you want to customize your delimited or quote character, open `meltano.yml` for your desired project and update the configuration there.

```yaml{1-3}
  - config:
      delimiter": "\t"
      quotechar": ''''
    name: target-csv
    pip_url: git+https://gitlab.com/meltano/target-csv.git
```

### Snowflake

`target-snowflake` is a loader that works with other extractors in order to move data into a Snowflake database. 

::: warning
Please note that querying in the Meltano UI is not supported, yet.
You can follow the progress on this feature in this issue: [meltano/meltano#428](https://gitlab.com/meltano/meltano/issues/428)
:::

#### Info

- **Data Warehouse**: [Snowflake](https://www.snowflake.com/)
- **Repository**: [https://gitlab.com/meltano/target-snowflake](https://gitlab.com/meltano/target-snowflake)

#### Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

```bash
export SF_ACCOUNT=""
export SF_USER=""
export SF_PASSWORD=""
export SF_ROLE=""       # in UPPERCASE
export SF_DATABASE=""   # in UPPERCASE
export SF_WAREHOUSE=""  # in UPPERCASE
```

### Postgres

`target-postgres` is a loader that works with other extractors in order to move data into a Postgres database. 

#### Info

- **Data Warehouse**: [Postgres](https://www.postgresql.org/)
- **Repository**: [https://github.com/meltano/target-postgres](https://github.com/meltano/target-postgres)

#### Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

```bash
export PG_ADDRESS=""
export PG_USERNAME=""
export PG_PORT=""
export PG_PASSWORD=""
export PG_DATABASE=""
export PG_SCHEMA=""
```

### Sqlite

`target-sqlite` is a loader that works with other extractors in order to move data into a SQLite database. 

#### Info

- **Data Warehouse**: [SQLite](https://sqlite.org/)
- **Repository**: [https://gitlab.com/meltano/target-sqlite](https://gitlab.com/meltano/target-sqlite)

#### Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

```bash
export SQLITE_DATABASE=""
```