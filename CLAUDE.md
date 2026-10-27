# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Read @AGENTS.md

## Before pushing

Run `nox -t lint` and make sure it passes before committing or pushing. Pre-commit hooks and `ruff` alone are not enough: the lint tag also runs the type checkers (`mypy`, `ty`), which CI enforces.
