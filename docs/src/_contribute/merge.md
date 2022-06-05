---
title: Pull Request Process
description: Meltano is open source software built by a growing team and a community of contributors.
layout: doc
weight: 3
---

Meltano uses an approval workflow for all pull requests.

1. Create your pull request (PR) in GitHub.
1. Assign the pull request to any eligible approvers as shown in the GitHub Pull Request UI (or specified in [CODEOWNERS](https://github.com/meltano/meltano/blob/main/.github/CODEOWNERS)) for a review cycle.
1. Once the review is done the reviewer may approve the pull request or send it back for further iteration.
1. Once approved, the pull request will be merged by any Meltano maintainer.

### Reviews

A contributor can ask for a review on any pull request, without this pull request being done and/or ready to merge.

Asking for a review is asking for feedback on the implementation, not approval of the pull request. It is also the perfect time to familiarize yourself with the code base. If you don’t understand why a certain code path would solve a particular problem, that should be sent as feedback: it most probably means the code is cryptic/complex or that the problem is bigger than anticipated.

Merge conflicts, failing tests and/or missing checkboxes should not be used as ground for sending back a pull request without feedback, unless specified by the reviewer.

## Architectural Decision Records

Meltano makes use of ADR's (Architectural Decision Records) to record architectural decisions roughly as [described by Michael Nygard](http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions).
In a nutshell, these are used to document architectural decisions and to provide a record of the decisions made by the team and contributors in regard to Meltano's architecture. These are held in [docs/adr](https://github.com/meltano/meltano/blob/main/docs/adr).
To propose or add a new ADR, its simplest to create a new entry using [adr-tools](https://github.com/npryce/adr-tools), and then send a long a pull request for review.

## Changelog

Meltano uses [changelog-cli](https://github.com/mc706/changelog-cli) to populate the CHANGELOG.md

### Script

Use `changelog (new|change|fix|breaks) MESSAGE` to describe your current work in progress.

```bash
$ poetry run changelog new "add an amazing feature"
$ git add CHANGELOG.md
```

Make sure to add CHANGELOG entries to your pull requests.
