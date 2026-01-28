# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Reference

**Project Type**: Data integration platform (ELT/ETL)
**Language**: Python 3.10+
**Package Manager**: `uv`
**Task Runner**: `nox`
**Testing**: `pytest` with multiple backend support
**Linting**: `ruff` + `pre-commit`
**Type Checking**: `mypy` (full type hints required)

## Development Commands

### Package Management
- Install dependencies: `uv sync`
- Install with development dependencies: `uv sync --group=dev`
- Install with specific groups: `uv sync --group=testing --group=typing --group=pre-commit`
- Install with extras: `uv sync --extra=azure --extra=gcs --extra=s3 --extra=postgres --extra=mssql`

### Testing
- Run specific test: `uv run pytest tests/path/to/test.py::test_function`
- Run all tests: `nox -t test` or `nox -s pytest`
- Run tests with coverage: `nox -s pytest` (coverage included by default)
- Generate coverage report: `nox -s coverage -- report --show-missing`
- Run with specific backend: `PYTEST_BACKEND=postgresql nox -s pytest`

### Linting and Formatting
- Run all linting: `nox -t lint` or `nox -s pre-commit`
- Run pre-commit on all files: `pre-commit run --all-files`
- Run Ruff formatting: `ruff format`
- Run Ruff linting: `ruff check --fix`

### Type Checking
- Run MyPy: `nox -s mypy`
- Type check specific files: `mypy src/meltano/core/`

### Development Workflow
Use `nox` for development tasks - it manages virtual environments and dependencies automatically:
```bash
nox -l  # List available sessions
nox     # Run default sessions (mypy, pre-commit, pytest)
```

## Architecture Overview

Meltano is a data integration platform built with a plugin-based architecture around the ELT (Extract, Load, Transform) pattern.

### Core Architecture

**Service-Oriented Design**: The core is organized around specialized services (22+ services):

*Project & Configuration*:
- `ProjectService` - Project management and initialization
- `ProjectPluginsService` - Plugin registry and definitions
- `ConfigService` - Hierarchical configuration management
- `ProjectSettingsService` - Project-level settings
- `PluginConfigService` - Plugin-specific configuration
- `EnvironmentService` - Multi-environment deployment support

*Plugin Management*:
- `PluginInstallService` - Plugin installation and dependency management
- `PluginLockService` - Lock file generation and management
- `PluginRemoveService` - Plugin removal
- `PluginInvoker` - Plugin execution engine
- `VenvService` / `UvVenvService` - Virtual environment isolation

*State Management*:
- `StateService` - ELT state persistence across multiple backends
- Multiple `StateStoreManager` implementations (filesystem, database, cloud, memory)

*Execution & Support*:
- `JobLoggingService` - Job execution logging
- `ScheduleService` - Scheduled job management
- `SelectService` - Entity selection for taps
- `MigrationService` - Database schema migrations
- `ValidationService` - Configuration validation

**Plugin System**: Extensible plugin architecture supporting:
- **Singer plugins**: Taps (extractors) and targets (loaders) following Singer specification
- **DBT plugins**: Data transformation via dbt-core
- **Utility plugins**: Orchestrators (Airflow), BI tools (Superset), etc.
- **Mapper plugins**: Data transformation and mapping
- **File plugins**: File-based operations

**Block-Based Execution**: Modern async execution architecture (location: `src/meltano/core/block/`):
- `BlockSet` - Abstract base for all block execution types
- `ExtractLoadBlocks` - Main ELT pipeline executor with producer/consumer pattern
- `SingerBlock` - Wraps Singer plugins as IOBlocks with protocol compliance
- `IOBlock` - Input/output block abstraction with lifecycle management
- `BlockParser` - Parses command invocations into executable blocks
- **Execution Context**:
  - `ELBContext` - Modern block-based execution context (run ID, state strategy, session)
  - `ELTContext` - Legacy ELT execution context (extractor, loader, transform)
  - `ELContextProtocol` - Protocol ensuring consistent interface across contexts
- **Key Features**:
  - Asynchronous execution with proper resource cleanup
  - Producer/Consumer pipeline: Extractors/Mappers → Loaders/Mappers
  - Line length limits and buffer management for Singer protocol
  - State management with strategies: `auto`, `merge`, `overwrite`

