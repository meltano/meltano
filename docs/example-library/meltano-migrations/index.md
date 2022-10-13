# Basic meltano migrations test

A quick test of how meltano applies migrations.

## Setup

This test ships with a sample meltano database from Meltano v2.5.0 already in `.meltano`. To utilize it run:

```shell
meltano install
```

## Trigger a migration event

```shell
meltano --environment=dev state list
```

## Validate that a new run completes successfully

Validate that we can perform an EL task post migration:

```shell
meltano --environment=dev run tap-gitlab target-sqlite
meltano --environment=dev state list
```
