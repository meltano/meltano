---
title: Meltano 3.0 Migration Guide
description: Migrate existing "v2" projects to the latest version of Meltano
layout: doc
sidebar_position: 21
sidebar_class_name: hidden
---

_Note: This document is still a work in progress. Expect further changes, coming soon._

The following list includes all recommended migration tasks as well as breaking changes in Meltano version 3.0.

## Recommended

## Changed

### Using Postgres as a backend now requires installing Meltano with extra components

If you are already using Postgres as a backend, odds are you rely on Meltano's dependency on `psycopg2`, so you will need to install Meltano with the `psycopg2` extra:

```bash
pipx install "meltano[psycopg2]"
```

If you are setting a Postgres backend for the first time, it's recommended to instead use the `postgres` extra and use the `postgres+psycopg` URI scheme:

```bash
pipx install "meltano[postgres]"
meltano config meltano set database_uri postgresql+psycopg://<username>:<password>@<host>:<port>/<database>
```

## Removed

## CLI and API Changes
