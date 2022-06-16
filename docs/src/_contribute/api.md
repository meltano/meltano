---
title: API Development
description: Contribute to the Meltano API.
layout: doc
weight: 10
---

This section of the guide provides guidance on how to work with the Meltano API, which serves as the backend of Meltano and is built with the [Python framework: Flask](https://github.com/pallets/flask).

## Getting Set Up

After all of your dependencies installed, we recommend opening a new window/tab in your terminal so you can run the following commands:

```bash
# Activate your poetry created virtual environment if needed.
# If you manage your virtualenv activation through other means you can omit this command.
poetry shell

# Create a new Meltano project
meltano init $PROJECT_NAME

# Change directory into your newly created project
cd $PROJECT_NAME

# Start a development build of the Meltano API and a production build of Meltano UI
FLASK_ENV=development meltano ui
```

The development build of the Meltano API and a production build of the UI will now be available at <http://localhost:5000/>.

<div class="notification is-danger">
  <p><strong>Potential MacOS port conflicts</strong></p>
  <p>On recent versions of MacOS (Monterey/12.0 and up) an AirPlay related service may be bound to port 5000. In that scenario you may want to specify an alternate <a href="/reference/settings#ui-bind-port">bind to port</a> to start the service on a port other than 5000. If you would like to continue using that port, please consult this <a href="https://developer.apple.com/forums/thread/682332">Apple Developers Forum article</a> to how to reset port 5000.</p>
</div>

## Debugging Your Code

To debug your code, we recommend using [the Python debugger](https://docs.python.org/3/library/pdb.html). It can be invoked by adding [`breakpoint()`](https://docs.python.org/3/library/functions.html#breakpoint) in your Python code at the location you want to drop into the debugger.

## API V2 Design Guidelines

For V2 of the Meltano API, we generally aim to implement and adhere to our variation of a [Resource Oriented Architecture](https://cloud.google.com/apis/design/resources).

> The key characteristic of a resource-oriented API is that it emphasizes resources (data model) over the methods performed on the resources (functionality).
> A typical resource-oriented API exposes a large number of resources with a small number of methods.
> The methods can be either the standard methods or custom methods.
>
> Where API functionality naturally maps to one of the standard methods, that method **should** be used in the API design.
> For functionality that does not naturally map to one of the standard methods,*custom methods* **may** be used.
> Custom methods offer the same design freedom as traditional RPC APIs, which can be used to implement common programming patterns, such as database transactions or data analysis.

### Concrete methods/verbs

We stick to traditional methods/verbs `List`, `Get`, `Create`, `Update`, and `Delete`, with the following HTTP equivalents:

- List
  - HTTP GET `<collection>`, No request body, Resource list as a response
- Get
  - HTTP GET `<resource>`, No request body, Resource as a response
- Create
  - HTTP POST `<collection>`, Resource as request body, Resource as response body
- Update
  - HTTP PUT, PATCH `<resource>`, Resource as request body, Resource as response body
- Delete
  - HTTP DELETE `<resource>`, No request body, No response body
  - HTTP DELETE `<resource>`, No request body, Resource as response body with a state indicating deletion (if a soft delete is being performed)

### Custom methods/verbs

Occasionally, during development we may also have a need for custom verbs (e.g. for things like copying state or bulk operations).
In those case, we'll map to an appropriate HTTP verb, but the MR/issue will require justification for the use of a custom verb, and be documented in this guide.
Where a custom verb is used, the verb will be appended to the resource as a new path segment:

- Move
  - HTTP POST `<collection>/<resource>/move` (we follow a more conventional style, rather than using Google's `<resource>:<verb>` style)

### Collections and resources

API service umbrella and namespace:

 - `meltano/core/v2beta` (during development)
 - `meltano/core/v2`

Our top-level collection is `projects/*` with an intermediate of `/envs/*` as we've opted to include support for operating on multiple projects.
The V2 API spec is in flux, we don't yet actually have strong ties between a lot of the topics beyond this level, but as we start specing v2 we expect a grouping around the below features to evolve.

- `envs/*/plugins/*`
- `envs/*/state/*`
- `envs/*/schedules/*`
- `envs/*/run/*`
- `envs/*/test/*`
- `envs/*/service/*`
- `envs/*/jobs/*`

As a hypothetical on how the spec might evolve, we may also end up organize around a `job` as resource or the like. Nesting under a `jobs` collection might look more like:

- `envs/*/jobs/*`
  - `envs/*/jobs/run` (potentially a custom verb - need to support ad hoc `meltano run`  like invocations, where the submitting client doesn't know what the state IDs will be)
  - `envs/*/jobs/*/runs/*`
  - `envs/*/jobs/*/schedule/*`
  - `envs/*/jobs/*/state/*`? (up for discussion whether state should be stand-alone or part of the jobs' collection.)
  - `envs/*/jobs/*/tests/*`? (would `meltano test` ever become a "job")

### API Design Examples

These are for illustration only, and subject to change.

```
# list all runs
GET meltano/core/v2/envs/prod/jobs/tap-gitlab-target-jsonl/runs
Response: {[the runs]}

# get a specific run
GET meltano/core/v2/envs/prod/jobs/tap-gitlab-target-jsonl/runs/ff643ba2
Response: {A run}

# meltano run equivalent (custom google style verb: run)
POST meltano/core/v2/envs/prod/jobs:run
{"command": "tap mapper target dbt:run", "args"...}
Reponse: {The run, with run_id , and "inprogress" status field}

# meltano state set equivalent
PUT meltano/core/v2/envs/stage/jobs/tap-gh-to-target-sql/state
{new state message}
Reponse: {"The new state after update"}

# meltano state copy equivalent (custom verb: copy)
POST meltano/core/v2/envs/stage/jobs/tap-gh-to-target-sql/state/copy
{destination: "different-state-id"}
Response: {"ref to the dest")
```

### Guidelines for FastAPI pydantic models and auto generated documention

TBD
