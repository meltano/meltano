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

In order for the Salesforce extractor to be able to access your Salesforce data, you will need to provide your username, password and the Salesforce Security Token for your account. 

If you don't already have a Salesforce Security Token for your account, you can generate one through the following steps:

1. Sign in to your [Salesforce Account](https://login.salesforce.com/).

1. Go to your Account Settings (top right on the header bar)

1. Click `Reset My Security Token` (Under the `My Personal Information` section)

1. Click `Reset Security Token` 

An email with the Security Token will be sent to your email.

![Screenshot of Salesforce Security Token Reset](/images/salesforce/01-salesforce-reset-security-token.png)


## Meltano Setup

### Prerequisites

* [Running instance of Meltano](/docs/getting-started.html)

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
