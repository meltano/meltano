---
title: Agentic Coding
description: Guidelines for using AI coding agents when contributing to Meltano.
layout: doc
sidebar_position: 4
sidebar_class_name: hidden
---

We welcome contributions that use AI coding agents. AI-assisted contributions are held to the same quality bar as any
other pull request. The guidelines below help you get there.

:::warning

Please avoid wasting maintainers' time by submitting PRs you haven't personally reviewed, understood and tested. Any PR that appears to violate this guideline will be closed without a review.

:::

## Setup

Point your agent at
[`AGENTS.md`](https://github.com/meltano/meltano/blob/main/AGENTS.md) in the
repository root. It contains project conventions, architecture overview, and
common development workflows.

- **Claude Code** users: the
  [`CLAUDE.md`](https://github.com/meltano/meltano/blob/main/CLAUDE.md) file is
  loaded automatically and already references `AGENTS.md`.
- **Other agents**: feed `AGENTS.md` into your agent's context or system prompt
  so it follows the same conventions.

## Quality checklist

Before opening a pull request, verify the following - whether the code was
written by you, an agent, or both:

1. **Lint and format**

   ```bash
   nox -s lint
   ```

2. **Run the relevant tests**

   ```bash
   uv run pytest tests/path/to/test.py
   ```

3. **Review the diff yourself** - agents can introduce subtle issues such as
   overly broad exception handling, unnecessary refactors, hallucinated APIs,
   or redundant comments. A human review of the final diff is always required
   and a basic courtesy to the maintainers.

## Disclosure

If generative AI tooling was used to co-author your PR, check the corresponding
box in the [pull request template](https://github.com/meltano/meltano/blob/main/.github/pull_request_template.md)
and specify the tool name. This lets reviewers calibrate their review
accordingly.

:::warning

Not using the template might result in your pull request being closed without a review.

:::

## Tips for effective agent use

- **Keep changes focused.** Smaller, well-scoped prompts produce better results
  than asking an agent to refactor an entire module at once.
- **Verify external references.** Agents may hallucinate package names, API
  endpoints, or configuration keys. Double-check anything that references
  external systems.
- **Run the full validation loop.** Agents often skip the linter or type checker
  unless explicitly told to run them. Make it part of your workflow.
- **Iterate on failures.** If a test fails, share the traceback with the agent
  rather than accepting a speculative fix.
