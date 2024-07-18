---
title: Vendoring Dependencies
description: How to manage vendored dependencies in Meltano.
layout: doc
sidebar_position: 12
---

## Prerequisites

1. The [`vendoring`][vendoring-cli] command-line tool. Install with `pipx install vendoring`.

## Updating vendored dependencies

To add or upgrade vendored dependencies, update the `src/meltano/_vendor/vendor.txt` file and run the following command:

```bash
vendoring sync
```

This will update the vendored dependencies in the `src/meltano/_vendor` directory.

## Vendoring Policy

TODO

[vendoring-cli]: https://github.com/pradyunsg/vendoring