### Key Directories

- `src/meltano/cli/` - CLI commands and user interface
- `src/meltano/core/` - Core business logic and services
- `src/meltano/core/plugin/` - Plugin system implementation
- `src/meltano/core/state_store/` - State persistence backends
- `src/meltano/core/runner/` - Plugin execution engines
- `tests/` - Test suite organized by module

### Configuration System

**Hierarchical Configuration**: Settings resolved in order:
1. Built-in defaults
2. Project settings (`meltano.yml`)
3. Environment-specific settings
4. Plugin configuration
5. Runtime overrides (CLI flags, environment variables)

**Multi-Environment Support**: Different configurations for dev/staging/prod environments via environment-specific meltano.yml files.

### State Management

**Multiple State Backends** (location: `src/meltano/core/state_store/`):
- **Filesystem** (`filesystem.py`) - Default, local file-based storage
- **Database** (`db.py`) - SQLAlchemy-based with PostgreSQL, SQLite, MSSQL support
- **Cloud Storage**:
  - `s3.py` - AWS S3 backend
  - `azure.py` - Azure Blob Storage backend
  - `gcs.py` - Google Cloud Storage backend
- **Memory** (`memory.py`) - In-memory storage for testing/single-run scenarios

**State Data Model**:
- `MeltanoState` - Dataclass with `state_id`, `partial_state`, `completed_state`
- `StateStoreManager` - Abstract base for all backend implementations
- `StateIDLockedError` - Prevents concurrent runs on same state ID

**State Strategies** (from `src/meltano/core/_state.py`):
- `auto` - Automatically choose between merge/overwrite based on context
- `merge` - Merge new state with existing state
- `overwrite` - Replace existing state completely

**State Types**:
- Singer state (incremental extraction tracking)
- Job state (execution status and history)
- Plugin state (installation and configuration)

### Plugin Development Patterns

When working with plugins:
- All plugins inherit from `BasePlugin` in `src/meltano/core/plugin/base.py`
- Plugin types defined in `PluginType` enum
- Use `PluginInvoker` for plugin execution
- Plugin settings defined via `SettingDefinition` objects
- Virtual environment isolation via `VenvService`

### Testing Patterns

- Tests are organized to mirror the source structure
- Use `pytest` fixtures for common test setup
- Backend-specific tests use `PYTEST_BACKEND` environment variable
- Integration tests in `tests/meltano/cli/` test full CLI workflows
- Mock external dependencies using `pytest-mock` and `requests-mock`

### Error Handling

**Custom Exception Hierarchy** (`src/meltano/core/error.py`):
- `MeltanoError` - Base user-facing exception with `reason` and `instruction` attributes
- **Specialized exceptions**:
  - Project: `ProjectNotFound`, `ProjectReadonly`
  - Plugins: `PluginNotFoundError`, `PluginInstallError`, `VariantNotFoundError`
  - Execution: `AsyncSubprocessError`, `PluginExecutionError`
  - State: `StateIDLockedError`, `StateBackendError`
- **ExitCode enum**: `OK` (0), `FAIL` (1), `NO_RETRY` (2)
- **Pattern**: Always provide user-actionable error messages with clear next steps

### Logging & Events

**Structured Logging**: Uses `structlog` for structured, context-rich logging
- Import: `import structlog; logger = structlog.stdlib.get_logger(__name__)`
- Outputs: Console (colorized), JSON, key-value, plain text
- Integration: Automatic telemetry tracking via structured context

**Structured Events System** (NEW - `src/meltano/core/logging/structured_event.py`):
- `StructuredEvent` - Abstract base class for events with rendering capabilities
- `StructuredEventFormatter` - Rich console formatting for events
- Methods: `__structlog__()` for log integration, `render()` for output
- Use case: Standardized event logging with rich formatting

**OutputLogger**: Captures subprocess output with structured parsing
- Parses plugin-specific output formats
- Extensible parser system for different plugin types
- Buffer management for large outputs

**JobLoggingService**: Manages job execution logs
- Persistent storage of job runs
- Integration with state management
- Searchable job history

### Telemetry & Tracking

