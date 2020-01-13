---
sidebar: auto
metaTitle: Extract Data from Zendesk
description: Use Meltano to extract raw data from Zendesk and insert it into Postgres, Snowflake, and more.
---

# Zendesk

`tap-zendesk` is an extractor that pulls data from a Zendesk REST API and produces JSON-formatted data following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

## Getting Started

### Prerequisites

In order to use `tap-zendesk`, you need to three key pieces of information that will allow the Meltano application to fetch data.

1. Account email (e.g., `hello@meltano.com`)
1. API key (e.g., `oz3M12Xdtlrkj38efLkOzHI9GhkJxrquuw`)
1. Zendesk Subdomain (e.g., `meltano` from `meltano.zendesk.com`)

#### Account Email

This is the email you use to login to your Zendesk dashboard.

#### API Key

1. Login to your Zendesk dashboard.

![Screenshot of sample Zendesk dashboard](/images/tap-zendesk/01-zendesk-docs.png)

2. On the left navigation, scroll down to the `Channels` section to click on the `API` link. If you don't see this, your account does not have adequate permissions.

![Screenshot of left nav with API link](/images/tap-zendesk/02-zendesk-docs.png)

3. Ensure that `Token Access` is enabled

4. Click on the `+` button to create a new API token

![Screenshot of new API token creation](/images/tap-zendesk/03-zendesk-docs.png)

5. Add `Meltano` as the API Token Description

6. Copy the API token since it will not be shown again

7. Click `Save` button to complete API key creation

#### Zendesk Subdomain

When visiting your Zendesk instance, the URL is structured as follows:

```
SUBDOMAIN.zendesk.com
```

You'll need this subdomain when configuring the extractor.

For example, if the URL is `meltano.zendesk.com`, then the subdomain is `meltano`.

### Install

#### Web Application

1. On `Pipeline: Extract` page, find the `Zendesk` card and click on `Install`
1. When it is complete, you should see the following modal

![Screenshot of tap-zendesk modal](/images/tap-zendesk/04-zendesk-docs.png)

3. Fill out the form with your [account email](/plugins/extractors/zendesk.html#account-email), [secret key](/plugins/extractors/zendesk.html#api-key) and [Zendesk subdomain](/plugins/extractors/zendesk.html#zendesk-subdomain)
1. Click `Test Connection` to make sure that everything works correctly
1. Click `Save` to finish installation!

#### Command Line Interface

1. Navigate to your Meltano project in the terminal
2. Run the following command:

```bash
meltano add extractor tap-zendesk
```

If you are successful, you should see `Added and installed extractors 'tap-zendesk'` in your terminal.

### Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

```bash
export TAP_ZENDESK_EMAIL="yourZendeskEmail"
export TAP_ZENDESK_API_TOKEN="yourZendeskApiToken"
export TAP_ZENDESK_SUBDOMAIN="yourZendeskSubdomain"
# The date uses ISO-8601 and supports time if desired
export TAP_ZENDESK_START_DATE="yourZendeskStartDate"
```

## Additional Information

- **Data Source**: [Zendesk REST API](https://developer.zendesk.com/rest_api)
- **Repository**: [https://github.com/meltano/tap-zendesk](https://github.com/meltano/tap-zendesk)
