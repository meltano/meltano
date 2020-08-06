---
sidebar: auto
metaTitle: Extract Data from Marketo
description: Use Meltano to extract raw data from Marketo and insert it into Postgres, Snowflake, and more.
---

# Marketo

`tap-marketo` pulls raw data from Marketo's REST API and extracts activity types, activites, and leads from Marketo.

## Info

- **Data Source**: [Marketo's REST API](http://developers.marketo.com/rest-api/)
- **Repository**: [https://gitlab.com/meltano/tap-marketo](https://gitlab.com/meltano/tap-marketo)

## Install

1. Navigate to your Meltano project in the terminal
2. Run the following command:

```shell
meltano add extractor tap-marketo
```

If you are successful, you should see `Added and installed extractors 'tap-marketo'` in your terminal.

## Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

```shell
export TAP_MARKETO_CLIENT_ID="Your Client Id"
export TAP_MARKETO_CLIENT_SECRET="Your Client Secret"
export TAP_MARKETO_ENDPOINT="Your Endpoint Url"
export TAP_MARKETO_IDENTITY="Your Identity"
export TAP_MARKETO_START_DATE="2019-01-01T00:00:00Z"
```
