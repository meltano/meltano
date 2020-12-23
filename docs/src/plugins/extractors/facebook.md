---
sidebar: auto
description: Use Meltano to pull data from the Facebook Ads API and load it into Snowflake, PostgreSQL, and more
---

# Facebook Ads

The `tap-facebook` [extractor](/plugins/extractors/) pulls data from the [Facebook Ads API](https://developers.facebook.com/docs/marketing-apis).

To learn more about `tap-facebook`, refer to the repository at <https://gitlab.com/meltano/tap-facebook>.

## Getting Started

### Prerequisites

If you haven't already, follow the initial steps of the [Getting Started guide](/docs/getting-started.html):

1. [Install Meltano](/docs/getting-started.html#install-meltano)
1. [Create your Meltano project](/docs/getting-started.html#create-your-meltano-project)

### Installation and configuration

#### Using the Command Line Interface

1. Add the `tap-facebook` extractor to your project using [`meltano add`](/docs/command-line-interface.html#add):

    ```bash
    meltano add extractor tap-facebook
    ```

1. Configure the [settings](#settings) below using [`meltano config`](/docs/command-line-interface.html#config).

#### Using Meltano UI

1. Start [Meltano UI](/docs/ui.html) using [`meltano ui`](/docs/command-line-interface.html#ui):

    ```bash
    meltano ui
    ```

1. Open the Extractors interface at <http://localhost:5000/extractors>.
1. Click the "Add to project" button for "Facebook Ads".
1. Configure the [settings](#settings) below in the "Configuration" interface that opens automatically.

### Next steps

Follow the remaining steps of the [Getting Started guide](/docs/getting-started.html):

1. [Select entities and attributes to extract](/docs/getting-started.html#select-entities-and-attributes-to-extract)
1. [Add a loader to send data to a destination](/docs/getting-started.html#add-a-loader-to-send-data-to-a-destination)
1. [Run a data integration (EL) pipeline](/docs/getting-started.html#run-a-data-integration-el-pipeline)

## Settings

`tap-facebook` requires the [configuration](/docs/configuration.html) of the following settings:

- [Account ID](#account-id)
- [Access Token](#access-token)
- [Start Date](#start-date)

These and other supported settings are documented below.
To quickly find the setting you're looking for, use the Table of Contents in the sidebar.

#### Minimal configuration

A minimal configuration of `tap-facebook` in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) will look like this:

```yml{5-7}
plugins:
  extractors:
  - name: tap-facebook
    variant: meltano
    config:
      account_id: 791728544625001
      start_date: '2020-10-01T00:00:00Z'
```

Sensitive values are most appropriately stored in [the environment](/docs/configuration.html#configuring-settings) or your project's [`.env` file](/docs/project.html#env):

```bash
export TAP_FACEBOOK_ACCESS_TOKEN=my_access_token
```

### Account ID

- Name: `account_id`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_FACEBOOK_ACCOUNT_ID`

Your Facebook Ads Account ID.

#### How to get

To get your Account ID:

1. Visit the Facebook Ads Manager: <https://www.facebook.com/adsmanager/>
2. Log in if you haven't already.
3. Make sure the correct account is selected in the top left corner.

![Screenshot of account selector](/images/tap-facebook/account-selector.png)

4. You will see the Account ID displayed inside the selector. You can also find it in the URL, after `?act=` and ahead of any additional parameters starting with `&`:

Examples:
- URL: `https://www.facebook.com/adsmanager/manage/campaigns?act=593385444078559`

  Account ID: `593385444078559`
- URL: `https://business.facebook.com/adsmanager/manage/campaigns?act=791728544625001&business_id=172253903856261`

  Account ID: `791728544625001`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-facebook set account_id <id>

export TAP_FACEBOOK_ACCOUNT_ID=<id>
```

### Access Token

- Name: `access_token`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_FACEBOOK_ACCESS_TOKEN`

Facebook Marketing API Access Token

#### How to get

##### Create App

First, you will need to create a Facebook App through the Developer Portal.

::: tip Don't feel like going through the Facebook App setup process?

<p>
  <OAuthServiceLink provider="facebook">Connect your Facebook Ads account</OAuthServiceLink> to acquire this token right away.
</p>

Once you authorize Meltano to access your Facebook Ads data, Facebook will generate an access token and provide it to Meltano OAuth Service. The OAuth Service will not store or use the token, and will only display it to you once so that you can copy and paste it into your local Meltano configuration.
:::

1. Go to <https://developers.facebook.com/>.
2. Log into Facebook if you haven't already. Make sure that your account is an Admin of the Ads Account you will be pulling data from.
3. Convert your Facebook account to a Developer Account if you haven't done so already. This will not affect your personal Facebook profile, but will give you access to Facebook's developer tools.
4. Click "My Apps" in the top right, and choose "Create App".
5. In the modal that appears, enter a "Display Name" of your choosing. Since you will only use this app to generate an Access Token for your own use, the actual display name does not matter too much.
6. Enter your email address under "Contact Email" if it is not yet populated automatically.
7. Click "Create App ID".

![Screenshot of "Create A New App ID" modal](/images/tap-facebook/create-new-app-id.png)

8. Under "Add a Product", find "Marketing API", and click "Set Up".

##### Generate Access Token

Now that your app has been created and the Marketing API product has been enabled, we can generate an access token.

1. In the sidebar on the left, expand "Marketing API" if it isn't expanded already.
2. Under "Marketing API", click "Tools".
3. Select `ads_management`, `ads_read`, and `manage_pages` under "Select Token Permissions".
4. Click "Get Token".
5. Copy the token that appears in the field.

![Screenshot of "Get Access Token" section](/images/tap-facebook/get-access-token.png)

This is the Access Token you will provide to Meltano.

##### Token Expiration

Tokens generated using this method are only valid for 60 days by default.
When the token expires, Meltano will no longer be able to automatically update your Facebook Ads data, and you will need to generate a new token and update the extractor configuration.

To find out exactly when this token will expire, you can use the Access Token Debugger:

1. Go to <https://developers.facebook.com/tools/debug/accesstoken/>.
2. Paste the token into the field at the top.
3. Click "Debug" on the right.
4. Look for the value under "Expires".

![Screenshot of the Access Token Debugger](/images/tap-facebook/access-token-debugger.png)

To prevent any interruption of your data pipeline, we recommend that you generate and configure a new token before the currently configured one expires:

1. Go to <https://developers.facebook.com/>
2. Log into Facebook if you haven't already.
3. Click "My Apps" in the top right, and select the app you created earlier.
4. Follow the steps under ["Generate Access Token"](#generate-access-token) above.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-facebook set access_token <token>

export TAP_FACEBOOK_ACCESS_TOKEN=<token>
```

### Start Date

- Name: `start_date`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_FACEBOOK_START_DATE`

This property determines how much historical data will be extracted.

Please be aware that the larger the time period and amount of data, the longer the initial extraction can be expected to take.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-facebook set start_date YYYY-MM-DDTHH:MM:SSZ

export TAP_FACEBOOK_START_DATE=YYYY-MM-DDTHH:MM:SSZ

# For example:
meltano config tap-facebook set start_date 2020-10-01T00:00:00Z

export TAP_FACEBOOK_START_DATE=2020-10-01T00:00:00Z
```

### End Date

- Name: `end_date`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_FACEBOOK_END_DATE`

Date up to when historical data will be extracted.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-facebook set end_date YYYY-MM-DDTHH:MM:SSZ

export TAP_FACEBOOK_END_DATE=YYYY-MM-DDTHH:MM:SSZ

# For example:
meltano config tap-facebook set end_date 2020-10-01T00:00:00Z

export TAP_FACEBOOK_END_DATE=2020-10-01T00:00:00Z
```

### Insights Buffer Days

- Name: `insights_buffer_days`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_FACEBOOK_INSIGHTS_BUFFER_DAYS`
- Default: `0`

How many Days before the Start Date to fetch Ads Insights for

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-facebook set insights_buffer_days 7

export TAP_FACEBOOK_INSIGHTS_BUFFER_DAYS=7
```
