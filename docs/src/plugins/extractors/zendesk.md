---
sidebar: auto
metaTitle: Extract Data from Zendesk
description: Use Meltano to extract raw data from Zendesk and insert it into Postgres, Snowflake, and more.
---

# Zendesk

`tap-zendesk` is an extractor that pulls data from a Zendesk REST API and produces JSON-formatted data following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

<YouTubeEmbed src="https://www.youtube.com/embed/bUnY-7Azhcc" />

## Zendesk Setup

In order to access your Zendesk data, you will need:

- Email
- API Token
- Zendesk Subdomain
- Start Date

### Email

:::tip Configuration Notes

- The Email (e.g., `hello@meltano.com`) used to sign in to your Zendesk account

:::

This is the email you use to login to your Zendesk dashboard.

### API Token

:::tip Configuration Notes

- The API Token (e.g., `oz3M12Xdtlrkj38efLkOzHI9GhkJxrquuw`) accessible via your Zendesk account when signed in

:::

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

<h3 id="subdomain">Zendesk Subdomain</h3>

:::tip Configuration Notes

- The subdomain you access when using Zendesk

:::

### Zendesk Subdomain

:::tip Configuration Notes

- If the URL is `meltano.zendesk.com`, then the subdomain is `meltano`.

:::

When visiting your Zendesk instance, the URL is structured as follows:

```
SUBDOMAIN.zendesk.com
```

You'll need this subdomain when configuring the extractor.

For example, if the URL is `meltano.zendesk.com`, then the subdomain is `meltano`.

### Start Date

:::tip Configuration Notes

- Determines how much historical data will be extracted. Please be aware that the larger the time period and amount of data, the longer the initial extraction can be expected to take.

:::

This property allows you to configure where you want your data set to start from. Otherwise, if left blank, it will try to fetch the entire history of the groups or projects specified.

## Web Application

1. On `Pipeline: Extract` page, find the `Zendesk` card and click on `Install`
1. When it is complete, you should see the following modal

![Screenshot of tap-zendesk modal](/images/tap-zendesk/04-zendesk-docs.png)

3. Fill out the form with your [account email](/plugins/extractors/zendesk.html#account-email), [secret key](/plugins/extractors/zendesk.html#api-key) and [Zendesk subdomain](/plugins/extractors/zendesk.html#zendesk-subdomain)
1. Click `Test Connection` to make sure that everything works correctly
1. Click `Save` to finish installation!

## Advanced: Command Line Installation

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