**Snowplow-based Tracking** (location: `src/meltano/core/tracking/`):
- `Tracker` class - Main telemetry interface
- `BlockEvents` enum - Block lifecycle events (initialized, started, completed, failed)
- Context types: CLI, plugins, environment, exceptions, projects
- `TelemetrySettings` - User preferences for analytics
- **Privacy**: Respects user opt-out, no PII collected

### Virtual Environment Management

**VenvService Pattern**:
- `VenvService` - Base virtual environment manager (traditional pip/venv)
- `UvVenvService` - Modern implementation using `uv` package manager (faster, more reliable)
- **Capabilities**:
  - Plugin isolation in separate virtual environments
  - Lock file generation and management (`plugin.lock`)
  - Dependency resolution with conflict handling
  - Clean installation/upgrade/removal workflows

**ContainerService** (`src/meltano/core/container_service/`):
- Docker/container execution support via `aiodocker`
- Async container management
- Integrates with `PluginInvoker` for containerized plugins
- Requires extra dependencies: `uv sync --extra=docker`

### CLI Architecture

Location: `src/meltano/cli/` (32+ command files)

**Command Categories**:
- **Core Operations**: `add`, `remove`, `install`, `lock`, `initialize`
- **Execution**: `run`, `elt`, `invoke`, `job`, `schedule`
- **Configuration**: `config`, `params`, `schema`, `environment`
- **Management**: `state`, `logs`, `select`, `hub`
- **Advanced**: `compile`, `test`, `upgrade`, `validate`
- **Interactive**: `interactive/` subpackage for interactive configuration

**CLI Patterns**:
- Click-based with custom decorators
- `@pass_project` - Dependency injection of `Project` instance
- `PartialInstrumentedCmd` - Custom command class with telemetry
- `CliEnvironmentBehavior` - Enum for environment requirement levels
- `InstallPlugins` options - Reusable parameter combinations

### Testing Infrastructure

**Test Organization** (`tests/`):
- Mirror source structure: `tests/meltano/cli/`, `tests/meltano/core/`
- Backend-agnostic tests with `PYTEST_BACKEND` environment variable
- Integration tests for full CLI workflows

**Fixtures** (`tests/fixtures/`):
- Database fixtures for PostgreSQL, SQLite, MSSQL
- Docker fixtures for container tests
- Project fixtures for various configurations
- Plugin fixtures for mock testing

**Testing Patterns**:
- Use `pytest` fixtures for common setup
- Mock external dependencies with `pytest-mock` and `requests-mock`
- Async tests with `pytest-asyncio`
- Parametrized tests for multi-backend support

### Coding Conventions

**Type Hints** (Required):
- Full type hints required for all functions/methods
- `mypy` enforces strict type checking
- Use `typing_extensions` for compatibility features
- `t.TYPE_CHECKING` blocks for circular imports
- Example: `from typing import TYPE_CHECKING; import typing as t`

**Async Patterns**:
- Extensive use of `async`/`await` via `asyncio`
- Async context managers for resource management
- Async subprocess management
- Pattern: Clean lifecycle management with proper cleanup

**Deprecation Process**:
- Use `@deprecated` decorator for legacy functionality
- Issue `MeltanoInternalDeprecationWarning` warnings
- Document migration path in deprecation message
- Controlled removal across versions

**Configuration Resolution**:
- Dot-notation paths: `"plugin.setting"` → `plugin['setting']`
- Environment variable expansion with `expand_env_vars()`
- Fallback chains for missing values
- Negation support: `NO_` prefix to disable features

**Import Organization**:
```python
# Standard library
import typing as t
from pathlib import Path

# Third-party
import structlog
from click import command, option

# Local/application
from meltano.core.project import Project
from meltano.core.plugin import PluginType
```

## Development Guidelines

### Adding New CLI Commands
- Create command module in `src/meltano/cli/`
- Use Click decorators for argument parsing
- Add command to main CLI group in `cli.py`
- Include telemetry tracking for usage analytics

### Adding New Plugin Types
- Extend `PluginType` enum in `base.py`
- Create specialized plugin class if needed
- Update plugin factory logic
- Add appropriate runner if custom execution needed

### Working with State
- Use appropriate state store backend via `StateService`
- Implement atomic state updates
- Handle state migration for schema changes
- Test with multiple backend types

