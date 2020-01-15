---
sidebar: auto
metaTitle: Extract Facebook Ads Data
description: Use Meltano to extract Facebook Ads data from the Facebook Marketing API and insert it into Postgres, Snowflake, and more.
---

# Facebook Ads

The Facebook Ads extractor pulls raw data from the [Facebook Marketing API](https://developers.facebook.com/docs/marketing-apis) and extracts the following resources from a Facebook Ads account:

- Ad Creatives
- Ads
- Ad Sets
- Campaigns
- Ads Insights
  - Breakdown by age and gender
  - Breakdown by country
  - Breakdown by placement and device

For more information you can check [the documentation for tap-facebook](https://gitlab.com/meltano/tap-facebook).

## Facebook Ads Setup

In order to access your Facebook Ads data, you will need the following:

- Account ID
- Access Token
- Start Date
- End Date

<h3 id="account-id">Account ID</h3>

Your Facebook Ads Account ID.

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

<h3 id="access-token">Access Token</h3>

#### Create App

First, you will need to create a Facebook App trough the Developer Portal.

1. Go to <https://developers.facebook.com/>.
2. Log into Facebook if you haven't already. Make sure that your account is an Admin of the Ads Account you will be pulling data from.
3. Convert your Facebook account to a Developer Account if you haven't done so already. This will not affect your personal Facebook profile, but will give you access to Facebook's developer tools.
4. Click "My Apps" in the top right, and choose "Create App".
5. In the modal that appears, enter a "Display Name" of your choosing. Since you will only use this app to generate an Access Token for your own use, the actual display name does not matter too much.
6. Enter your email address under "Contact Email" if it is not yet populated automatically.
7. Click "Create App ID".

![Screenshot of "Create A New App ID" modal](/images/tap-facebook/create-new-app-id.png)

8. Under "Add a Product", find "Marketing API", and click "Set Up".

#### Generate Access Token

Now that your app has been created and the Marketing API product has been enabled, we can generate an access token.

1. In the sidebar on the left, expand "Marketing API" if it isn't expanded already.
2. Under "Marketing API", click "Tools".
3. Select `ads_management`, `ads_read`, and `manage_pages` under "Select Token Permissions".
4. Click "Get Token".
5. Copy the token that appears in the field.

![Screenshot of "Get Access Token" section](/images/tap-facebook/get-access-token.png)

This is the Access Token you will provide to Meltano.

#### Token Expiration

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

<h3 id="start-date">Start Date</h3>

This property allows you to configure where you want your extracted data set to start from. 

:::tip Configuration Notes

- Determines how much historical data will be extracted.
- Please be aware that the larger the time period and amount of data, the longer the initial extraction can be expected to take.

:::

<h3 id="end-date">End Date</h3>

This property allows you to configure where you want your extracted data set to end. Otherwise, if left blank, it will try to fetch all the Ads data from the Start Date until the date you run the Extractor.

## Meltano Setup

### Prerequisites

- [Running instance of Meltano](/docs/getting-started.html)

### Configure the Extractor

Open your Meltano instance and click "Pipelines" in the top navigation bar. You should now see the Extractors page, which contains various options for connecting your data sources.

![Screenshot of Meltano UI with all extractors not installed and Facebook Ads Extractor highlighted](/images/facebook-tutorial/01-facebook-extractor-selection.png)

Let's install the Facebook Ads Extractor by clicking on the `Install` button inside its card.

On the configuration modal we want to enter the Account ID and Access Token that Facebook Ads extractor will use to connect to the Facebook Marketing API, the Start Date we want the extracted data set to start from and the End Date.

![Screenshot of the Facebook Ads Extractor Configuration](/images/facebook-tutorial/02-facebook-configuration.png)


## Advanced: Command Line Installation

1. Navigate to your Meltano project in the terminal
1. Run the following command:

```bash
meltano add extractor tap-facebook
```

If you are successful, you should see `Added and installed extractors 'tap-facebook'` in your terminal.

### Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

Required:

```bash
export TAP_FACEBOOK_ACCOUNT_ID="123456789012345"
export TAP_FACEBOOK_ACCESS_TOKEN="YOUR ACCESS TOKEN"
export TAP_FACEBOOK_START_DATE="2019-12-01T00:00:00Z"
```

Optional:

```bash
export TAP_FACEBOOK_END_DATE="2019-12-31T00:00:00Z"
export TAP_FACEBOOK_INSIGHTS_BUFFER_DAYS=0
```

If `TAP_FACEBOOK_INSIGHTS_BUFFER_DAYS` sets how many days to start extracting Ads Insights before the **start_date** (default: 0)

Check the [README](https://gitlab.com/meltano/tap-facebook) for more details.
