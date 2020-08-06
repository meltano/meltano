---
sidebar: auto
metaTitle: Load Data into Snowflake with Meltano
description: Use Meltano to load data from numerous sources and insert it into Snowflake for easy analysis.
---

# Snowflake Data Warehouse

`target-snowflake` is a loader that works with other extractors in order to move data into a Snowflake database.

::: warning
Please note that querying in the Meltano UI is not supported, yet.
You can follow the progress on this feature in this issue: [meltano/meltano#428](https://gitlab.com/meltano/meltano/issues/428)
:::

## Info

- **Data Warehouse**: [Snowflake](https://www.snowflake.com/)
- **Repository**: [https://gitlab.com/meltano/target-snowflake](https://gitlab.com/meltano/target-snowflake)

## Installing from the Meltano UI

From the Meltano UI, you can [select this Loader in Step 3 of your pipeline configuration](http://localhost:5000/pipelines/loaders).

### Configuration

Once the loader has installed, a modal will appear that'll allow you to configure your Snowflake connection.

## Installing from the Meltano CLI

1. Navigate to your Meltano project in the terminal
2. Run the following command:

```shell
meltano add loader target-snowflake
```

If you are successful, you should see `Added and installed loaders 'target-snowflake'` in your terminal.

### CLI Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

```shell
export SF_ACCOUNT=""
export SF_USER=""
export SF_PASSWORD=""
export SF_ROLE=""       # in UPPERCASE
export SF_DATABASE=""   # in UPPERCASE
export SF_WAREHOUSE=""  # in UPPERCASE
# export SF_SCHEMA=""   # override if the default (see below) is not appropriate
```

- **SF_ACCOUNT** - This is the account name which is derived from the URL. More info can be found on the [Snowflake docs](https://docs.snowflake.net/manuals/user-guide/connecting.html#your-snowflake-account-name-and-url)
- **SF_USER** - This is the username for the user that will be used for loading data
- **SF_PASSWORD** - This is the password for the user that will be used for loading data
- **SF_ROLE** - This is the role you want to use for your account for loading the data
- **SF_DATABASE** - The name of the Snowflake database you want to use
- **SF_WAREHOUSE** - The name of the Snowflake warehouse you want to use
- **SF_SCHEMA** - The name of the Snowflake schema you want to use. The default value is `$MELTANO_EXTRACTOR_NAMESPACE`, which will expand to the `namespace` of the `extractor` used in the pipeline, e.g. `tap_gitlab` for [`tap-gitlab`](/plugins/extractors/gitlab.html).