### Configuration Changes
- Update setting definitions in plugin classes
- Maintain backward compatibility
- Add environment variable support if needed
- Update JSON schema for validation

## Important Integration Points

**Project Discovery**:
- `Project.find()` - Walks parent directories to locate `meltano.yml`
- Automatic project detection for CLI commands
- Falls back to explicit project directory with `--cwd` flag

**Plugin Resolution**:
- `ProjectPluginsService.get_plugin()` - Resolves plugins from multiple sources
- Resolution order: Custom definitions → Lock file → Hub discovery → Inherited
- Handles variant selection and fallback logic

**State Backend Selection**:
- Dynamic selection based on `meltano.yml` configuration
- `state_backend.uri` determines backend type
- Automatic migration between backends
- Thread-safe state locking via `StateIDLockedError`

**Virtual Environment Isolation**:
- Each plugin gets isolated venv in `.meltano/plugins/`
- `VenvService` manages creation/activation/cleanup
- Lock files (`plugin.lock`) ensure reproducible installs
- `uv` provides faster, more reliable dependency resolution

**Telemetry Integration**:
- Automatic event tracking throughout CLI lifecycle
- `@pass_project` decorator injects tracking context
- Respects `send_anonymous_usage_stats` setting
- Block events track execution success/failure

**Database Migration**:
- `MigrationService` handles Alembic migrations
- Automatic on project initialization and upgrade
- Schema versioning for system database
- Migrations in `src/meltano/migrations/versions/`

**Container Execution**:
- Optional feature requiring `--extra=docker`
- `ContainerService` wraps `aiodocker` client
- Integrates with `PluginInvoker` for transparent execution
- Automatic volume mounting for project files

## Key Files & Locations

**Configuration**:
- `meltano.yml` - Project configuration file (root)
- `meltano.schema.json` - JSON schema for validation
- `.meltano/` - Project-local state and plugins directory
- `.meltano/run/` - Runtime state and logs

**Core Modules**:
- `src/meltano/core/project.py` - Project model and discovery
- `src/meltano/core/plugin/base.py` - Plugin base classes and types
- `src/meltano/core/block/` - Block-based execution engine
- `src/meltano/core/state_store/` - State persistence backends
- `src/meltano/core/runner/` - Plugin execution runners

**CLI Entry Points**:
- `src/meltano/cli/cli.py` - Main CLI entry point
- `src/meltano/cli/params.py` - Common CLI parameters
- `src/meltano/cli/utils.py` - CLI helper functions

**Testing**:
- `tests/conftest.py` - Pytest configuration and shared fixtures
- `tests/fixtures/` - Test fixtures and mock data
- `noxfile.py` - Nox session definitions

**Build & Configuration**:
- `pyproject.toml` - Project metadata and dependencies
- `uv.lock` - Locked dependency versions
- `.pre-commit-config.yaml` - Pre-commit hooks configuration
- `mypy.ini` - MyPy type checking configuration

## Common Development Workflows

**Adding a New State Backend**:
1. Create new module in `src/meltano/core/state_store/`
2. Inherit from `StateStoreManager` abstract base
3. Implement `get()`, `set()`, `clear()`, `acquire_lock()`, `list_state_ids()`
4. Add backend detection logic in state service
5. Add tests with backend fixtures
6. Update documentation

**Adding a New Plugin Type**:
1. Add new type to `PluginType` enum in `src/meltano/core/plugin/base.py`
2. Create specialized plugin class if needed (inherit from `BasePlugin`)
3. Update `ProjectPluginsService` factory logic
4. Add runner implementation if custom execution needed
5. Update CLI commands (`add`, `install`, etc.)
6. Add tests and documentation

**Modifying CLI Commands**:
1. Edit command module in `src/meltano/cli/`
2. Update Click decorators for parameters
3. Add telemetry tracking for new features
4. Update tests in `tests/meltano/cli/`
5. Run `nox -s pre-commit` to check formatting
6. Test with `pytest tests/meltano/cli/test_<command>.py`

**Working with Configuration**:
1. Define settings with `SettingDefinition` in plugin class
2. Use `ConfigService` to read/write configuration
3. Support environment variables with `env` property
4. Add validation logic in setting definition
5. Update JSON schema if adding project-level settings
6. Test resolution hierarchy

