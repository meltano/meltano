# 4. Store Job State as VARCHAR

Date: 2022-04-26

## Status

Accepted

## Context

The `meltano state` command necessarily requires adding to the system db Singer state which is
not associated with any invoked job. Job state is currently represented as an ENUM
with possible values:

- IDLE
- RUNNING
- SUCCESS
- FAIL
- DEAD

There is no differentiation between `job` and `job run` or `job instance` in
our current schema. So because of the way job state is managed and constructed,
manually editing state will require creating new "dummy" job records. These need
to have a job state associated with them. Using any of the existing ENUM
values for this would at best be semantically incorrect and at worst could break
existing functionality in unexpected ways.

SQLite does not enforce ENUM types, so this field is already stored as VARCHAR in SQLite.

Postgres supports and enforces ENUM types, so this field is stored in Postgres as a user-defined type
called `job_state`.

Because ENUM support differs among DBMSes in ways that are not abstracted away in SQLAlchemy, there is
no easy way to write a DBMS-agnostic migration which adds a new possible value for an ENUM type.

## Decision

We will change the `state` field of the `Job` model to be represented as a `sqlalchemy.types.String`
column, which will be stored as VARCHAR on the DBMSes that we support.

In Python, this field will continue to be `State` ENUM. We will use a
[hybrid property](https://docs.sqlalchemy.org/en/14/orm/extensions/hybrid.html#building-custom-comparators)
with a custom comparator to map between the Python ENUM and the SQLAlchemy string type.

We will add a new `STATE_EDIT` value to the `State` ENUM.

## Consequences

Further state management features will become easier to implement because there will be an abstraction
for associating arbitrary state with job IDs.

Supporting new DBMSes may become slightly more difficult, since this migration may behave in
unexpected ways in DBMSes that treat ENUMs differently than SQLite or Postgres.
