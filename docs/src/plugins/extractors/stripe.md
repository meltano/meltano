---
sidebar: auto
description: Use Meltano to pull data from the Stripe API and load it into Snowflake, PostgreSQL, and more
---

# Stripe

The `tap-stripe` [extractor](https://hub.meltano.com/extractors/) pulls data from the [Stripe API](https://stripe.com/docs/api).

- **Repository**: <https://github.com/meltano/tap-stripe>
- **Maintainer**: Meltano community
- **Maintenance status**: Active

## Getting Started

### Prerequisites

If you haven't already, follow the initial steps of the [Getting Started guide](/docs/getting-started.html):

1. [Install Meltano](/docs/getting-started.html#install-meltano)
1. [Create your Meltano project](/docs/getting-started.html#create-your-meltano-project)

### Installation and configuration

#### Using the Command Line Interface

1. Add the `tap-stripe` extractor to your project using [`meltano add`](/docs/command-line-interface.html#add):

    ```bash
    meltano add extractor tap-stripe
    ```

1. Configure the [settings](#settings) below using [`meltano config`](/docs/command-line-interface.html#config).

#### Using Meltano UI

1. Start [Meltano UI](/docs/ui.html) using [`meltano ui`](/docs/command-line-interface.html#ui):

    ```bash
    meltano ui
    ```

1. Open the Extractors interface at <http://localhost:5000/extractors>.
1. Click the "Add to project" button for "Stripe".
1. Configure the [settings](#settings) below in the "Configuration" interface that opens automatically.

### Next steps

Follow the remaining steps of the [Getting Started guide](/docs/getting-started.html):

1. [Select entities and attributes to extract](/docs/getting-started.html#select-entities-and-attributes-to-extract)
1. [Add a loader to send data to a destination](/docs/getting-started.html#add-a-loader-to-send-data-to-a-destination)
1. [Run a data integration (EL) pipeline](/docs/getting-started.html#run-a-data-integration-el-pipeline)

If you run into any issues, [learn how to get help](/docs/getting-help.html).

## Settings

`tap-stripe` requires the [configuration](/docs/configuration.html) of the following settings:

- [Account ID](#account-id)
- [Client Secret](#client-secret)
- [Start Date](#start-date)

These and other supported settings are documented below.
To quickly find the setting you're looking for, use the Table of Contents in the sidebar.

#### Minimal configuration

A minimal configuration of `tap-stripe` in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) will look like this:

```yml{5-7}
plugins:
  extractors:
  - name: tap-stripe
    variant: meltano
    config:
      account_id: acct_1a2b3c4d5e
      start_date: '2020-10-01T00:00:00Z'
```

Sensitive values are most appropriately stored in [the environment](/docs/configuration.html#configuring-settings) or your project's [`.env` file](/docs/project.html#env):

```bash
export TAP_STRIPE_CLIENT_SECRET=sk_live_1a2b3c4d5e
```

### Account ID

- Name: `account_id`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_STRIPE_ACCOUNT_ID`, alias: `STRIPE_ACCOUNT_ID`

#### How to get

To get your account ID:

1. Visit your profile: [https://dashboard.stripe.com/settings/user](https://dashboard.stripe.com/settings/user)

   - Or in the upper right, click on the avatar to access a dropdown, and click on `Profile`

![Screenshot of what the avatar dropdown with Profile looks like](/images/tap-stripe/01-stripe-docs.png)

2. Once the page loads, scroll to the bottom to find your account ID in the section labelled `Accounts`

![Screenshot of account ID](/images/tap-stripe/02-stripe-docs.png)

3. Copy and paste it somewhere you can refer later on when configuring the tap.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-stripe set account_id <id>

export TAP_STRIPE_ACCOUNT_ID=<id>
```

### Client Secret

- Name: `client_secret`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_STRIPE_CLIENT_SECRET`, alias: `STRIPE_API_KEY`

Secret API Key

#### How to get

To get your secret API key:

1. Visit your Developer API Keys page: [https://dashboard.stripe.com/apikeys](https://dashboard.stripe.com/apikeys)

   - You can find this by clicking on the `Developers` link on the left navigation and clicking on `API Keys`

![Screeenshot of where the Developers link is on the left side](/images/tap-stripe/03-stripe-docs.png)

2. Under the `Standard keys` section, click on the button to `Create secret key`

:::tip No button?

If the "Create secret key" button is not available, a secret key may already have been generated before.
In this case, use the "Reveal live key token" button under "Token" and to the right of "Secret key". The token that appears is the secret key you can copy and paste into the data source configuration.

:::

![Screenshot of where Create secret key button is](/images/tap-stripe/04-stripe-docs.png)

3. To make things easy to track, assign the secret key a name of `Meltano` so you know why you created the key

![Screenshot of naming secret key](/images/tap-stripe/05-stripe-docs.png)

4. Once you click on `Create`, you should be greeted with you new API key which you'll copy and paste into the data source configuration.

![Screenshot of the new API key](/images/tap-stripe/06-stripe-docs.png)

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-stripe set client_secret <secret>

export TAP_STRIPE_CLIENT_SECRET=<secret>
```

### Start Date

- Name: `start_date`
- [Environment variable](/docs/configuration.html#configuring-settings): `TAP_STRIPE_START_DATE`

This property determines how much historical data will be extracted.

Please be aware that the larger the time period and amount of data, the longer the initial extraction can be expected to take.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config tap-stripe set start_date YYYY-MM-DDTHH:MM:SSZ

export TAP_STRIPE_START_DATE=YYYY-MM-DDTHH:MM:SSZ

# For example:
meltano config tap-stripe set start_date 2020-10-01T00:00:00Z

export TAP_STRIPE_START_DATE=2020-10-01T00:00:00Z
```
