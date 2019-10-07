---
sidebar: auto
---

# Google Analytics

`tap-google-analytics` pulls raw data from the Google Analytics Reporting APIv4.

## Info

- **Data Source**: [Google Analytics Reporting APIv4](https://developers.google.com/analytics/devguides/reporting/core/v4/)
- **Repository**: [https://gitlab.com/meltano/tap-google-analytics](https://gitlab.com/meltano/tap-google-analytics)

## Install

1. Navigate to your Meltano project in the terminal
2. Run the following command:

```bash
meltano add extractor tap-google-analytics
```

If you are successful, you should see `Added and installed extractors 'tap-google-analytics'` in your terminal.

## Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

Required:

```bash
export GOOGLE_ANALYTICS_API_CLIENT_SECRETS="client_secrets.json"
export GOOGLE_ANALYTICS_API_VIEW_ID="YOUR VIEW ID"
export GOOGLE_ANALYTICS_API_START_DATE="2019-02-01T00:00:00Z"
```

Optional:

```bash
export GOOGLE_ANALYTICS_API_REPORTS="cli_reports.json"
export GOOGLE_ANALYTICS_API_END_DATE="2019-06-01T00:00:00Z"
```

Check the [README](https://gitlab.com/meltano/tap-google-analytics#tap-google-analytics) for details.
