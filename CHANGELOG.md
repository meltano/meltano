# CHANGELOG

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/) and [Keep a Changelog](http://keepachangelog.com/).

## v4.1.2 (2026-02-03)

### 📦 Packaging changes

- Require google-cloud-storage 3+
- Require uv 0.8.14+
- [#9799](https://github.com/meltano/meltano/issues/9799) Allow pip 26.0

## v4.1.1 (2026-01-31)

### 🐛 Fixes

- [#9792](https://github.com/meltano/meltano/issues/9792) Require structlog 25.5.0+

## v4.1.0 (2026-01-30)

### ✨ New

- [#9694](https://github.com/meltano/meltano/issues/9694) Remove stale tables used by long-removed UI/API
- [#9759](https://github.com/meltano/meltano/issues/9759) Add plugin name or `meltano` as another column in the console-formatted output
- [#9680](https://github.com/meltano/meltano/issues/9680) Auto-select a supported Python version if the plugin is not compatible with Meltano's own Python version

### 🐛 Fixes

- [#9779](https://github.com/meltano/meltano/issues/9779) Always display Slack community message for errors without self-service instructions
- [#9775](https://github.com/meltano/meltano/issues/9775) Avoid displaying tracebacks when known CLI-level errors occur

### ⚙️ Under the Hood

- [#9723](https://github.com/meltano/meltano/issues/9723) Simplify state backend creation from settings
- [#9726](https://github.com/meltano/meltano/issues/9726) Replace use of `check-jsonschema` with direct `jsonschema` calls

### ⚡ Performance Improvements

- [#9724](https://github.com/meltano/meltano/issues/9724) Revert to sync APIs for writing the tap catalog file following discovery

### 📚 Documentation Improvements

- [#9758](https://github.com/meltano/meltano/issues/9758) Sync plugin definition syntax with current options

### 📦 Packaging changes

- [#9780](https://github.com/meltano/meltano/issues/9780) Allow Rich 14.3.x
- [#9762](https://github.com/meltano/meltano/issues/9762) Allow `packaging` 26.0
- [#9756](https://github.com/meltano/meltano/issues/9756) Allow ruamel-yaml 0.19.x

## v4.0.9 (2026-01-19)

### 🐛 Fixes

- [#9744](https://github.com/meltano/meltano/issues/9744) Handle `python` attribute when present in plugin YAML added with `meltano add <name> --from-ref ...`
- [#9734](https://github.com/meltano/meltano/issues/9734) Filter out Alembic logs of level INFO and below
- [#9732](https://github.com/meltano/meltano/issues/9732) Bump virtualenv from 20.35.4 to 20.36.1

### ⚙️ Under the Hood

- [#9710](https://github.com/meltano/meltano/issues/9710) Enable Ruff `EXE`, `FA`, `FLY`, `FURB` and `SLOT` rules
- [#9698](https://github.com/meltano/meltano/issues/9698) Add more type-safety to settings management
- [#9697](https://github.com/meltano/meltano/issues/9697) Use explicit package names to load resource files (e.g. `initialize.yml`) instead of unreliable `__package__`

### 📚 Documentation Improvements

- [#9729](https://github.com/meltano/meltano/issues/9729) Lock file maintenance
- [#9717](https://github.com/meltano/meltano/issues/9717) Update docs mentioning how to publish a custom plugin to Meltano Hub
- [#9707](https://github.com/meltano/meltano/issues/9707) Fix `meltano config <plugin>` examples to use the correct syntax `meltano config print <plugin>`

### 📦 Packaging changes

- [#9711](https://github.com/meltano/meltano/issues/9711) Removed license classifier made redundant by PEP 639

## v4.0.8 (2025-12-17)

### 🐛 Fixes

- [#9688](https://github.com/meltano/meltano/issues/9688) Fixed typo in migration error message
- [#9687](https://github.com/meltano/meltano/issues/9687) Serialize nested date-time values in plugin configuration
- [#9669](https://github.com/meltano/meltano/issues/9669) Parse plugin logs coming out during `meltano invoke`

### ⚙️ Under the Hood

- [#9689](https://github.com/meltano/meltano/issues/9689) Use the `Project.dirs` API in more places

## v4.0.7 (2025-12-09)

### ⚙️ Under the Hood

- [#9665](https://github.com/meltano/meltano/issues/9665) Remove dependency on `click-didyoumean`

### 📚 Documentation Improvements

- [#9675](https://github.com/meltano/meltano/issues/9675) Update `meltano config` examples to use new command syntax/order

### 📦 Packaging changes

- [#9673](https://github.com/meltano/meltano/issues/9673) Bump build requirement hatchling to 1.28.0

## v4.0.6 (2025-11-19)

### 🐛 Fixes

- [#9637](https://github.com/meltano/meltano/issues/9637) Bump `fasteners` to 0.20

### 📚 Documentation Improvements

- [#9634](https://github.com/meltano/meltano/issues/9634) Fix command syntax in troubleshooting docs -- _**Thanks @visch!**_

## v4.0.5 (2025-11-04)

### 🐛 Fixes

- [#9626](https://github.com/meltano/meltano/issues/9626) Expand environment variables in mapping configuration

### ⚙️ Under the Hood

- [#9627](https://github.com/meltano/meltano/issues/9627) Use pattern matching to update the schedule in `meltano schedule set`

### 📦 Packaging changes

- [#9609](https://github.com/meltano/meltano/issues/9609) Remove unmaintained dependency `flatten-dict`

## v4.0.4 (2025-10-31)

### 🐛 Fixes

- [#9621](https://github.com/meltano/meltano/issues/9621) Handle stringification of nested date values in plugin configuration

## v4.0.3 (2025-10-30)

### 🐛 Fixes

- [#9617](https://github.com/meltano/meltano/issues/9617) Default smart-open logs to the warning level and above
- [#9618](https://github.com/meltano/meltano/issues/9618) `meltano el/elt` now also supports log parsing

## v4.0.2 (2025-10-29)

### 🐛 Fixes

- [#9613](https://github.com/meltano/meltano/issues/9613) Auto-install plugin if existing virtualenv is broken

### 📚 Documentation Improvements

- [#9603](https://github.com/meltano/meltano/issues/9603) Add an admonition for `psycopg2` and link to SQLAlchemy docs

## v4.0.1 (2025-10-23)

### 🐛 Fixes

- [#9600](https://github.com/meltano/meltano/issues/9600) Fetch plugin definition only once when locking plugins with `meltano lock`

### ⚙️ Under the Hood

- [#9599](https://github.com/meltano/meltano/issues/9599) Filter out `urllib3` logs below the error level

## v4.0.0 (2025-10-17)

### BREAKING CHANGES

- [#9525](https://github.com/meltano/meltano/issues/9525) Print fewer keys in the default console output
- [#9520](https://github.com/meltano/meltano/issues/9520) Rename subprocess logger to `meltano.plugins.<stream>.<type>.<name>` (split stdout and stderr streams into separate loggers)
- [#9493](https://github.com/meltano/meltano/issues/9493) Remove `psycopg2` extra from the Docker images
- [#9477](https://github.com/meltano/meltano/issues/9477) Change order of positional arguments of `meltano config` subcommands
- [#9458](https://github.com/meltano/meltano/issues/9458) Remove `start_date` attribute from schedule

### ✨ New

- [#9583](https://github.com/meltano/meltano/issues/9583) Simplify how metrics are rendered with the console logger
- [#9582](https://github.com/meltano/meltano/issues/9582) Use a standard platform-dependent location to store Meltano logs
- [#9118](https://github.com/meltano/meltano/issues/9118) Support a `requires_meltano` key at the project level
- [#9576](https://github.com/meltano/meltano/issues/9576) Add validation to meltano state set command
- [#9570](https://github.com/meltano/meltano/issues/9570) Make `meltano state get` output compatible with `meltano state set`
- [#9572](https://github.com/meltano/meltano/issues/9572) Lower log level for symlink creation failure on Windows when not run as administrator -- _**Thanks @iamlorax!**_
- [#9571](https://github.com/meltano/meltano/issues/9571) Auto-lock plugin definitions
- [#9564](https://github.com/meltano/meltano/issues/9564) Add basic capabilities to mapper in JSON schema
- [#9565](https://github.com/meltano/meltano/issues/9565) Print installation error in a nice panel when using the console logger
- [#9554](https://github.com/meltano/meltano/issues/9554) Publish Python 3.14 Docker images
- [#9403](https://github.com/meltano/meltano/issues/9403) Add CLI version check warning system
- [#9542](https://github.com/meltano/meltano/issues/9542) And environment variables for `meltano run` options
- [#9535](https://github.com/meltano/meltano/issues/9535) New `--timeout` option for `meltano run`
- [#9534](https://github.com/meltano/meltano/issues/9534) Support `meltano config test` for loaders
- [#9521](https://github.com/meltano/meltano/issues/9521) Render exceptions parsed from structured logs
- [#9506](https://github.com/meltano/meltano/issues/9506) Parse structured logs coming from the Singer SDK
- [#9498](https://github.com/meltano/meltano/issues/9498) Log a more detailed reason for skipping a plugin's installation
- [#9494](https://github.com/meltano/meltano/issues/9494) Default to interactive settings flow when bare `meltano config set` command is invoked
- [#9484](https://github.com/meltano/meltano/issues/9484) Add `meltano state edit` to manually patch state -- _**Thanks @mahangu!**_
- [#9481](https://github.com/meltano/meltano/issues/9481) Slim Docker images
- [#9421](https://github.com/meltano/meltano/issues/9421) Customize meltano.yml YAML style with a user configuration file -- _**Thanks @mahangu!**_
- [#9412](https://github.com/meltano/meltano/issues/9412) Add meltano logs command for viewing job logs
- [#9183](https://github.com/meltano/meltano/issues/9183) Support custom `.env` paths
- [#9434](https://github.com/meltano/meltano/issues/9434) Make stream-only select patterns behave like `stream.*`
- [#9450](https://github.com/meltano/meltano/issues/9450) Add `--clear` option to select command

### 🐛 Fixes

- [#9566](https://github.com/meltano/meltano/issues/9566) Allow `meltano upgrade package` to run outside of a project directory
- [#9559](https://github.com/meltano/meltano/issues/9559) Update the error message when the executable is not found to use `--plugin-type` option
- [#9558](https://github.com/meltano/meltano/issues/9558) Remove deprecated plugin type positional argument from the CLI
- [#9557](https://github.com/meltano/meltano/issues/9557) Remove deprecated `meltano lock --all` flag
- [#9556](https://github.com/meltano/meltano/issues/9556) Removed `meltano install - <plugin_name>` support in favor of new `meltano install <plugin_name>`
- [#9552](https://github.com/meltano/meltano/issues/9552) Fix the error message when the state backend URI scheme is not known to Meltano
- [#9551](https://github.com/meltano/meltano/issues/9551) Do not display traceback for known errors
- [#9543](https://github.com/meltano/meltano/issues/9543) Correctly skip auto-installing plugins by fixing virtualenv fingerprint
- [#9524](https://github.com/meltano/meltano/issues/9524) Avoid reemitting noisy runner exception
- [#9510](https://github.com/meltano/meltano/issues/9510) Nuanced error detection for `FileNotFoundError` in plugin execution
- [#8810](https://github.com/meltano/meltano/issues/8810) Tap stream fields are now automatically selected when any subfield is selected
- [#9202](https://github.com/meltano/meltano/issues/9202) Make `aiodocker` an optional dependency
- [#9456](https://github.com/meltano/meltano/issues/9456) Honor `disable_tracking` setting

### ⚙️ Under the Hood

- [#9580](https://github.com/meltano/meltano/issues/9580) Move all project directory definitions to a new `ProjectDirsService`
- [#9581](https://github.com/meltano/meltano/issues/9581) Delay creation of installation log directory
- [#9573](https://github.com/meltano/meltano/issues/9573) Use `logging` calls for `meltano remove` events
- [#9578](https://github.com/meltano/meltano/issues/9578) Avoid deserializing state twice
- [#9569](https://github.com/meltano/meltano/issues/9569) Embed Hub client directly in lock service
- [#9553](https://github.com/meltano/meltano/issues/9553) Remove legacy warnings for configuration "profiles"
- [#9540](https://github.com/meltano/meltano/issues/9540) Remove redundant timeout log
- [#9538](https://github.com/meltano/meltano/issues/9538) Do not display traceback when timeout is exceeded
- [#9537](https://github.com/meltano/meltano/issues/9537) Simplify `--timeout` validation
- [#9512](https://github.com/meltano/meltano/issues/9512) Deprecate the `--all` flag of `meltano lock` and make it the default behavior
- [#9495](https://github.com/meltano/meltano/issues/9495) Standardize terminology usage from entity/attribute to stream/property
- [#9480](https://github.com/meltano/meltano/issues/9480) Avoid so much exception handling when finding a setting
- [#9479](https://github.com/meltano/meltano/issues/9479) Remove missing import handling for state backends now that they are loaded dynamically
- [#9478](https://github.com/meltano/meltano/issues/9478) Consolidate logs CLI logic into JobLoggingService
- [#9476](https://github.com/meltano/meltano/issues/9476) Raise a more specific exception when the configured state backend can not be found
- Move `PluginTypeArg` to `meltano.cli.params`
- [#9467](https://github.com/meltano/meltano/issues/9467) Split state lookup and retrieval
- [#9466](https://github.com/meltano/meltano/issues/9466) Use slotted dataclasses
- [#9465](https://github.com/meltano/meltano/issues/9465) Dropped support for Python 3.9
- [#9457](https://github.com/meltano/meltano/issues/9457) Improve docstrings and test coverage for Singer catalog manipulation
- [#9438](https://github.com/meltano/meltano/issues/9438) Get package version from distribution metadata

### 📚 Documentation Improvements

- [#9544](https://github.com/meltano/meltano/issues/9544) Document how to upgrade Meltano
- [#9533](https://github.com/meltano/meltano/issues/9533) Better call out the differences between `select` and `select_filter`
- [#9492](https://github.com/meltano/meltano/issues/9492) Link to SDK target development docs
- [#9455](https://github.com/meltano/meltano/issues/9455) Sync Meltano core settings
- [#9597](https://github.com/meltano/meltano/issues/9597) Document usage of uv environment variables

### 📦 Packaging changes

- [#9555](https://github.com/meltano/meltano/issues/9555) Declare support for Python 3.14
- [#9550](https://github.com/meltano/meltano/issues/9550) Allow uv 0.9
- [#9513](https://github.com/meltano/meltano/issues/9513) Allow Click 8.3
- [#9596](https://github.com/meltano/meltano/issues/9596) Allow Rich 14.2
- [#9496](https://github.com/meltano/meltano/issues/9496) Restore support for Click 8.1
- [#9472](https://github.com/meltano/meltano/issues/9472) Require Click 8.2+ and use new generic `click.Choice` support
- [#9449](https://github.com/meltano/meltano/issues/9449) Pin core `click` and `sqlalchemy` dependencies to their minor versions

## v3.x

See [changelogs/3.x.md](changelogs/v3.md).

## v2.x

See [changelogs/2.x.md](changelogs/v2.md).

## v1.x

See [changelogs/1.x.md](changelogs/v1.md).

## v0.x

See [changelogs/0.x.md](changelogs/v0.md).
