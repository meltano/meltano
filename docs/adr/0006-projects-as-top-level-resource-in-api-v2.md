# 6. Projects as top-level resource in API v2

Date: 2022-05-11

## Status

Accepted

## Context

In v2 of the API we have a chance to restructure and reorganize our URL namespace, collections, and resources. One of the core goals of a V2 of the API is to have closer to feature parity with the meltano cli. Just as the meltano cli can interact with multiple projects, so too might the API need to support multiple projects.  To support that, having a project concept as the top-level collection in the API is required:

```
$SERVICE_UMBRELLA/projects/$SOME_PROJECT/envs/$SOME_ENV
```

Being the top-level entity, it can not be added after the fact without creating a new API version. Without a project reference environments would naturally be the alternative top level collection.

See [#3302](https://gitlab.com/meltano/meltano/-/issues/3302#note_898109276) for additional context and background.

## Decision

Our top level collection in v2 of the API will be "projects", yielding a URL that looks as follows:

```
$SERVICE_UMBERELLA/projects/$SOME_PROJECT_ID/env/$SOME_ENV
```


## Consequences

Initially, having the project in the URI path only aid's in name-spacing. In the future, we may want to evolve the API server to allow a single instance to manage multiple projects. Including the project in the URL provides some future-proofing against having to cut a v3 version of the API solely to deal with Project level resources.

The main draw back to this is that at least in the short-term, API users will be required to supply a Project ref when interacting with the API for no obvious gain.
