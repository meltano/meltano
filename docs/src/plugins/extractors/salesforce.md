---
sidebar: auto
metaTitle: Extract Data from Salesforce
description: Use Meltano to extract raw data from Salesforce and insert it into Postgres, Snowflake, and more. 
---

# Salesforce

`tap-salesforce` is an extractor that pulls data from a Salesforce database and produced JSON-formatted data following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

## Info

- **Data Source**: [Salesforce](https://www.salesforce.com/)
- **Repository**: [https://gitlab.com/meltano/tap-salesforce](https://gitlab.com/meltano/tap-salesforce)

## Install

1. Navigate to your Meltano project in the terminal
2. Run the following command:

```bash
meltano add extractor tap-salesforce
```

If you are successful, you should see `Added and installed extractors 'tap-salesforce'` in your terminal.

## Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

```bash
export TAP_SALESFORCE_CLIENT_ID="yourSalesforceClientId"
export TAP_SALESFORCE_PASSWORD="yourSalesforcePassword"
export TAP_SALESFORCE_SECURITY_TOKEN="yourSalesforceSecurityToken"
export TAP_SALESFORCE_START_DATE="yourSalesforceStartDate"
export TAP_SALESFORCE_USERNAME="yourSalesforceUsername"
```
