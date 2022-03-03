# 3. Add incremental job support to meltano run

Date: 2022-02-27

## Status

Accepted

## Context

For actual adoption `meltano run` needs to close the feature gap with `meltano elt`. A core component of that is having support
for incremental jobs. For additional backgrounds and discussions on this see:

[#3130](https://gitlab.com/meltano/meltano/-/issues/3130)
[#3205](https://gitlab.com/meltano/meltano/-/issues/3205)

## Decision

We will add initial incremental job support to `meltano run`. Functionality in this iteration is limited to
unconfigurable ID's auto-generated using the active environment name and tap and target pair names. Yielding a format of
`{environment_name}:{tap_name}-to-{target_name}`. This behaviour is active only in the presence of an active environment.
When running with no active environment, state is not tracked.

- This version will attempt to run incrementally/save state by default. However, three top level flags are provided to alter behaviour:
  - `--no-state-update` will disable state saving for this invocation.
  - `--full-refresh` will force a full refresh and ignore current state.
  - `--force` will force a job run even if a conflicting job is in-flight.
- This version does not allow specifying a custom prefix or custom ID's.
- This version does not include mapping names when generating ID's



## Consequences

`meltano run` closes in on feature parity with the legacy `elt` command, and it becomes possible to use `run` for incremental jobs.

However, since users are unable to specify a custom ID `meltano run` can not yet take over for existing job's that have an ID that does not match the auto-generated string.
This is a limitation will be alleviated with the implementation of the `meltano state` command (ref: [#2754](https://gitlab.com/meltano/meltano/-/issues/2754)) which is specifically targeted to help people migrate their existing job states to the new naming convention.
Additionally, since mapping names are not used in ID generation users could end up with unintended ID collisions e.g:

```
$ meltano run tap-gitlab target-jsonl             # id tap-gitlab-to-target-jsonl
$ meltano run tap-gitlab hide-emails target-jsonl # also tap-gitlab-to-target-jsonl
```

The flags `--no-state-update`, `--full-refresh`, and `--force` are top level flags, users can not selectively apply these to meltano run segments e.g.:

```
$ meltano run --full-refresh tap-gitlab target-jsonl tap-salesfroce target-postgres # will perform a full refresh on both block sets.
```

Lastly, as mentioned this version _does not_ generate a job or preserve state when running without an active environment. We've
intentionally _excluded_ state tracking when there's no named environment as we believe its "safer" to not track than to
track automatically but potentially incorrectly.
