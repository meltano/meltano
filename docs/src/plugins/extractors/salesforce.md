---
sidebar: auto
metaTitle: Extract Data from Salesforce
description: Use Meltano to extract raw data from Salesforce and insert it into Postgres, Snowflake, and more.
---

# Salesforce

The Salesforce extractor pulls raw data from Salesforce's [REST API](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_what_is_rest_api.htm) and extracts the following resources by default:

- Users
- Accounts
- Leads
- Opportunities
- Contacts

For more information you can check [the documentation for tap-salesforce](https://gitlab.com/meltano/tap-salesforce).

## Salesforce Setup

In order to access your Stripe data, you will need:

- User Name
- Password
- Security Token
- Start Date

<h3 id="username">User Name</h3>

:::tip Configuration Notes

- The user name used to sign in to your Salesforce account

:::

### Password

:::tip Configuration Notes

- The password used to sign in to your Salesforce account

:::

### Security Token

:::tip Configuration Notes

- Access to Salesforce's API requires a security token that will authenticate you with the server

:::

If you don't already have a Salesforce Security Token for your account, you can generate one through the following steps:

1. Sign in to your [Salesforce Account](https://login.salesforce.com/).

1. Go to your Account Settings (top right on the header bar)

1. Click `Reset My Security Token` (Under the `My Personal Information` section)

1. Click `Reset Security Token`

An email with the Security Token will be sent to your email.

![Screenshot of Salesforce Security Token Reset](/images/salesforce/01-salesforce-reset-security-token.png)

::: tip

**Why is my "Reset Security Token" option missing?**

If a user’s profile is configured such that there is a restriction on the IP ranges that can access Salesforce, then that user will not have the ability to access/reset their security token.

In order to give access to the security token, either remove the user from the profile that contains the IP range restriction, or update the user’s profile by removing the IP range restriction.

In rare cases where the user’s profile doesn’t contain IP range restriction and they still can’t access the security token reset option, edit the user’s profile and save (without making any actual changes to the profile).

:::

::: tip

When you reset your Salesforce password, your security token resets as well. If that security token is used to integrate Meltano with Salesforce, that integration will break as well. Each time you reset an account password used to connect Meltano or other applications to Salesforce, you will need to re-enter your new security token into that application.

:::

::: warning

If you have other third-party applications integrated with Salesforce and you reset your security token, that integration will break. Try to use your existing Security Token instead of resetting your existing one. Otherwise, you will need to re-enter your new security token into all the connected applications.

:::

### Start Date

:::tip Configuration Notes

- Determines how much historical data will be extracted. Please be aware that the larger the time period and amount of data, the longer the initial extraction can be expected to take.

:::

This property allows you to configure where you want your data set to start from. Otherwise, if left blank, it will try to fetch the entire history of the groups or projects specified.

## Meltano Setup

### Prerequisites

- [Running instance of Meltano](/docs/getting-started.html)

### Configure the Extractor

Open your Meltano instance and click "Pipelines" in the top navigation bar. You should now see the Extractors page, which contains various options for connecting your data sources.

![Screenshot of Meltano UI with all extractors not installed and Salesforce Extractor highlighted](/images/salesforce-tutorial/01-salesforce-extractor-selection.png)

Let's install `tap-salesforce` by clicking on the `Install` button inside its card.

On the configuration modal we want to enter your username and password, the Security Token Salesforce extractor will use to connect to Salesforce, and the Start Date we want the extracted data set to start from.

![Screenshot of Salesforce Extractor Configuration](/images/salesforce-tutorial/02-salesforce-configuration.png)

::: tip

**Ready to do more with data from Salesforce?**

Check out our [Salesforce API + Postgres tutorial](/tutorials/salesforce-and-postgres.html) to learn how you can create an analytics database from within Meltano, and start analyzing your Salesforce data.

:::

## Advanced: Command Line Installation

1. Navigate to your Meltano project in the terminal
2. Run the following command:

```bash
meltano add extractor tap-salesforce
```

If you are successful, you should see `Added and installed extractors 'tap-salesforce'` in your terminal.

## Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

```bash
export TAP_SALESFORCE_USERNAME="Your Salesforce Username"
export TAP_SALESFORCE_PASSWORD="Your Salesforce Password"
export TAP_SALESFORCE_SECURITY_TOKEN="Your Salesforce Security Token"
export TAP_SALESFORCE_START_DATE="2018-01-01T00:00:00Z"
```
