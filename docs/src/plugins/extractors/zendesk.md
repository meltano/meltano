---
sidebar: auto
metaTitle: Extract Data from Zendesk
description: Use Meltano to extract raw data from Zendesk and insert it into Postgres, Snowflake, and more. 
---

# Zendesk

`tap-zendesk` is an extractor that pulls data from a Zendesk REST API and produces JSON-formatted data following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

## Info

- **Data Source**: [Zendesk REST API](https://developer.zendesk.com/rest_api)
- **Repository**: [https://github.com/meltano/tap-zendesk](https://github.com/meltano/tap-zendesk)

## Install

1. Navigate to your Meltano project in the terminal
2. Run the following command:

```bash
meltano add extractor tap-zendesk
```

If you are successful, you should see `Added and installed extractors 'tap-zendesk'` in your terminal.

## Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

```bash
export TAP_ZENDESK_EMAIL="yourZendeskEmail"
export TAP_ZENDESK_API_TOKEN="yourZendeskApiToken"
export TAP_ZENDESK_SUBDOMAIN="yourZendeskSubdomain"
# The date uses ISO-8601 and supports time if desired
export TAP_ZENDESK_START_DATE="yourZendeskStartDate"
```
