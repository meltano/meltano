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

If you are setting a Postgres backend for the first time, it's recommended to instead use the `postgres` extra and use the `postgresql+psycopg` URI scheme:

```bash
pipx install "meltano[postgres]"
meltano config meltano set database_uri postgresql+psycopg://<username>:<password>@<host>:<port>/<database>
```

### Plugin lock files are now always required

Plugin [lock files](/concepts/plugins#lock-artifacts) are now always required.

To generate all lock files for your project, run:

```bash
meltano lock --all
```

Before this, Meltano fell back to retrieving the plugin definition from Meltano Hub if the lock file was missing. This behavior caused issues when lock files were not deployed to production and Meltano Hub was unavailable because of network restrictions.

## Removed

## CLI and API Changes
