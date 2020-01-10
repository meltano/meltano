---
sidebar: auto
metaTitle: Extract Data from Fastly
description: Use Meltano to extract raw data from Fastly and insert it into Postgres, Snowflake, and more.
---

# Fastly

`tap-fastly` pulls raw data from Fastly and produces JSON-formatted data per the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

## Fastly Setup

In order to access your Fastly data, you will need:

- API Token
- Start Date

### API Token

:::tip Configuration Notes

- Full access to Fastly's API requires an API Token that will authenticate you with the server

:::

### Start Date

:::tip Configuration Notes

- Determines how much historical data will be extracted. Please be aware that the larger the time period and amount of data, the longer the initial extraction can be expected to take

:::

## Info

- **Data Source**: [Fastly](https://www.fastly.com/)
- **Repository**: [https://gitlab.com/meltano/tap-fastly](https://gitlab.com/meltano/tap-fastly)

## Advanced: Command Line Installation

1. Navigate to your Meltano project in the terminal
2. Run the following command:

```bash
meltano add extractor tap-fastly
```

If you are successful, you should see `Added and installed extractors 'tap-fastly'` in your terminal.

## Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

```bash
export TAP_FASTLY_API_TOKEN="yourFastlyApiToken"
# The date uses ISO-8601 and supports time if desired
export TAP_FASTLY_START_DATE="YYYY-MM-DD"
```
