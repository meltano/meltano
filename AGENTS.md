# AGENTS.md

This file provides guidance to AI coding agents when working with code in this repository.

## Quick Reference

**Project Type**: Data integration platform (ELT/ETL)
**Language**: Python 3.10+
**Package Manager**: `uv`
**Task Runner**: `nox`
**Testing**: `pytest` with support for multiple database backends
**Linting & Formatteing**: `ruff`
**Type Checking**: `mypy` + `ty`

## Development Commands

### Package Management

- Install dependencies: `uv sync --all-extras --all-groups`

### Testing

- Run specific test: `uv run pytest tests/path/to/test.py::test_function`
- Run all tests: `nox -t test` or `nox -s pytest`
- Run a subset of tests on a single Python version: `nox -p 3.14 -s pytest -- tests/meltano/core/state_store`
- Run with specific backend: `PYTEST_BACKEND=postgresql nox -s pytest`

### Linting, formatting and Type checking

- Run all linting: `nox -t lint`
- Run only type checks: `nox -s typing`
- Run only pre-commit checks: `nox -s pre-commit`

### Development Workflow

Use `nox` for development tasks - it manages virtual environments and dependencies automatically:

```bash
nox -l  # List available sessions
nox     # Run default sessions (mypy, pre-commit, pytest)
```

## GitHub

When submitting pull requests to GitHub, use this repo's `.github/pull_request_template.md` as your base to create the description. Note that not using the template might result in your PR being closed unceremoniously.

## Coding Conventions

- Type hints are required for all new code. See above for how to run type checks.
- Beware of asyncio overhead, e.g. https://github.com/meltano/meltano/pull/9724.
- The core is organized around specialized service classes and new core functionality should normally start by implementing a new service class. These are usually not ABCs, except for `SettingsService`.
- Subclass and raise `MeltanoError` to provide user-actionable error messages with clear next steps.
- Tests are organized to mirror the source structure
- Integration tests in `tests/meltano/cli/` test full CLI workflows
- Mock external dependencies (e.g. using `unittest.mock`)
