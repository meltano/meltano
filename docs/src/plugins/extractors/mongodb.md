---
sidebar: auto
metaTitle: Extract Data from MongoDB
description: Use Meltano to extract raw data from MongoDB and insert it into Postgres, Snowflake, and more.
---

# MongoDB

::: warning
This tap is currently a proof of concept and may have limited utility, but feedback is always welcome on [issue #631](https://gitlab.com/meltano/meltano/issues/631)
:::

`tap-mongodb` pulls raw data from a MongoDB source.

## Info

- **Data Source**: [MongoDB](https://www.mongodb.com/) source
- **Repository**: [https://github.com/singer-io/tap-mongodb](https://github.com/singer-io/tap-mongodb)

## Install

1. Navigate to your Meltano project in the terminal
2. Run the following command:

```bash
meltano add extractor tap-mongodb
```

If you are successful, you should see `Added and installed extractors 'tap-mongodb'` in your terminal.

## Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

```bash
# MongoDB databse host URI
export TAP_MONGODB_HOST=""
# MongoDB database port
export TAP_MONGODB_PORT=""
# MongoDB database username
export TAP_MONGODB_USER=""
# MongoDB database password
export TAP_MONGODB_PASSWORD=""
# MongoDB database name
export TAP_MONGODB_DATABASE=""
```
