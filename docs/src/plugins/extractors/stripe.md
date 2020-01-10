---
sidebar: auto
metaTitle: Extract Data from Stripe
description: Use Meltano to extract raw data from Stripe and insert it into Postgres, Snowflake, and more.
---

# Stripe

`tap-stripe` is an extractor that pulls data from Stripe's API and produces JSON-formatted data following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

<YouTubeEmbed src="https://www.youtube.com/embed/Qp-EgNP6Pjw" />

## Stripe Setup

In order to access your Stripe data, you will need:

- Account ID
- Client Secret
- Start Date

### Account ID

:::tip Configuration Notes

- The account ID (e.g., `acct_152Bdedkol54`) attained from your Stripe account profile

:::

To get your account ID:

1. Visit your profile: [https://dashboard.stripe.com/settings/user](https://dashboard.stripe.com/settings/user)

   - Or in the upper right, click on the avatar to access a dropdown, and click on `Profile`

![Screenshot of what the avatar dropdown with Profile looks like](/images/tap-stripe/01-stripe-docs.png)

2. Once the page loads, scroll to the bottom to find your account ID in the section labelled `Accounts`

![Screenshot of account ID](/images/tap-stripe/02-stripe-docs.png)

3. Copy and paste it somewhere you can refer later on when configuring the tap.

### Client Secret

:::tip Configuration Notes

- The client secret (e.g., `sk_live_eis72wonf921pqjdf`) is accessible in your Stripe account when signed in

:::

To get your client secret:

1. Visit your Developer API Keys page: [https://dashboard.stripe.com/apikeys](https://dashboard.stripe.com/apikeys)

   - You can find this by clicking on the `Developers` link on the left navigation and clicking on `API Keys`

![Screeenshot of where the Developers link is on the left side](/images/tap-stripe/03-stripe-docs.png)

2. Under the `Standard keys` section, click on the button to `Create secret key`

![Screenshot of where Create secret key button is](/images/tap-stripe/04-stripe-docs.png)

3. To make things easy to track, assign the secret key a name of `Meltano` so you know why you created the key

![Screenshot of naming secret key](/images/tap-stripe/05-stripe-docs.png)

4. Once you click on `Create`, you should be greeted with you new API key which you'll copy and paste into the tap configuration.

![Screenshot of the new API key](/images/tap-stripe/06-stripe-docs.png)

### Start Date

:::tip Configuration Notes

- Determines how much historical data will be extracted. Please be aware that the larger the time period and amount of data, the longer the initial extraction can be expected to take.

:::

This property allows you to configure where you want your data set to start from. Otherwise, if left blank, it will try to fetch the entire history of the groups or projects specified.

#### Web Application

1. On `Pipeline: Extract` page, find the `Zendesk` card and click on `Install`
1. When it is complete, you should see the following modal

![Screenshot of tap-stripe modal](/images/tap-stripe/07-stripe-docs.png)

3. Fill out the form with your [account ID](/plugins/extractors/stripe.html#account-id) and [secret key](/plugins/extractors/stripe.html#secret-key)
1. Click `Test Connection` to make sure that everything works correctly
1. Click `Save` to finish installation!

## Advanced: Command Line Installation

1. Navigate to your Meltano project in the terminal
2. Run the following command:

```bash
meltano add extractor tap-stripe
```

If you are successful, you should see `Added and installed extractors 'tap-stripe'` in your terminal.

### Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

```bash
# Can be found in your Profile
export STRIPE_ACCOUNT_ID="yourAccountId"
# Create a new secret key for Meltano
export STRIPE_API_KEY="yourStripeApiKey"
# The date uses ISO-8601 and supports time if desired
export TAP_STRIPE_START_DATE="YYYY-MM-DD"
```

## Additional Information

- **Data Source**: [Stripe's API](https://stripe.com/docs/api)
- **Repository**: [https://github.com/meltano/tap-stripe](https://github.com/meltano/tap-stripe)
