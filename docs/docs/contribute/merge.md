---
title: Pull Request Process
description: Meltano is open source software built by a growing team and a community of contributors.
layout: doc
sidebar_position: 3
sidebar_class_name: hidden
---

Meltano uses an approval workflow for all pull requests.

1. Create your pull request (PR) in GitHub.
1. Assign the pull request to any eligible approvers as shown in the GitHub Pull Request UI (or specified in [CODEOWNERS](https://github.com/meltano/meltano/blob/main/.github/CODEOWNERS)) for a review cycle.
1. Once the review is done the reviewer may approve the pull request or send it back for further iteration.
1. Once approved, the pull request will be merged by any Meltano maintainer.

## Reviews

A contributor can ask for a review on any pull request, without this pull request being done and/or ready to merge.

Asking for a review is asking for feedback on the implementation, not approval of the pull request. It is also the perfect time to familiarize yourself with the code base. If you don’t understand why a certain code path would solve a particular problem, that should be sent as feedback: it most probably means the code is cryptic/complex or that the problem is bigger than anticipated.

Merge conflicts, failing tests and/or missing checkboxes should not be used as ground for sending back a pull request without feedback, unless specified by the reviewer.

## Semantic PRs

The `meltano` repo uses the [semantic-prs](https://github.com/Ezard/semantic-prs) GitHub app to check all PRs againts the [conventional commit](https://www.conventionalcommits.org/en/v1.0.0/) syntax.

Pull requests should be named according to the conventional commit syntax to streamline changelog and release notes management. We encourage (but do not require) the use of conventional commits in commit messages as well.

In general, PR titles should follow the format `<type>: <desc>`, where type is any one of these:

- `ci`
- `chore`
- `build`
- `docs`
- `feat`
- `fix`
- `perf`
- `refactor`
- `revert`
- `style`
- `test`

Optionally, you may use the expanded syntax to specify a scope in the form `<type>(<scope>): <desc>`. Currently scopes are:

- `core`
- `cli`

The latest rules and settings are found within the file [`.github/semantic.yml`](https://github.com/meltano/meltano/blob/main/.github/semantic.yml).

## Architectural Decision Records

Meltano makes use of ADR's (Architectural Decision Records) to record architectural decisions roughly as [described by Michael Nygard](http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions).
In a nutshell, these are used to document architectural decisions and to provide a record of the decisions made by the team and contributors in regard to Meltano's architecture. These are held in [docs/adr](https://github.com/meltano/meltano/blob/main/docs/adr).
To propose or add a new ADR, its simplest to create a new entry using [adr-tools](https://github.com/npryce/adr-tools), and then send a long a pull request for review.

## AI-Assisted Contributions

If your pull request was co-authored with an AI coding agent, please check the
AI tooling box in the PR template and follow the
[Agentic Coding guidelines](/contribute/agentic-coding) to make sure the
contribution meets the project's quality bar.

## Integration Tests and The Example Library

All new features should be covered via the [integration tests](https://docs.meltano.com/contribute/tests). In some cases
a new feature or feature change may already be covered indirectly by one of the existing examples and no changes required.
If you need an explicit test you can do so by either updating an existing guide (e.g. to include calling your new feature)
or by creating a new guide to demo (and thus test) a more complex behavior.

If adding a net-new entry or changing the behavior of an existing example, please be sure to update [the table of contents in the README.md](https://github.com/meltano/meltano/tree/main/docs/example-library) accordingly.