## Troubleshooting Tips (for Developers)

**Development Environment Setup**:
- Install dependencies: `uv sync --all-groups --all-extras`
- If `uv sync` fails, check Python version: `python --version` (requires 3.10+)
- Clear cache and reinstall: `rm -rf .venv && uv sync`
- Pre-commit hooks not running: `pre-commit install`

**Test Failures**:
- Run specific test with verbose output: `pytest tests/path/to/test.py::test_name -vv`
- Backend tests require database setup:
  - PostgreSQL: `PYTEST_BACKEND=postgresql nox -s pytest`
  - Start local PostgreSQL: `docker run -p 5432:5432 -e POSTGRES_PASSWORD=password postgres`
- Docker tests require Docker daemon running
- Clean test artifacts: `find . -type d -name __pycache__ -exec rm -rf {} +`
- Reset test database: Drop and recreate test databases between runs
- Fixture issues: Check `tests/conftest.py` for fixture definitions

**Type Checking Failures**:
- Run MyPy: `nox -s mypy` or `mypy src/meltano/core/`
- Ignore false positives: Add `# type: ignore[specific-error]` comments sparingly
- Missing type stubs: Install with `uv add --group=typing types-<package>`
- Circular import issues: Use `t.TYPE_CHECKING` blocks

**Linting/Formatting Issues**:
- Auto-fix most issues: `ruff check --fix && ruff format`
- Pre-commit failures: `pre-commit run --all-files`
- Specific hook: `pre-commit run <hook-name> --all-files`
- Skip hooks temporarily (not recommended): `git commit --no-verify`
- Update pre-commit hooks: `pre-commit autoupdate`

**Import/Module Issues**:
- `ModuleNotFoundError`: Ensure you're in virtual environment: `source .venv/bin/activate`
- Install in editable mode: `uv pip install -e .`
- Clear Python cache: `find . -type d -name __pycache__ -delete`
- Circular imports: Check for cycles, use `TYPE_CHECKING` blocks

**Debugging Tests**:
- Add breakpoint: `import pdb; pdb.set_trace()` or `breakpoint()`
- Run with pdb on failure: `pytest --pdb`
- Show print statements: `pytest -s`
- Verbose output: `pytest -vv`
- Show local variables on failure: `pytest -l`
- Run last failed tests: `pytest --lf`

**Nox Session Issues**:
- List available sessions: `nox -l`
- Run specific session: `nox -s <session-name>`
- Clear nox cache: `rm -rf .nox/`
- Sessions fail to create: Check Python interpreter availability
- Skip environment recreation: `nox -s <session> --reuse-existing-virtualenvs`

**Database/SQLAlchemy Issues**:
- Migration conflicts: Check `src/meltano/migrations/versions/` for conflicting migrations
- Create new migration: Use Alembic commands via `MigrationService`
- Reset test database: Drop all tables and rerun migrations
- Connection pool exhausted: Ensure proper session cleanup with context managers
- SQLite locking: Use separate database files for concurrent tests

**Async/Asyncio Debugging**:
- Enable asyncio debug mode: `PYTHONASYNCIODEBUG=1 pytest`
- Check for unawaited coroutines in test output
- Event loop issues: Ensure proper `pytest-asyncio` fixture usage
- Async context managers: Always use `async with` for proper cleanup

**Git/Pre-commit Issues**:
- Pre-commit hooks timeout: Increase timeout in `.pre-commit-config.yaml`
- Hooks fail on modified files: Stage changes first or use `--all-files`
- Update hooks: `pre-commit autoupdate`
- Clear hook cache: `pre-commit clean`

## Additional Resources

**Documentation**:
- Official docs: https://docs.meltano.com
- SDK docs: https://sdk.meltano.com
- Singer spec: https://hub.meltano.com/singer/spec

**Development Tools**:
- Ruff: https://docs.astral.sh/ruff/
- uv: https://docs.astral.sh/uv/
- MyPy: https://mypy.readthedocs.io/
- Nox: https://nox.thea.codes/

**Community**:
- Slack: https://meltano.com/slack
- GitHub Issues: https://github.com/meltano/meltano/issues
- Discussions: https://github.com/meltano/meltano/discussions
