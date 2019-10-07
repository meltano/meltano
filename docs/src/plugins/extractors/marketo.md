---
sidebar: auto
---

# Marketo

`tap-marketo` pulls raw data from Marketo's REST API and extracts activity types, activites, and leads from Marketo.

## Info

- **Data Source**: [Marketo's REST API](http://developers.marketo.com/rest-api/)
- **Repository**: [https://gitlab.com/meltano/tap-marketo](https://gitlab.com/meltano/tap-marketo)

## Install

1. Navigate to your Meltano project in the terminal
2. Run the following command:

```bash
meltano add extractor tap-marketo
```

If you are successful, you should see `Added and installed extractors 'tap-marketo'` in your terminal.

## Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

```bash
export TAP_MARKETO_CLIENT_ID="yourClientId"
export TAP_MARKETO_CLIENT_SECRET="yourClientSecret"
export TAP_MARKETO_ENDPOINT="yourEndpointUrl"
export TAP_MARKETO_IDENTITY="yourIdentity"
export TAP_MARKETO_START_TIME="yourStartTime"
```
