# CHANGELOG

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/) and [Keep a Changelog](http://keepachangelog.com/).

## v4.1.0 (2025-10-23)

### 🐛 Fixes

- [#9600](https://github.com/meltano/meltano/issues/9600) Fix plugin definition only once when locking plugins with `meltano lock`

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

## v3.9.1 (2025-08-08)

### 🐛 Fixes

- [#9435](https://github.com/meltano/meltano/issues/9435) Disallow uv 0.8.7 since `find_uv_bin` is broken on Python 3.9

## v3.9.0 (2025-08-04)

### ✨ New

- [#9411](https://github.com/meltano/meltano/issues/9411) Implement UUIDv7 for time-ordered job run IDs
- [#9404](https://github.com/meltano/meltano/issues/9404) Add 'disabled' log level to suppress all logging output
- [#9400](https://github.com/meltano/meltano/issues/9400) Add log file support for uv venv backend installation errors -- _**Thanks @mahangu!**_
- [#9391](https://github.com/meltano/meltano/issues/9391) `meltano add` now updates existing plugins by default
- [#9374](https://github.com/meltano/meltano/issues/9374) Add decimal setting kind -- _**Thanks @mahangu!**_
- [#9366](https://github.com/meltano/meltano/issues/9366) Use `NO_UTC=1` environment variable to emit logs with timestamps in your local timezone

### 🐛 Fixes

- [#9394](https://github.com/meltano/meltano/issues/9394) Recreate venv when plugin Python version is changed -- _**Thanks @mahangu!**_
- [#9393](https://github.com/meltano/meltano/issues/9393) Increase YAML width to prevent wrapping long lines -- _**Thanks @mahangu!**_
- [#9386](https://github.com/meltano/meltano/issues/9386) Support both .yaml and .yml extensions for logging config files -- _**Thanks @mahangu!**_
- [#9368](https://github.com/meltano/meltano/issues/9368) Honor valid `properties` field name in `select` values

### ⚙️ Under the Hood

- [#9419](https://github.com/meltano/meltano/issues/9419) Represent UUID instances in YAML as strings
- [#9388](https://github.com/meltano/meltano/issues/9388) Remove dependency on croniter
- [#9378](https://github.com/meltano/meltano/issues/9378) Standardize how the positional plugin type parameter and the `--plugin-type` option are handled in `meltano add`, `meltano install` and `meltano remove`
- [#9364](https://github.com/meltano/meltano/issues/9364) Replace `atomicwrites` with stdlib functions
- [#9362](https://github.com/meltano/meltano/issues/9362) Replace deprecated `asyncio.iscoroutinefunction` with `inspect.iscoroutinefunction`

### 📚 Documentation Improvements

- [#9410](https://github.com/meltano/meltano/issues/9410) Document PostgreSQL database privileges and requirements
- [#9409](https://github.com/meltano/meltano/issues/9409) Update `meltano elt` references to `meltano el`
- [#9406](https://github.com/meltano/meltano/issues/9406) Document alternatives to meltano run --dump flag
- [#9408](https://github.com/meltano/meltano/issues/9408) Document that moving start_date to the past has no effect with incremental state
- [#9401](https://github.com/meltano/meltano/issues/9401) Fix typo in `meltano --version` example -- _**Thanks @ddobrinskiy!**_
- [#9385](https://github.com/meltano/meltano/issues/9385) Use tabs to exemplify new and legacy syntax for `meltano add`
- [#9381](https://github.com/meltano/meltano/issues/9381) Document that Snowflake is a supported state backend
- [#9370](https://github.com/meltano/meltano/issues/9370) The "most straightforward" way to install Meltano now is uv

### 📦 Packaging changes

- [#9426](https://github.com/meltano/meltano/issues/9426) Allow boto 1.40.x
- [#9425](https://github.com/meltano/meltano/issues/9425) Disallow click 8.2.2
- [#9392](https://github.com/meltano/meltano/issues/9392) Test with uv 0.8.0

## v3.8.0 (2025-07-07)

### ✨ New

- [#9353](https://github.com/meltano/meltano/issues/9353) Accept JSON string to configure the GCS state backend
- [#9351](https://github.com/meltano/meltano/issues/9351) `meltano install` no longer requires specifying a plugin type, i.e. `meltano install tap-github target-postgres` works too
- [#9350](https://github.com/meltano/meltano/issues/9350) `meltano remove` no longer requires specifying a plugin type, i.e. `meltano remove tap-github` works too
- [#9347](https://github.com/meltano/meltano/issues/9347) Limit the traceback in console logs format to two frames
- [#9348](https://github.com/meltano/meltano/issues/9348) For the `python` project and plugin setting, rely on the `venv.backend` to discover the correct Python executable
- [#9344](https://github.com/meltano/meltano/issues/9344) Log execution time at the end of a `meltano run` invocation
- [#9293](https://github.com/meltano/meltano/issues/9293) Make uv the default venv backend
- [#9335](https://github.com/meltano/meltano/issues/9335) Catalog is now refreshed when `--full-refresh` is used
- [#9329](https://github.com/meltano/meltano/issues/9329) New `--state-strategy` CLI option to control the behavior of state updates in `run` and `el`/`elt` commands
- [#9328](https://github.com/meltano/meltano/issues/9328) Support emitting logs with timestamps in local time
- [#9266](https://github.com/meltano/meltano/issues/9266) New CLI option `meltano select EXTRACTOR --json`
- [#9317](https://github.com/meltano/meltano/issues/9317) `meltano add` no longer requires specifying a plugin type, i.e. `meltano add tap-github` works too
- [#9012](https://github.com/meltano/meltano/issues/9012) Add `run_id` key to all logs for `meltano run` and `meltano el`

### 🐛 Fixes

- [#9330](https://github.com/meltano/meltano/issues/9330) Create Singer logging config regardless of any arguments passed to `meltano invoke <plugin> ...`

### ⚙️ Under the Hood

- [#9355](https://github.com/meltano/meltano/issues/9355) Make generic error message more log-friendly
- [#9354](https://github.com/meltano/meltano/issues/9354) Update the JSON schema to reflect recent changes
- [#9345](https://github.com/meltano/meltano/issues/9345) Split error handling for persisting state to the system database and to the configured state backend, and log details of the state backend failure

### 📚 Documentation Improvements

- [#9352](https://github.com/meltano/meltano/issues/9352) Improve reference description of `settings[*].aliases` and `settings[*].env`
- [#9343](https://github.com/meltano/meltano/issues/9343) Add more context around custom state backends
- [#9342](https://github.com/meltano/meltano/issues/9342) Add connector contribution and Q1/Q2 Changelogs

### 📦 Packaging changes

- [#9357](https://github.com/meltano/meltano/issues/9357) Allow boto3 1.39.x
- [#9325](https://github.com/meltano/meltano/issues/9325) Remove urllib3<2 constraint for Python 3.9
- [#9272](https://github.com/meltano/meltano/issues/9272) Remove `setuptools` constraint

## v3.7.9 (2025-06-26)

### 🐛 Fixes

- [#9331](https://github.com/meltano/meltano/issues/9331) Create Singer logging config regardless of any arguments passed to `meltano invoke <plugin> ...` (backport of #9330)

## v3.7.8 (2025-06-05)

### 🐛 Fixes

- [#9300](https://github.com/meltano/meltano/issues/9300) Do not try to cast expandable inherited settings

## v3.7.7 (2025-05-29)

### 🐛 Fixes

- [#8793](https://github.com/meltano/meltano/issues/8793) Avoid passing plugin configuration to the installation environment

### ⚙️ Under the Hood

- [#9289](https://github.com/meltano/meltano/issues/9289) Avoid checking catalog cache key if user passed a custom catalog
- [#9280](https://github.com/meltano/meltano/issues/9280) Split job and ELT schedules into separate classes
- [#9273](https://github.com/meltano/meltano/issues/9273) Use `ruamel.yaml.add_multi_representer` to add YAML representations of internal types

### 📚 Documentation Improvements

- [#9288](https://github.com/meltano/meltano/issues/9288) Remove outdated log messages from CLI examples
- [#9271](https://github.com/meltano/meltano/issues/9271) Fixed typo `mapper` -> `mappers` in `meltano.yml` inline data mapping example

### 📦 Packaging changes

- [#9290](https://github.com/meltano/meltano/issues/9290) Bump latest supported version of `setuptools` to 80

## v3.7.6 (2025-05-14)

### 🐛 Fixes

- [#9260](https://github.com/meltano/meltano/issues/9260) Fixed state merging for incomplete/interrupted payloads
- [#9258](https://github.com/meltano/meltano/issues/9258) Avoid writing empty state after an invalid STATE message -- _**Thanks @joaopamaral!**_

## v3.7.5 (2025-05-11)

### 🐛 Fixes

- [#9251](https://github.com/meltano/meltano/issues/9251) Compatibility with click 8.2.x

### ⚙️ Under the Hood

- [#9249](https://github.com/meltano/meltano/issues/9249) Make installation error details an extra context key of the main installation error log
- [#9242](https://github.com/meltano/meltano/issues/9242) Use dict instead of `OrderedDict`

### 📚 Documentation Improvements

- [#9250](https://github.com/meltano/meltano/issues/9250) Updated `docker compose` commands

## v3.7.4 (2025-04-28)

### 📦 Packaging changes

- [#9235](https://github.com/meltano/meltano/issues/9235) Allow installing Meltano with boto 1.38

## v3.7.3 (2025-04-22)

### 🐛 Fixes

- [#9193](https://github.com/meltano/meltano/issues/9193) Omit warning log messages coming from `urllib3` certificate errors
- [#9222](https://github.com/meltano/meltano/issues/9222) Make `name` argument of setting definition required
- [#9210](https://github.com/meltano/meltano/issues/9210) Use `airflow config list --defaults` to generate initial config file
- [#9208](https://github.com/meltano/meltano/issues/9208) Use `config generate` command to generate `airflow.cfg` configuration file -- _**Thanks @DTyvoniuk!**_

### 📦 Packaging changes

- [#9218](https://github.com/meltano/meltano/issues/9218) Bump supported version of `check-jsonschema`
- [#9220](https://github.com/meltano/meltano/issues/9220) Bump supported version of `rich`

## v3.7.2 (2025-04-09)

### 🐛 Fixes

- [#9200](https://github.com/meltano/meltano/issues/9200) Display a more useful error message if an unknown plugin could be a custom one
- [#9185](https://github.com/meltano/meltano/issues/9185) Avoid crashing with `KeyError` after a setting is unset

### ⚙️ Under the Hood

- [#9204](https://github.com/meltano/meltano/issues/9204) Remove redundant logic for handling builtin `systemdb` state backend
- [#9176](https://github.com/meltano/meltano/issues/9176) Refactor `CatalogRule` classes into dataclasses

### 📚 Documentation Improvements

- [#9205](https://github.com/meltano/meltano/issues/9205) Fixed a few broken links in plugin concept page
- [#9191](https://github.com/meltano/meltano/issues/9191) Drop dbt version pin required by now fixed dbt-labs/dbt-postgres#96 -- _**Thanks @rafalkrupinski!**_
- [#9179](https://github.com/meltano/meltano/issues/9179) Added installation examples for additional Meltano components and clarify system database requirements -- _**Thanks @cbrammer!**_

## v3.7.1 (2025-03-26)

### 🐛 Fixes

- [#9173](https://github.com/meltano/meltano/issues/9173) Avoid parsing valid ISO 8601 strings

### 📦 Packaging changes

- [#9171](https://github.com/meltano/meltano/issues/9171) Bump `tzlocal` to 5.3

## v3.7.0 (2025-03-25)

### ✨ New

- [#9158](https://github.com/meltano/meltano/issues/9158) Pass project `env` to installation environment
- [#9119](https://github.com/meltano/meltano/issues/9119) Parse relative dates in plugin config
- [#9019](https://github.com/meltano/meltano/issues/9019) Set `application/json` as the content type for blobs uploaded with the GCS state backend
- [#8367](https://github.com/meltano/meltano/issues/8367) Support state backend and setting add-ons
- [#9047](https://github.com/meltano/meltano/issues/9047) Added a default Meltano User-Agent env var that plugins can refer to in config
- [#9077](https://github.com/meltano/meltano/issues/9077) Pass a default logging configuration for Pipelinewise and Singer SDK extractors, loaders and mappers
- [#9046](https://github.com/meltano/meltano/issues/9046) The `process` key containing the process ID for a Meltano invocation is now added to logs when `callsite_parameters: true` is used
- [#9018](https://github.com/meltano/meltano/issues/9018) Add descriptions to Meltano's internal settings
- [#8975](https://github.com/meltano/meltano/issues/8975) Added a `--log-format` option as a shorcut to quickly change the format of logs
- [#8991](https://github.com/meltano/meltano/issues/8991) Uv venv backend is no longer experimental
- [#8951](https://github.com/meltano/meltano/issues/8951) Add a simple log formatter that only contains the event by default

### 🐛 Fixes

- [#9162](https://github.com/meltano/meltano/issues/9162) Stringify YAML values from top-level `env` key of `meltano.yml`
- [#9153](https://github.com/meltano/meltano/issues/9153) Display catalog file contents when it cannot be parsed as valid JSON
- [#9148](https://github.com/meltano/meltano/issues/9148) Send first heartbeat when initializing job
- [#9117](https://github.com/meltano/meltano/issues/9117) Avoid prepending a slash to state file path in Cloud state backends
- [#9045](https://github.com/meltano/meltano/issues/9045) Added help to `--extras` option of `meltano config ... list`
- [#9035](https://github.com/meltano/meltano/issues/9035) Limit boto3 to < 1.36 to fix incompatibility with Minio (S3-compatible state backend)
- [#9003](https://github.com/meltano/meltano/issues/9003) Disable local variables by default in JSON logs
- [#8973](https://github.com/meltano/meltano/issues/8973) Print the time when the job will go stale if no more heartbeats are sent

### ⚙️ Under the Hood

- [#9165](https://github.com/meltano/meltano/issues/9165) Refactor base state backend so that a lock is always acquired when supported
- [#9000](https://github.com/meltano/meltano/issues/9000) Use `anyio` to open `pathlib.Path` instances
- [#8972](https://github.com/meltano/meltano/issues/8972) Enable Ruff `ASYNC` rules, open files with `anyio` and run subprocess with `asyncio.create_subprocess_exec` in async contexts

### 📚 Documentation Improvements

- [#9116](https://github.com/meltano/meltano/issues/9116) Mention `meltano schedule run` whenever we discuss `meltano schedule`
- [#9115](https://github.com/meltano/meltano/issues/9115) Document common `metadata` keys
- [#9109](https://github.com/meltano/meltano/issues/9109) Updated the contributing guide
- [#9084](https://github.com/meltano/meltano/issues/9084) Use `meltano-map-transform` PyPI distribution in examples
- [#9069](https://github.com/meltano/meltano/issues/9069) Update plugin development guide to use uv
- [#9055](https://github.com/meltano/meltano/issues/9055) Update CLI examples to use `tap-shopify`
- [#9048](https://github.com/meltano/meltano/issues/9048) Document `plain` option of `cli.log_format`
- [#9011](https://github.com/meltano/meltano/issues/9011) Fixed small indent issue in mapper YAML example
- [#8992](https://github.com/meltano/meltano/issues/8992) Added 2024-Q4 changelog
- [#8983](https://github.com/meltano/meltano/issues/8983) Use a different repo in part 1 of Getting Started guide -- _**Thanks @martinburch!**_
- [#8969](https://github.com/meltano/meltano/issues/8969) Document `database_uri` examples for supported backends
- [#8961](https://github.com/meltano/meltano/issues/8961) Change to code theme that does not italicize keywords or variables -- _**Thanks @ReubenFrankel!**_

### 📦 Packaging changes

- [#9139](https://github.com/meltano/meltano/issues/9139) Switch to uv 🚀
- [#9092](https://github.com/meltano/meltano/issues/9092) Bump psutil from 6.1.1 to 7.0.0
- [#9089](https://github.com/meltano/meltano/issues/9089) Bump `check-jsonschema` and `ruamel.yaml`
- [#9088](https://github.com/meltano/meltano/issues/9088) Always install `uv` with Meltano
- [#9032](https://github.com/meltano/meltano/issues/9032) Bump structlog from 24.4.0 to 25.1.0
- [#8980](https://github.com/meltano/meltano/issues/8980) Bump croniter from 5.0.1 to 6.0.0
- [#8979](https://github.com/meltano/meltano/issues/8979) Bump the runtime-dependencies group with 6 updates
- [#8981](https://github.com/meltano/meltano/issues/8981) Bump jinja2 from 3.1.4 to 3.1.5
- [#8968](https://github.com/meltano/meltano/issues/8968) Bump the runtime-dependencies group with 2 updates

## v3.6.0 (2024-12-09)

### ✨ New

- [#8944](https://github.com/meltano/meltano/issues/8944) Suggest verifying stream selection after `meltano config ... test` fails
- [#8917](https://github.com/meltano/meltano/issues/8917) Bumped the default `elt.buffer_size` to 100 MiB
- [#8913](https://github.com/meltano/meltano/issues/8913) Include the Python version and machine type in system debug log message
- [#8894](https://github.com/meltano/meltano/issues/8894) Fields marked as `unsupported` in the catalog are now marked as such in the output of `meltano select --list --all`
- [#8889](https://github.com/meltano/meltano/issues/8889) The `args` attribute of plugin commands is now optional
- [#8786](https://github.com/meltano/meltano/issues/8786) Added an `--all` flag to `meltano state clear` to delete all state IDs -- _**Thanks @fauzxan!**_
- [#8735](https://github.com/meltano/meltano/issues/8735) Add Content-Type to S3 state file uploads
- [#8844](https://github.com/meltano/meltano/issues/8844) Support an environment variable for the `--full-refresh` flag -- _**Thanks @MutuT2!**_
- [#8618](https://github.com/meltano/meltano/issues/8618) Python 3.13 is now supported
- [#8737](https://github.com/meltano/meltano/issues/8737) Added `exceptions` to the log message when using the JSON formatter
- [#8626](https://github.com/meltano/meltano/issues/8626) Added a `--run-id` option to `meltano el[t]`
- [#8494](https://github.com/meltano/meltano/issues/8494) Added a `callsite_parameters` argument to the builtin log formatters, which adds source path, line number and function name fields to the emitted log

### 🐛 Fixes

- [#8949](https://github.com/meltano/meltano/issues/8949) Add newline at the end of plugin lock files
- [#8914](https://github.com/meltano/meltano/issues/8914) Ask for confirmation in `meltano config ... reset`
- [#8869](https://github.com/meltano/meltano/issues/8869) Adding User friendly loader error when the loader is missing from the Meltano run. -- _**Thanks @NishitSingh2023!**_
- [#8852](https://github.com/meltano/meltano/issues/8852) Using the `--force` flag of `meltano install` no longer causes plugin installation to crash when using the `uv` venv backend
- [#8828](https://github.com/meltano/meltano/issues/8828) Show the correct value in the "Current value is still" warning for `meltano config set` -- _**Thanks @ReubenFrankel!**_
- [#8815](https://github.com/meltano/meltano/issues/8815) A mapper is now auto-installed when one of its mappings is used in a command -- _**Thanks @ReubenFrankel!**_

### ⚙️ Under the Hood

- [#8851](https://github.com/meltano/meltano/issues/8851) Decoupled the `JobState` ORM model of the system db from state store implementations
- [#8898](https://github.com/meltano/meltano/issues/8898) Use `importlib.resources` to read package files and use `importlib.metadata` to detect "editable" installations (via PEP 610)
- [#8830](https://github.com/meltano/meltano/issues/8830) Dropped support for EOL Python 3.8

### 📚 Documentation Improvements

- [#8950](https://github.com/meltano/meltano/issues/8950) Document Git requirement and add `uv` section
- [#8937](https://github.com/meltano/meltano/issues/8937) Use tabs for code blocks with OS-specific instructions in Getting Started guide
- [#8934](https://github.com/meltano/meltano/issues/8934) Document a logging example to log at DEBUG level but excluding extractor/loader stdout
- [#8909](https://github.com/meltano/meltano/issues/8909) Update part1.mdx
- [#8829](https://github.com/meltano/meltano/issues/8829) Update Azure state backend connection documentation for DefaultAzureCredential -- _**Thanks @acarter24!**_
- [#8809](https://github.com/meltano/meltano/issues/8809) Bumped Docusaurus to 3.1, fixed broken links and started printing warnings on broken anchors
- [#8752](https://github.com/meltano/meltano/issues/8752) Added 2024-Q3 changelog
- [#8808](https://github.com/meltano/meltano/issues/8808) Fixed broken anchor links in settings page

### 📦 Packaging changes

- [#8956](https://github.com/meltano/meltano/issues/8956) Bump the runtime-dependencies group with 3 updates
- [#8947](https://github.com/meltano/meltano/issues/8947) Bump the runtime-dependencies group with 3 updates
- [#8943](https://github.com/meltano/meltano/issues/8943) Bump the runtime-dependencies group with 2 updates
- [#8931](https://github.com/meltano/meltano/issues/8931) Bump the runtime-dependencies group with 6 updates
- [#8907](https://github.com/meltano/meltano/issues/8907) Bump the runtime-dependencies group with 4 updates
- [#8910](https://github.com/meltano/meltano/issues/8910) Bump aiohttp from 3.10.10 to 3.10.11
- [#8883](https://github.com/meltano/meltano/issues/8883) Bump the runtime-dependencies group with 4 updates
- [#8873](https://github.com/meltano/meltano/issues/8873) Bump the runtime-dependencies group with 4 updates
- [#8860](https://github.com/meltano/meltano/issues/8860) Bump the runtime-dependencies group with 3 updates
- [#8849](https://github.com/meltano/meltano/issues/8849) Bump the runtime-dependencies group with 2 updates
- [#8841](https://github.com/meltano/meltano/issues/8841) Bump boto3 from 1.35.41 to 1.35.42 in the runtime-dependencies group

## v3.5.4 (2024-09-25)

### 🐛 Fixes

- [#8802](https://github.com/meltano/meltano/issues/8802) No longer fail on uploading state to S3 when the object does not initially exist
- [#8800](https://github.com/meltano/meltano/issues/8800) Failure message is now correctly printed when a plugin can not be removed from the system database

## v3.5.3 (2024-09-24)

### 🐛 Fixes

- [#8784](https://github.com/meltano/meltano/issues/8784) Inheriting plugins are no longer always auto-installed -- _**Thanks @ReubenFrankel!**_
- [#8785](https://github.com/meltano/meltano/issues/8785) Install plugins correctly given multiple levels of inheritance -- _**Thanks @ReubenFrankel!**_

### 📚 Documentation Improvements

- [#8779](https://github.com/meltano/meltano/issues/8779) Fix layout of troubleshooting page

## v3.5.2 (2024-09-16)

### 🐛 Fixes

- [#8770](https://github.com/meltano/meltano/issues/8770) Redact secret settings by default in `meltano compile` -- _**Thanks @holly-evans!**_
- [#8731](https://github.com/meltano/meltano/issues/8731) Valid options are now printed for the `--interval` option of the schedule subcommand

### ⚙️ Under the Hood

- [#8762](https://github.com/meltano/meltano/issues/8762) Remove `record-flattening` capability in favour of `schema-flattening` -- _**Thanks @ReubenFrankel!**_
- [#8748](https://github.com/meltano/meltano/issues/8748) Move `install_plugins` to `meltano.core.plugin_install_service`
- [#8732](https://github.com/meltano/meltano/issues/8732) Use `uv venv` instead of `uv virtualenv` alias

### 📚 Documentation Improvements

- [#8764](https://github.com/meltano/meltano/issues/8764) Migrate to Docusaurus v3
- [#8756](https://github.com/meltano/meltano/issues/8756) Updated docs to reference `meltano-dbt-ext` PyPI distribution

## v3.5.1 (2024-08-23)

### 🐛 Fixes

- [#8689](https://github.com/meltano/meltano/issues/8689) Emit a clearer error message when trying to set/unset an unknown setting in `.env`
- [#8658](https://github.com/meltano/meltano/issues/8658) List only the state IDs within the specified prefix in the S3 URI
- [#8698](https://github.com/meltano/meltano/issues/8698) `meltano config ... test` now uses the `elt.buffer` setting
- [#8699](https://github.com/meltano/meltano/issues/8699) Add missing `project_readonly` setting to JSON schema
- [#8691](https://github.com/meltano/meltano/issues/8691) Addressed `structlog` warning by removing `format_exc_info` from the processor chain

### 📚 Documentation Improvements

- [#8721](https://github.com/meltano/meltano/issues/8721) Added instructions for installing Meltano with uv
- [#8695](https://github.com/meltano/meltano/issues/8695) Fixed line highlighting and handling of `==` in code blocks

## v3.5.0 (2024-07-23)

### ✨ New

- [#8633](https://github.com/meltano/meltano/issues/8633) Added a `--only-install` option to commands that can auto-install plugins
- [#8482](https://github.com/meltano/meltano/issues/8482) Plugins are now auto-installed when commands require them -- _**Thanks @ReubenFrankel!**_
- [#8620](https://github.com/meltano/meltano/issues/8620) Sensitive values in `meltano config <plugin>` are now hidden by default
- [#8580](https://github.com/meltano/meltano/issues/8580) Added CLI `--refresh-catalog` option and extractor extra `use_cached_catalog` to ignore the cached source catalog

### 🐛 Fixes

- [#8648](https://github.com/meltano/meltano/issues/8648) Listing Cloud (S3, GCS, etc.) state IDs no longer crashes if there is a file at the root of the bucket, and files in GCS buckets are only listed within the prefix specified in the `state_backend_uri` -- _**Thanks @jx2lee!**_
- [#8636](https://github.com/meltano/meltano/issues/8636) Values with `$` can now be escaped instead of trying to expand them from environment variables
- [#8590](https://github.com/meltano/meltano/issues/8590) `meltano config ... test` now also checks for `BATCH` messages

### ⚙️ Under the Hood

- [#8265](https://github.com/meltano/meltano/issues/8265) Use timezone-aware datetime objects

### 📚 Documentation Improvements

- [#8646](https://github.com/meltano/meltano/issues/8646) Documented hot to escape setting values with `$`
- [#8627](https://github.com/meltano/meltano/issues/8627) Fixed a broken link in the plugin concept page
- [#8621](https://github.com/meltano/meltano/issues/8621) Update to current year and recommendations
- [#8610](https://github.com/meltano/meltano/issues/8610) Remove Meltano Cloud docs
- [#8609](https://github.com/meltano/meltano/issues/8609) Redirect Meltano Cloud docs to Arch docs
- [#8608](https://github.com/meltano/meltano/issues/8608) Meltano Cloud has been shut down in favor of Arch -- _**Thanks @hulet!**_
- [#8505](https://github.com/meltano/meltano/issues/8505) Added 2024-Q2 changelog
- [#8589](https://github.com/meltano/meltano/issues/8589) Recommend adding `namespace` key to custom plugins when migrating to Meltano 3
- [#8578](https://github.com/meltano/meltano/issues/8578) Update `environments.md` to fix link
- [#8570](https://github.com/meltano/meltano/issues/8570) Added a few dbt-postgres troubleshooting notes to the Getting Started guide
- [#8566](https://github.com/meltano/meltano/issues/8566) Added a note about state IDs when using `meltano schedule run`

## v3.4.2 (2024-05-15)

### 🐛 Fixes

- [#8542](https://github.com/meltano/meltano/issues/8542) State from interrupted pipelines or using the `--merge-state` flag no longer causes crashes

### 📚 Documentation Improvements

- [#8544](https://github.com/meltano/meltano/issues/8544) Added YAML docs examples of global and per-plugin `python` executable option

## v3.4.1 (2024-05-06)

### 🐛 Fixes

- [#8509](https://github.com/meltano/meltano/issues/8509) Mapper configuration is no longer ignored and is passed to direct mapper invocations as well as mappings in pipelines
- [#8527](https://github.com/meltano/meltano/issues/8527) Made the output of `meltano select ... list` consistent between different Python versions
- [#8213](https://github.com/meltano/meltano/issues/8213) `meltano config <plugin> test` false-negative on Windows -- _**Thanks @ReubenFrankel!**_
- [#8508](https://github.com/meltano/meltano/issues/8508) Cron regex pattern on meltano.schema.json -- _**Thanks @sabino!**_

### ⚙️ Under the Hood

- [#8470](https://github.com/meltano/meltano/issues/8470) Started enforcing usage of `structlog.stdlib.get_logger` over `logging.getLogger` and banned use of the root logger
- [#8510](https://github.com/meltano/meltano/issues/8510) Plugin installation status is now logged instead of printed

### 📚 Documentation Improvements

- [#8524](https://github.com/meltano/meltano/issues/8524) Changed references of Airflow `orchestrator` to `utility`
- [#8506](https://github.com/meltano/meltano/issues/8506) Document `venv.backend` usage to configure `uv`

## v3.4.0 (2024-04-18)

### ✨ New

- [#8459](https://github.com/meltano/meltano/issues/8459) `meltano run` now has a `--run-id` option to allow for custom run UUIDs
- [#8465](https://github.com/meltano/meltano/issues/8465) Support `uv` as an optional virtualenv backend
- [#8355](https://github.com/meltano/meltano/issues/8355) Support installing multiple plugins of any type -- _**Thanks @ReubenFrankel!**_

### 🐛 Fixes

- [#8486](https://github.com/meltano/meltano/issues/8486) "`kind: {kind}` is deprecated..." is no longer logged if the corresponding replacement is in place
- [#8489](https://github.com/meltano/meltano/issues/8489) Environment variables from `.env` are now passed to the plugin installation subprocesses
- [#8490](https://github.com/meltano/meltano/issues/8490) An explicit error message is now logged when Meltano fails to retrieve tap state from the state backend
- [#8447](https://github.com/meltano/meltano/issues/8447) `meltano run` no longer creates empty `venv` plugin directories for inherited plugins
- [#8446](https://github.com/meltano/meltano/issues/8446) Added `run_id` and `job_name` properties to `meltano run` log messages

### ⚙️ Under the Hood

- [#8499](https://github.com/meltano/meltano/issues/8499) Only lookup uv executable once
- [#8469](https://github.com/meltano/meltano/issues/8469) Fixed some log serialization issues with `meltano.core.proj…ec_plugins_service.DefinitionSource` and `meltano.core.plugin.project_plugin.ProjectPlugin`

### 📚 Documentation Improvements

- [#8449](https://github.com/meltano/meltano/issues/8449) Fixed a broken link to custom plugin definitions in the project concept page
- [#8432](https://github.com/meltano/meltano/issues/8432) Added the 2024-Q1 changelog

## v3.3.2 (2024-03-06)

### 🐛 Fixes

- [#8436](https://github.com/meltano/meltano/issues/8436) Terminal output from plugin installation is now safely decoded
- [#8381](https://github.com/meltano/meltano/issues/8381) Print `Plugin definition is already locked` to stdout instead of stderr
- [#8399](https://github.com/meltano/meltano/issues/8399) Handle non-UTF-8 lines in plugin output for logging -- _**Thanks @nkclemson!**_

### 📚 Documentation Improvements

- [#8434](https://github.com/meltano/meltano/issues/8434) Added a note about using the `--require-virtualenv` flag for installing Meltano with pip
- [#8433](https://github.com/meltano/meltano/issues/8433) Removed some stale references to the old API

## v3.3.1 (2024-01-26)

### 🐛 Fixes

- [#8379](https://github.com/meltano/meltano/issues/8379) `--from-ref` for a plugin definition missing a `variant` -- _**Thanks @ReubenFrankel!**_

### 📚 Documentation Improvements

- [#8378](https://github.com/meltano/meltano/issues/8378) Mention `--from-ref` in the custom extractor guide -- _**Thanks @ReubenFrankel!**_

## v3.3.0 (2024-01-23)

### ✨ New

- [#8351](https://github.com/meltano/meltano/issues/8351) Warn if select rules are not used on catalog -- _**Thanks @haleemur!**_
- [#8176](https://github.com/meltano/meltano/issues/8176) Add new `--update` flag to `meltano add` to re-add plugins to a project -- _**Thanks @ReubenFrankel!**_
- [#7874](https://github.com/meltano/meltano/issues/7874) Add setting `sensitive` flag -- _**Thanks @ReubenFrankel!**_

### 🐛 Fixes

- [#8365](https://github.com/meltano/meltano/issues/8365) Retain stderr in `meltano config <plugin> test` -- _**Thanks @ReubenFrankel!**_
- [#8354](https://github.com/meltano/meltano/issues/8354) Emit pip installation errors

### ⚡ Performance Improvements

- [#8343](https://github.com/meltano/meltano/issues/8343) Cache `Project.dotenv_env`

### 📚 Documentation Improvements

- [#8306](https://github.com/meltano/meltano/issues/8306) Add changelog updates

## v3.2.0 (2023-12-05)

## v3.2.0rc1 (2023-12-05)

### ✨ New

- [#8258](https://github.com/meltano/meltano/issues/8258) Add a `--merge-state` flag to `meltano run` to merge the current pipeline state with that of the latest run
- [#8268](https://github.com/meltano/meltano/issues/8268) Expand environment variables in array setting values

### 🐛 Fixes

- [#8301](https://github.com/meltano/meltano/issues/8301) Interactive config now indicates that you're typing a redacted value -- _**Thanks @abastola0!**_

## v3.2.0b1 (2023-11-21)

### ✨ New

- [#8184](https://github.com/meltano/meltano/issues/8184) Log Meltano version and Operating System at invocation of CLI -- _**Thanks @ashu565!**_
- [#8228](https://github.com/meltano/meltano/issues/8228) Support setting configuration from files and STDIN -- _**Thanks @XshubhamX!**_
- [#8194](https://github.com/meltano/meltano/issues/8194) Allow escaping stream names with periods in `select` rules
- [#8241](https://github.com/meltano/meltano/issues/8241) Support Python 3.12
- [#8215](https://github.com/meltano/meltano/issues/8215) Support authenticating to Azure state backend without a connection string -- _**Thanks @XshubhamX!**_

### 🐛 Fixes

- [#8249](https://github.com/meltano/meltano/issues/8249) Display special characters in column names in the output of `meltano select --list`
- [#8227](https://github.com/meltano/meltano/issues/8227) Validate input to settings with `kind: options`
- [#8232](https://github.com/meltano/meltano/issues/8232) Interval validation for `meltano schedule set` -- _**Thanks @XshubhamX!**_
- [#8225](https://github.com/meltano/meltano/issues/8225) Redirect tap's stderr to /dev/null during a configuration test -- _**Thanks @raiatul14!**_

### 📚 Documentation Improvements

- [#8267](https://github.com/meltano/meltano/issues/8267) Add Q4 Changelog
- [#8260](https://github.com/meltano/meltano/issues/8260) Add information about database schema destination -- _**Thanks @EChaffraix!**_
- [#8259](https://github.com/meltano/meltano/issues/8259) Fix links in v3 migration guide
- [#8251](https://github.com/meltano/meltano/issues/8251) Fix dbt model in part3.mdx -- _**Thanks @diegoquintanav!**_
- [#8214](https://github.com/meltano/meltano/issues/8214) Document other supported ways of configuring an S3 endpoint URL
- [#8211](https://github.com/meltano/meltano/issues/8211) Sync sidebar order with index page link-lists, remove broken /index links -- _**Thanks @mjsqu!**_
- [#8209](https://github.com/meltano/meltano/issues/8209) Remove broken link (reference/index) and order links to match sidebar -- _**Thanks @mjsqu!**_
- [#8210](https://github.com/meltano/meltano/issues/8210) Add tabs for all remaining env/cli/config settings -- _**Thanks @mjsqu!**_
- [#8201](https://github.com/meltano/meltano/issues/8201) Use tabs for examples on settings page -- _**Thanks @mjsqu!**_
- [#8200](https://github.com/meltano/meltano/issues/8200) Update contribution guidelines -- _**Thanks @mjsqu!**_
- [#8155](https://github.com/meltano/meltano/issues/8155) Add september changelog

## v3.1.0 (2023-09-26)

### ✨ New

- [#8169](https://github.com/meltano/meltano/issues/8169) Added `--force-install` CLI flag for meltano `add` command. -- _**Thanks @XshubhamX!**_
- [#8145](https://github.com/meltano/meltano/issues/8145) Save pip logs to a file in the system directory
- [#7907](https://github.com/meltano/meltano/issues/7907) Add plugin from ref -- _**Thanks @ReubenFrankel!**_

### 🐛 Fixes

- [#8179](https://github.com/meltano/meltano/issues/8179) Removed the `--verbose` option from CLI, which no longer had any effect -- _**Thanks @arorarohan981!**_
- [#8044](https://github.com/meltano/meltano/issues/8044) Better error message when Azure connection string is missing
- [#8115](https://github.com/meltano/meltano/issues/8115) Do not perform destructive state ops when answering 'no' in prompt

### 📚 Documentation Improvements

- [#8178](https://github.com/meltano/meltano/issues/8178) Top-level ordered lists are now rendered correctly in docs
- [#8156](https://github.com/meltano/meltano/issues/8156) Added docs for --cwd CLI option -- _**Thanks @XshubhamX!**_
- [#8143](https://github.com/meltano/meltano/issues/8143) Remove Cloud announcement banner
- [#8113](https://github.com/meltano/meltano/issues/8113) Update Cloud "Getting Started" guide to include the lock command
- [#8111](https://github.com/meltano/meltano/issues/8111) Add example of database URI for SQL Server -- _**Thanks @wesseljt!**_
- [#8087](https://github.com/meltano/meltano/issues/8087) Add cloud state command

## v3.0.0 (2023-09-05)

### BREAKING CHANGES

- [#8041](https://github.com/meltano/meltano/issues/8041) Remove `target_schema` loader extra
- [#8007](https://github.com/meltano/meltano/issues/8007) Always require plugin lock files
- [#7499](https://github.com/meltano/meltano/issues/7499) Remove API and web UI
- [#7656](https://github.com/meltano/meltano/issues/7656) Remove the `meltano discover` command

### ✨ New

- [#8020](https://github.com/meltano/meltano/issues/8020) Add [`python` setting](https://docs.meltano.com/reference/settings#python)
- [#7997](https://github.com/meltano/meltano/issues/7997) Add [`el` command](https://docs.meltano.com/reference/command-line-interface#el) as an alias of `elt` and deprecate both `elt` and the `--transform` option
- [#7992](https://github.com/meltano/meltano/issues/7992) Add support for mappers in the invoke command
- [#7989](https://github.com/meltano/meltano/issues/7989) Add `meltano hub ping` command
- [#7984](https://github.com/meltano/meltano/issues/7984) Add `meltano config --unsafe` flag -- _**Thanks @ReubenFrankel!**_
- [#7981](https://github.com/meltano/meltano/issues/7981) Support `psycopg[binary]` under a new `postgres` extra
- [#7963](https://github.com/meltano/meltano/issues/7963) Bump SQLAlchemy to 2.0
- [#7932](https://github.com/meltano/meltano/issues/7932) Add "did you mean" CLI command name suggestions
- [#7846](https://github.com/meltano/meltano/issues/7846) Add aliases for the `@once` schedule interval

### 🐛 Fixes

- [#8042](https://github.com/meltano/meltano/issues/8042) Ensure migration lock file is closed after read
- [#8043](https://github.com/meltano/meltano/issues/8043) Ensure elt/run log file is closed
- [#8031](https://github.com/meltano/meltano/issues/8031) Redact DB password from logs
- [#8015](https://github.com/meltano/meltano/issues/8015) Display a better error message when database URI is null
- [#7982](https://github.com/meltano/meltano/issues/7982) Use hyphens consistently for CLI options
- [#7947](https://github.com/meltano/meltano/issues/7947) Support [PEP 440 direct references](https://peps.python.org/pep-0440/#direct-references) in `pip_url`

### ⚙️ Under the Hood

- [#7964](https://github.com/meltano/meltano/issues/7964) Replace deprecated `locale.getdefaultlocale` with `locale.getlocale` -- _**Thanks @AmirAflak!**_
- [#7960](https://github.com/meltano/meltano/issues/7960) Compatibility with SQLAlchemy 2

### 📚 Documentation Improvements

- [#8011](https://github.com/meltano/meltano/issues/8011) Add JSON Schema information -- _**Thanks @anden-akkio!**_
- [#7991](https://github.com/meltano/meltano/issues/7991) Fix cloud install git URL
- [#7975](https://github.com/meltano/meltano/issues/7975) Link `mssql` additional component to system database explanation
- [#7979](https://github.com/meltano/meltano/issues/7979) Correct `repo_ext` to `ext_repo` for plugin definition syntax -- _**Thanks @ReubenFrankel!**_
- [#7953](https://github.com/meltano/meltano/issues/7953) Update tagline in readme
- [#7951](https://github.com/meltano/meltano/issues/7951) Update changelog
- [#7950](https://github.com/meltano/meltano/issues/7950) Fix logging example -- _**Thanks @aminebeh!**_
- [#7948](https://github.com/meltano/meltano/issues/7948) Update docusaurus.config.js -- _**Thanks @gridig!**_
- [#7945](https://github.com/meltano/meltano/issues/7945) Douwe fixes
- [#7944](https://github.com/meltano/meltano/issues/7944) Quick doc fixes
- [#7936](https://github.com/meltano/meltano/issues/7936) Migrate Meltano docs to Docusaurus
- [#7902](https://github.com/meltano/meltano/issues/7902) Remove ELT messaging, move things around
- [#7931](https://github.com/meltano/meltano/issues/7931) Cloud docs ssh key validate tip
- [#7930](https://github.com/meltano/meltano/issues/7930) Meltano cloud to meltano-cloud
- [#7926](https://github.com/meltano/meltano/issues/7926) Fix state backend env vars in examples

## v2.20.0 (2023-07-19)

### ✨ New

- [#7733](https://github.com/meltano/meltano/issues/7733) Add setting `hidden` flag -- _**Thanks @ReubenFrankel!**_

### 🐛 Fixes

- [#7878](https://github.com/meltano/meltano/issues/7878) Redact sensitive values in `config list` output -- _**Thanks @ReubenFrankel!**_
- [#7725](https://github.com/meltano/meltano/issues/7725) Restrict Azure state logging to WARNING and above -- _**Thanks @acarter24!**_
- [#7745](https://github.com/meltano/meltano/issues/7745) Python code formatting in Custom Extractor docs -- _**Thanks @rawwar!**_

### ⚡ Performance Improvements

- [#7811](https://github.com/meltano/meltano/issues/7811) Optimize migration 6828cc5b1a4f_create_dedicated_state_table.py -- _**Thanks @asmisha!**_

### 📚 Documentation Improvements

- [#7911](https://github.com/meltano/meltano/issues/7911) Advanced docs on running custom scripts
- [#7917](https://github.com/meltano/meltano/issues/7917) Update instructions for providing `GIT_SSH_PRIVATE_KEY`
- [#7906](https://github.com/meltano/meltano/issues/7906) Recommend airflow utility over orchestrator
- [#7892](https://github.com/meltano/meltano/issues/7892) Fix onboarding.md config command
- [#7668](https://github.com/meltano/meltano/issues/7668) Document `meltano-cloud job stop`
- [#7837](https://github.com/meltano/meltano/issues/7837) Update environment example to be more complete
- [#7836](https://github.com/meltano/meltano/issues/7836) Add more detail for cloud history command
- [#7817](https://github.com/meltano/meltano/issues/7817) Update Meltano Cloud notice in Deployment doc
- [#7823](https://github.com/meltano/meltano/issues/7823) Add cloud deployment hints for common errors
- [#7816](https://github.com/meltano/meltano/issues/7816) Remove Kubernetes reference from Production doc
- [#7822](https://github.com/meltano/meltano/issues/7822) Fix plural deployments cli command
- [#7807](https://github.com/meltano/meltano/issues/7807) Update schedule interval with single quotes
- [#7795](https://github.com/meltano/meltano/issues/7795) Add note on ephemeral storage
- [#7758](https://github.com/meltano/meltano/issues/7758) Cloud docs content and better navigation from index
- [#7783](https://github.com/meltano/meltano/issues/7783) Part3 getting started guide dbt initialize section
- [#7782](https://github.com/meltano/meltano/issues/7782) Use `--interactive` flag in Loader configuration section of Getting Started
- [#7780](https://github.com/meltano/meltano/issues/7780) Fix indentation issue for code block in Getting Started
- [#7619](https://github.com/meltano/meltano/issues/7619) 7186: change transform to utility
- [#7765](https://github.com/meltano/meltano/issues/7765) Use tabs for meltano.yml vs meltano config or env -- _**Thanks @mjsqu!**_
- [#7764](https://github.com/meltano/meltano/issues/7764) Explain Cloud schedule offsets
- [#7763](https://github.com/meltano/meltano/issues/7763) Make quoting consistent for intervals
- [#7754](https://github.com/meltano/meltano/issues/7754) Update deployment details
- [#7753](https://github.com/meltano/meltano/issues/7753) Update `project use` to include `--name` flag
- [#7750](https://github.com/meltano/meltano/issues/7750) Update `onboarding.md` to use `--environment` kwarg for deployments -- _**Thanks @GJMcClintock!**_
- [#7744](https://github.com/meltano/meltano/issues/7744) Fix `mappers.md` sample command

## v2.19.1 (2023-06-02)

### 🐛 Fixes

- [#7644](https://github.com/meltano/meltano/issues/7644) Install schedule elt style and mappings
- [#7636](https://github.com/meltano/meltano/issues/7636) Print a clearer message when `meltano.yml` is empty -- _**Thanks @rawwar!**_

### 📚 Documentation Improvements

- [#7732](https://github.com/meltano/meltano/issues/7732) Update Meltano Cloud GitHub App Installation Docs
- [#7717](https://github.com/meltano/meltano/issues/7717) Update onboarding docs
- [#7724](https://github.com/meltano/meltano/issues/7724) Add Cloud CLI docs for `deployment` command
- [#7722](https://github.com/meltano/meltano/issues/7722) Add credit pricing, clarify expiration
- [#7713](https://github.com/meltano/meltano/issues/7713) Spelling oopsie -- _**Thanks @visch!**_
- [#7706](https://github.com/meltano/meltano/issues/7706) Add egress pricing and Credit expiration (after 1 year of non-use) to Cloud Fees
- [#7703](https://github.com/meltano/meltano/issues/7703) Correct name of meltano-map-transformer in add command -- _**Thanks @mjsqu!**_
- [#7702](https://github.com/meltano/meltano/issues/7702) Fix typo in `docs/src/_guide/integration.md` -- _**Thanks @burmecia!**_
- [#7694](https://github.com/meltano/meltano/issues/7694) Add cloud python version
- [#7678](https://github.com/meltano/meltano/issues/7678) Refresh getting started guide
- [#7630](https://github.com/meltano/meltano/issues/7630) Add details on platinum connectors
- [#7639](https://github.com/meltano/meltano/issues/7639) Promote `pipx` to install Meltano

## v2.19.0 (2023-05-02)

### ✨ New

- [#7609](https://github.com/meltano/meltano/issues/7609) Support arm64 Meltano Docker image -- _**Thanks @space192!**_
- [#7594](https://github.com/meltano/meltano/issues/7594) Install plugins using schedule name

## v2.18.0 (2023-04-25)

### ✨ New

- [#7555](https://github.com/meltano/meltano/issues/7555) Add docs command
- [#7097](https://github.com/meltano/meltano/issues/7097) Feature flag to disable calls to Hub and `discovery.yml` outside of `add` and `discover`

### 🐛 Fixes

- [#7537](https://github.com/meltano/meltano/issues/7537) Add correct type for state_backend lock settings

### 📚 Documentation Improvements

- [#7585](https://github.com/meltano/meltano/issues/7585) Updates for Meltano Cloud GitHub App permissions and remove Alpha references
- [#7582](https://github.com/meltano/meltano/issues/7582) Include fix for git+ssh urls with colons -- _**Thanks @acarter24!**_
- [#7579](https://github.com/meltano/meltano/issues/7579) Change "meltano cloud" to "meltano-cloud" during Beta
- [#7571](https://github.com/meltano/meltano/issues/7571) Remove dead link to GitLab container registry -- _**Thanks @longtomjr!**_
- [#7566](https://github.com/meltano/meltano/issues/7566) Remove references to --include-related -- _**Thanks @msardana94!**_
- [#7545](https://github.com/meltano/meltano/issues/7545) Update link to Meltano dbt Jaffle shop example -- _**Thanks @flexponsive!**_
- [#7482](https://github.com/meltano/meltano/issues/7482) Add the Matatika GitHub Analytics project to the example projects page -- _**Thanks @DanielPDWalker!**_

## v2.17.1 (2023-04-04)

### 🐛 Fixes

- [#7403](https://github.com/meltano/meltano/issues/7403) Print right variant name in instructions to switch a plugin variant
- [#7399](https://github.com/meltano/meltano/issues/7399) Display the right message when adding a new variant of an existing plugin

### 📚 Documentation Improvements

- [#7469](https://github.com/meltano/meltano/issues/7469) Add Cloud Fees stub
- [#7466](https://github.com/meltano/meltano/issues/7466) Yaml snippets for Cloud quickstart
- [#7462](https://github.com/meltano/meltano/issues/7462) Update Cloud onboarding docs
- [#7457](https://github.com/meltano/meltano/issues/7457) Change link color from pink to blue
- [#7452](https://github.com/meltano/meltano/issues/7452) Fix two broken links to example repo
- [#7450](https://github.com/meltano/meltano/issues/7450) Update branding
- [#7433](https://github.com/meltano/meltano/issues/7433) Document incremental replication support
- [#7428](https://github.com/meltano/meltano/issues/7428) Add Cloud Docs
- [#7394](https://github.com/meltano/meltano/issues/7394) Add mappers docs guide
- [#7385](https://github.com/meltano/meltano/issues/7385) Redirect for dbt migration guide

## v2.17.0 (2023-03-14)

### ✨ New

- [#7343](https://github.com/meltano/meltano/issues/7343) Support arrow key text navigation during interactive config

### 🐛 Fixes

- [#7371](https://github.com/meltano/meltano/issues/7371) `meltano install --parallelism` error
- [#7367](https://github.com/meltano/meltano/issues/7367) Resolve variant label from Hub response
- [#7358](https://github.com/meltano/meltano/issues/7358) Add error and log for locking unknown plugins

### 📚 Documentation Improvements

- [#7364](https://github.com/meltano/meltano/issues/7364) Part2 gsg refresh target-postgres for meltanolabs

## v2.16.1 (2023-02-24)

### 🐛 Fixes

- [#7347](https://github.com/meltano/meltano/issues/7347) Error in `meltano add` when using env var proxies (e.g. `HTTP_PROXY`)
- [#7344](https://github.com/meltano/meltano/issues/7344) Improve config JSON array/object error message and parser

## v2.16.0 (2023-02-21)

### ✨ New

- [#7287](https://github.com/meltano/meltano/issues/7287) Add support for `annotations` to provide documentation and 3rd-party configurations in `meltano.yml`
- [#7148](https://github.com/meltano/meltano/issues/7148) Add the `meltano compile` command to generate Meltano manifest files

### 🐛 Fixes

- [#7331](https://github.com/meltano/meltano/issues/7331) Merge environment-level annotations into top level in manifest
- [#7320](https://github.com/meltano/meltano/issues/7320) Correct trimming of state backend URIs for filesystem backends
- [#7299](https://github.com/meltano/meltano/issues/7299) Respect `requests`/`curl` custom Certificate Authorities env vars

### ⚙️ Under the Hood

- [#7273](https://github.com/meltano/meltano/issues/7273) Add `settings` and `plugins` attributes to `Project`

### 📚 Documentation Improvements

- [#7322](https://github.com/meltano/meltano/issues/7322) State that the `meltano compile` command is in beta
- [#7329](https://github.com/meltano/meltano/issues/7329) Update airbyte FAQ
- [#7315](https://github.com/meltano/meltano/issues/7315) Escaping `$` in `meltano config <plugin> set`
- [#7301](https://github.com/meltano/meltano/issues/7301) Refresh to prefer 'run' and 'invoke' over 'elt', and 'utilities' over 'transformers' and 'orchestrators'

## v2.15.3 (2023-02-09)

### 🐛 Fixes

- [#7294](https://github.com/meltano/meltano/issues/7294) Avoid casting settings before env var expansion

### 📚 Documentation Improvements

- [#7050](https://github.com/meltano/meltano/issues/7050) Add "variant" prompt and description to custom plugin development docs
- [#7292](https://github.com/meltano/meltano/issues/7292) Fix typo in settings reference

## v2.15.2 (2023-02-08)

### 🐛 Fixes

- [#7284](https://github.com/meltano/meltano/issues/7284) Use `$MELTANO_ENVIRONMENT` set in `.env`
- [#7232](https://github.com/meltano/meltano/issues/7232) Cast setting values according to their setting definitions
- [#7213](https://github.com/meltano/meltano/issues/7213) Omit local variables in `rich` tracebacks by default and add `show_locals` option to log formatter

### 📚 Documentation Improvements

- [#7282](https://github.com/meltano/meltano/issues/7282) Add headers to global config section
- [#7279](https://github.com/meltano/meltano/issues/7279) Change ref
- [#7276](https://github.com/meltano/meltano/issues/7276) Correct small typo in `no-color.org` URL -- _**Thanks @menzenski!**_
- [#7274](https://github.com/meltano/meltano/issues/7274) Add links to glossary
- [#7239](https://github.com/meltano/meltano/issues/7239) Add EDK details and context around switching to utilities
- [#7258](https://github.com/meltano/meltano/issues/7258) Fix `virtualenvs.in-project` setting in custom extractor debugging doc -- _**Thanks @chodera!**_

## v2.15.1 (2023-01-31)

### 🐛 Fixes

- [#7236](https://github.com/meltano/meltano/issues/7236) Invoke `virtualenv` as a module
- [#7235](https://github.com/meltano/meltano/issues/7235) Avoid adding `LICENSE` file directly in `site-packages`

## v2.15.0 (2023-01-30)

### ✨ New

- [#7210](https://github.com/meltano/meltano/issues/7210) Support Python 3.11
- [#7198](https://github.com/meltano/meltano/issues/7198) Replace `venv` with `virtualenv`

### 🐛 Fixes

- [#7212](https://github.com/meltano/meltano/issues/7212) Do not log env vars passed to subprocesses

## v2.14.0 (2023-01-23)

### 🐛 Fixes

- [#7104](https://github.com/meltano/meltano/issues/7104) Support default boto3 auth for S3 state backend when AWS creds are unconfigured
- [#7174](https://github.com/meltano/meltano/issues/7174) Support default auth for GCS and Azure state backends
- [#7190](https://github.com/meltano/meltano/issues/7190) Make fully missing env var settings `None`

### ⚙️ Under the Hood

- [#7182](https://github.com/meltano/meltano/issues/7182) Use JSONschema version `draft-2020-12` for `meltano.yml` & `discovery.yml`
- [#7169](https://github.com/meltano/meltano/issues/7169) Use `$defs` instead of `definitions` in jsonschemas
- [#7188](https://github.com/meltano/meltano/issues/7188) Add header with Meltano command to Hub request

### 📚 Documentation Improvements

- [#7187](https://github.com/meltano/meltano/issues/7187) Fix YAML indent on getting started page and fix link to page source in GitHub -- _**Thanks @jx2lee!**_
- [#6699](https://github.com/meltano/meltano/issues/6699) Update `dbt` x `airflow` example project description
- [#7177](https://github.com/meltano/meltano/issues/7177) Add codespaces links to nav and ind

## v2.13.0 (2023-01-06)

### ✨ New

- [#7105](https://github.com/meltano/meltano/issues/7105) Support `meltano init` in a non-empty dir
- [#7115](https://github.com/meltano/meltano/issues/7115) Allow top-level annotations in `meltano.yml`
- [#7123](https://github.com/meltano/meltano/issues/7123) Optionally ignore missing env vars during expansion

### 🐛 Fixes

- [#7145](https://github.com/meltano/meltano/issues/7145) Setting nested setting key no longer clears sibling keys
- [#7120](https://github.com/meltano/meltano/issues/7120) Support str values when deep-merging config
- [#7144](https://github.com/meltano/meltano/issues/7144) Check system database version compatibility before migrations

### ⚙️ Under the Hood

- [#7069](https://github.com/meltano/meltano/issues/7069) Use a custom build backend

### 📚 Documentation Improvements

- [#7139](https://github.com/meltano/meltano/issues/7139) Add Airbyte Source Connector FAQ
- [#7140](https://github.com/meltano/meltano/issues/7140) Remove references to deprecated `MELTANO_CLI_*` aliases

## v2.12.0 (2022-12-19)

### 🐛 Fixes

- [#7093](https://github.com/meltano/meltano/issues/7093) Add missing description to environment context schema
- [#7084](https://github.com/meltano/meltano/issues/7084) Display better errors when failing to connect with the Hub API
- [#7078](https://github.com/meltano/meltano/issues/7078) Remove explicit aliases for S3 state backend

### ⚡ Performance Improvements

- [#7091](https://github.com/meltano/meltano/issues/7091) Compile env var pattern only once

### 📚 Documentation Improvements

- [#7089](https://github.com/meltano/meltano/issues/7089) Fix typo `tap-postgres` -> `postgres` -- _**Thanks @visch!**_
- [#7090](https://github.com/meltano/meltano/issues/7090) Fix config name for poetry -- _**Thanks @adherr!**_
- [#7088](https://github.com/meltano/meltano/issues/7088) Update banner copy & cta

## v2.11.1 (2022-12-09)

### 🐛 Fixes

- [#7057](https://github.com/meltano/meltano/issues/7057) Ensure `environment_name_hash` is collected
- [#7064](https://github.com/meltano/meltano/issues/7064) Misc `meltano.yml` schema fixes

## v2.11.0 (2022-12-08)

### ✨ New

- [#7019](https://github.com/meltano/meltano/issues/7019) Support env vars in plugin `pip_url`
- [#6995](https://github.com/meltano/meltano/issues/6995) `meltano install --force`

### 🐛 Fixes

- [#6873](https://github.com/meltano/meltano/issues/6873) Correct migration downgrade for 2.7.1 release
- [#7026](https://github.com/meltano/meltano/issues/7026) Permit `env` under plugins in `meltano.yml` schema
- [#7022](https://github.com/meltano/meltano/issues/7022) Pin `setuptools==57.5.0` in plugin venvs
- [#7017](https://github.com/meltano/meltano/issues/7017) Remove premature deserialization of settings in the CLI
- [#7010](https://github.com/meltano/meltano/issues/7010) Re-create plugin venv if Python executable is missing
- [#6997](https://github.com/meltano/meltano/issues/6997) Correct meltano config behavior when explicit environment is provided
- [#6986](https://github.com/meltano/meltano/issues/6986) List strings instead of enum objects as CLI options

### 📚 Documentation Improvements

- [#7046](https://github.com/meltano/meltano/issues/7046) Fix internal links and `meltano config` example code block in state backends page
- [#7041](https://github.com/meltano/meltano/issues/7041) Expand UI deprecation description -- _**Thanks @qbatten!**_
- [#7044](https://github.com/meltano/meltano/issues/7044) Add star donation blurb to readme
- [#7043](https://github.com/meltano/meltano/issues/7043) Add december campaign banner
- [#7030](https://github.com/meltano/meltano/issues/7030) Env var expansion within `pip_url`
- [#7035](https://github.com/meltano/meltano/issues/7035) Update custom extractor Poetry instructions -- _**Thanks @EMCP!**_
- [#7014](https://github.com/meltano/meltano/issues/7014) Add more project links to PyPI page
- [#7012](https://github.com/meltano/meltano/issues/7012) Complete list of commands that run with environment flag
- [#7002](https://github.com/meltano/meltano/issues/7002) Add docs for state backend migration

## v2.10.0 (2022-11-16)

### ✨ New

- [#6911](https://github.com/meltano/meltano/issues/6911) Remote state backends

### 🐛 Fixes

- [#6971](https://github.com/meltano/meltano/issues/6971) Correct strict_env_var_mode flag check in plugin configs
- [#6935](https://github.com/meltano/meltano/issues/6935) Persist `description` and `logo_url` to plugin lock files -- _**Thanks @DanielPDWalker!**_

### 📚 Documentation Improvements

- [#6984](https://github.com/meltano/meltano/issues/6984) Fix tap-github
- [#6955](https://github.com/meltano/meltano/issues/6955) Remove UI docs
- [#6977](https://github.com/meltano/meltano/issues/6977) Link to Meltano Cloud from Production doc

## v2.9.0 (2022-11-08)

### ✨ New

- [#6964](https://github.com/meltano/meltano/issues/6964) Add `--cwd` CLI option
- [#6785](https://github.com/meltano/meltano/issues/6785) Use `NO_COLOR` env var to disable colored output
- [#6628](https://github.com/meltano/meltano/issues/6628) Make `.meltano` folder path configurable via new `MELTANO_SYS_DIR_ROOT` env var -- _**Thanks @rawwar!**_

### 🐛 Fixes

- [#6938](https://github.com/meltano/meltano/issues/6938) Handle case where setting metadata is `None`
- [#6468](https://github.com/meltano/meltano/issues/6468) Symbolic link creation for meltano.exe when on windows -- _**Thanks @BuzzCutNorman!**_

### 📚 Documentation Improvements

- [#6961](https://github.com/meltano/meltano/issues/6961) Fix typo "differe" -> "different" -- _**Thanks @kayakr!**_
- [#6948](https://github.com/meltano/meltano/issues/6948) Add additional plugin definition ref entries -- _**Thanks @pandemicsyn!**_
- [#6951](https://github.com/meltano/meltano/issues/6951) Reindent code block -- _**Thanks @jx2lee!**_
- [#6887](https://github.com/meltano/meltano/issues/6887) Exclude little t from docs
- [#6923](https://github.com/meltano/meltano/issues/6923) Make clear you can override `executable` in `commands`

## v2.8.0 (2022-10-17)

### ✨ New

- [#6814](https://github.com/meltano/meltano/issues/6814) Support `meltano init` into an empty directory -- _**Thanks @ReubenFrankel!**_

### 🐛 Fixes

- [#6891](https://github.com/meltano/meltano/issues/6891) Interactive config for plugins with no settings
- [#6877](https://github.com/meltano/meltano/issues/6877) Make default `default_environment` null
- [#6862](https://github.com/meltano/meltano/issues/6862) Ignore default environment for some commands
- [#6751](https://github.com/meltano/meltano/issues/6751) Catch ConnectionError in /version endpoint -- _**Thanks @dingobar!**_

### 📚 Documentation Improvements

- [#6880](https://github.com/meltano/meltano/issues/6880) Add update pip to install
- [#6875](https://github.com/meltano/meltano/issues/6875) Add common problems
- [#6703](https://github.com/meltano/meltano/issues/6703) Update custom extractor tutorial -- _**Thanks @jared-rimmer!**_
- [#6852](https://github.com/meltano/meltano/issues/6852) Add giffy to title
- [#6844](https://github.com/meltano/meltano/issues/6844) Update `2.5.0` changelog to reflect breaking change

## v2.7.2 (2022-10-03)

### 🐛 Fixes

- [#6819](https://github.com/meltano/meltano/issues/6819) Fix error on `meltano config meltano set ...`
- [#6818](https://github.com/meltano/meltano/issues/6818) Avoid SQLAlchemy deprecation warning

### 📚 Documentation Improvements

- [#6822](https://github.com/meltano/meltano/issues/6822) Remove E(t)LT from tutorial
- [#6800](https://github.com/meltano/meltano/issues/6800) Shorten install quick start, move rest to guide
- [#6809](https://github.com/meltano/meltano/issues/6809) Tutorial small cleanup
- [#6781](https://github.com/meltano/meltano/issues/6781) Add parts 2-4 to the tutorial
- [#6801](https://github.com/meltano/meltano/issues/6801) Fix broken link

## v2.7.1 (2022-09-27)

### 🐛 Fixes

- [#6797](https://github.com/meltano/meltano/issues/6797) Show appropriate UI toasts
- [#6795](https://github.com/meltano/meltano/issues/6795) Correct migration path for state table

### 📚 Documentation Improvements

- [#6791](https://github.com/meltano/meltano/issues/6791) Remove datahub docs from guide

## v2.7.0 (2022-09-23)

### ✨ New

- [#6758](https://github.com/meltano/meltano/issues/6758) Support custom state IDs in `meltano run` with `--state-id-suffix` -- _**Thanks @ReubenFrankel!**_
- [#6756](https://github.com/meltano/meltano/issues/6756) Place `project_id` before `environments` in initial `meltano.yml`

### 🐛 Fixes

- [#6783](https://github.com/meltano/meltano/issues/6783) Remove "disable telemetry" toast from the UI
- [#6779](https://github.com/meltano/meltano/issues/6779) Use v1.0.1 of the `exit_event` Snowplow telemetry schema
- [#6745](https://github.com/meltano/meltano/issues/6745) Use random UUID as default `project_id`

### ⚙️ Under the Hood

- [#6748](https://github.com/meltano/meltano/issues/6748) Define and recommend `MeltanoError` exception class for improved CLI error messages

### 📚 Documentation Improvements

- [#6709](https://github.com/meltano/meltano/issues/6709) Add DataHub HowTo
- [#6764](https://github.com/meltano/meltano/issues/6764) Move installation guide to "Getting Started" add Part 1 tutorial
- [#6769](https://github.com/meltano/meltano/issues/6769) Guide for existing dbt projects
- [#6737](https://github.com/meltano/meltano/issues/6737) Add getting started section
- [#6753](https://github.com/meltano/meltano/issues/6753) Add list of video tuts and demos
- [#6739](https://github.com/meltano/meltano/issues/6739) Add how to jupyter
- [#6752](https://github.com/meltano/meltano/issues/6752) Shrink contrib. docs in sidebar to 1p
- [#6743](https://github.com/meltano/meltano/issues/6743) Describe how `project_id` is hashed

## v2.6.0 (2022-09-12)

### ✨ New

- [#5892](https://github.com/meltano/meltano/issues/5892) Add `--interactive` CLI flag in `meltano config set`.
- [#6640](https://github.com/meltano/meltano/issues/6640) Add rich exception formatting, configurable from `logging.yaml`.

### 🐛 Fixes

- [#6694](https://github.com/meltano/meltano/issues/6694) Regression in `meltano remove` with error stating the plugin is missing the `settings_with_extras` attribute.
- [#6652](https://github.com/meltano/meltano/issues/6652) Catch permission errors when creating a new project -- _**Thanks @jakegut!**_
- [#6676](https://github.com/meltano/meltano/issues/6676) Prevent warnings/errors when running `meltano config <plugin> test` -- _**Thanks @ReubenFrankel!**_

### 📚 Documentation Improvements

- [#6706](https://github.com/meltano/meltano/issues/6706) Add troubleshooting page -- _**Thanks @jared-rimmer!**_
- [#6688](https://github.com/meltano/meltano/issues/6688) Add docs about environment variable expansion.
- [#6671](https://github.com/meltano/meltano/issues/6671) Add example meltano projects.
- [#6674](https://github.com/meltano/meltano/issues/6674) Add docs for schedule `env` key.
- [#6680](https://github.com/meltano/meltano/issues/6680) Fix feature flag name for strict env var mode.
- [#6672](https://github.com/meltano/meltano/issues/6672) Add tutorial on how to debug a custom extractor -- _**Thanks @jared-rimmer!**_

## v2.5.0 (2022-08-24)

### BREAKING CHANGES

- [#6582](https://github.com/meltano/meltano/issues/6582) Make `default_environment` a top-level setting

  Running `meltano environment add dev` as a one-time fix will resolve the issue, even if no other changes are made and no environment-specific settings are added.
  _Note: This breaking change was added inadvertently in this version. We do not intend to release breaking changes in minor versions and have added this notice retroactively. _

### ✨ New

- [#6596](https://github.com/meltano/meltano/issues/6596) Support glob paths in file plugin `update` extra
- [#6578](https://github.com/meltano/meltano/issues/6578) Add `--no-install` option to `meltano add`

### 🐛 Fixes

- [#6656](https://github.com/meltano/meltano/issues/6656) Correct STRICT_ENV_VAR_MODE behavior
- [#6627](https://github.com/meltano/meltano/issues/6627) Raise exception when meltano.yml is empty
- [#6643](https://github.com/meltano/meltano/issues/6643) Address `alter_column` warning for MSSQL
- [#6636](https://github.com/meltano/meltano/issues/6636) Use `docs.meltano.com` instead of `meltano.com/docs`
- [#6601](https://github.com/meltano/meltano/issues/6601) raise error on migration fail
- [#6609](https://github.com/meltano/meltano/issues/6609) `meltano state list` change pattern from argument to option
- [#6592](https://github.com/meltano/meltano/issues/6592) Validate CRON expressions
- [#6543](https://github.com/meltano/meltano/issues/6543) Register legacy `DiscoveryFile` object in Ruamel YAML instance
- [#6593](https://github.com/meltano/meltano/issues/6593) Docker workflow
- [#6584](https://github.com/meltano/meltano/issues/6584) Avoid `pyproject.toml` Poetry parsing issue

### ⚙️ Under the Hood

- [#6621](https://github.com/meltano/meltano/issues/6621) Make `ProjectInitService.init` generate/set a `project_id`
- [#6611](https://github.com/meltano/meltano/issues/6611) Use `closing` for DB sessions & add docstrings to `meltano.core.db`
- [#6610](https://github.com/meltano/meltano/issues/6610) Replace `StaleJobFailer` class with `fail_stale_jobs` function

### ⚡ Performance Improvements

- [#6644](https://github.com/meltano/meltano/issues/6644) Improve performance when handling large yaml files

### 📚 Documentation Improvements

- [#6663](https://github.com/meltano/meltano/issues/6663) update custom extractor tutorial to use pip_url
- [#6648](https://github.com/meltano/meltano/issues/6648) logging configuration guide
- [#6650](https://github.com/meltano/meltano/issues/6650) Update Custom Extractor tutorial to use an editable install
- [#6631](https://github.com/meltano/meltano/issues/6631) Add "Pytest Best Practices" section to contributing docs
- [#6602](https://github.com/meltano/meltano/issues/6602) Update `Docker` definition in `glossary.yml`

## v2.4.0 (2022-08-05)

### ✨ New

- [#5983](https://github.com/meltano/meltano/issues/5983) Add support for env var inheritance across config layers
- [!6167](https://github.com/meltano/meltano/pull/6167) Add systemdb support for MS SQL Server
- [#6494](https://github.com/meltano/meltano/issues/6494) **core**: Report how `send_anonymous_usage_stats` was configured
- [#6116](https://github.com/meltano/meltano/issues/6116) Ignore setting values when selecting store location and `store=auto`

### 🐛 Fixes

- [#6383](https://github.com/meltano/meltano/issues/6383) Test DB Creation when meltano install is ran
- [#6360](https://github.com/meltano/meltano/issues/6360) Lock plugins using the latest Hub definition if plugin has no variant name and no lock file exists
- [!6557](https://github.com/meltano/meltano/pull/6557) Remove broken unused method `PluginsTrackingContext.append_plugin_context`
- [#6532](https://github.com/meltano/meltano/issues/6532) **core**: Timeout Snowplow requests
- [#5982](https://github.com/meltano/meltano/issues/5982) **core**: Update env var tests to be in line with correct reading of spec
- [#6189](https://github.com/meltano/meltano/issues/6189) Validating Mapper and Mappings names and alerting if necessary
- [#6240](https://github.com/meltano/meltano/issues/6240) **ui**: When feature flag `enable_uvicorn` is true require write lock when accessing Project.meltano attribute
- [#6469](https://github.com/meltano/meltano/issues/6469) **deps**: Pin werkzeug to <2.2.0

### 📚 Documentation Improvements

- [!6535](https://github.com/meltano/meltano/pull/6535) Update broken doc link in `meltano.schema.json`
- [!6456](https://github.com/meltano/meltano/pull/6456) Update for Windows and for using pipx --python version
- [#6491](https://github.com/meltano/meltano/issues/6491) Update style doc to note that MyPy is not run in CI
- [#6107](https://github.com/meltano/meltano/issues/6107) Document YAML syntax for Hub plugins
- [!6465](https://github.com/meltano/meltano/pull/6465) Move 'v2 migration guide' under 'guides'

## v2.3.0 (2022-07-20)

### ✨ New

- [#6150](https://github.com/meltano/meltano/issues/6150) meltano now surfaces full stderr output for catalog discovery failures
- [#3419](https://github.com/meltano/meltano/issues/3419) Change default meltano config behavior to --no-environment
- [#2133](https://github.com/meltano/meltano/issues/2133) Preserve comments and flow style in `meltano.yml`
- [#6207](https://github.com/meltano/meltano/issues/6207) Add env as first-class attribute of MeltanoFile and ProjectPlugin classes (not an extra)

### 🐛 Fixes

- [#6188](https://github.com/meltano/meltano/issues/6188) Allow `meltano run` to run without providing subcommand
- [#6380](https://github.com/meltano/meltano/issues/6380) **core**: Extras of kind `object` not honored in inherited plugins
- [#3322](https://github.com/meltano/meltano/issues/3322) Extras of kind `object` not honored in environments
- [#6301](https://github.com/meltano/meltano/issues/6301) Swap add_related for add_required in api v1 plugins
- [#6359](https://github.com/meltano/meltano/issues/6359) Do not attempt to lock inherited plugins when using `meltano lock`
- [#6136](https://github.com/meltano/meltano/issues/6136) clarify job/task relation to airflow
- [#6234](https://github.com/meltano/meltano/issues/6234) Emit `RuntimeWarning` if a setting uses the default value
- [#6357](https://github.com/meltano/meltano/issues/6357) typo in `meltano-basics` example link
- [#6354](https://github.com/meltano/meltano/issues/6354) removed run preview references

### ⚙️ Under the Hood

- [#6324](https://github.com/meltano/meltano/issues/6324) update to automatically fire start AND end events

### 📚 Documentation Improvements

- [#6283](https://github.com/meltano/meltano/issues/6283) Document overriding capabilities and extending settings
- [#6420](https://github.com/meltano/meltano/issues/6420) Windows installation old gitlab link
- [#6367](https://github.com/meltano/meltano/issues/6367) Fix typo etl -> elt

## 2.2.0 - (2022-07-01)

---

### New

- [#2830](https://github.com/meltano/meltano/issues/2830) Add support for Python 3.10.
- [#3452](https://gitlab.com/meltano/meltano/-/issues/3452) Add `copy` and `move` commands to `meltano state`

### Changes

- [#3174](https://gitlab.com/meltano/meltano/-/issues/3174) We now recommend pipx over manually created virtual environments.
- [#3450](https://gitlab.com/meltano/meltano/-/issues/3450) Added installation instructions for Windows.
- [#3367](https://gitlab.com/meltano/meltano/-/issues/3367) Windows now covered in CI for some basic cases.
- [#3135](https://github.com/meltano/meltano/issues/3135) Formalize settings alias behavior and disallow conflicting values between setting name and aliases.
- [#2035](https://github.com/meltano/meltano/issues/2035) Rename `job` table and `job_id` column in backend db.

### Fixes

- [#5985](https://github.com/meltano/meltano/issues/5985) - Address warning in Airflow plugin version check by using recommended `packaging.version.Version`.

## 2.1.0 - (2022-06-17)

---

### New

- [#5961](https://github.com/meltano/meltano/issues/5961) - Add `meltano lock` command to create or update plugin lock artifacts.
- [#6199](https://github.com/meltano/meltano/pull/6199/) - Restore project_id from analytics.json & improve analytics.json handling.
- [#6203](https://github.com/meltano/meltano/pull/6203) - Fire exit event exactly once & include detailed exception context.
- [#6141](https://github.com/meltano/meltano/pull/6141) - Add tracking for job command.
- [#6137](https://github.com/meltano/meltano/pull/6137) - Add telemetry for meltano config.
- [#6114](https://github.com/meltano/meltano/pull/6114) - Add meltano lock.

### Changes

- [#3473](https://gitlab.com/meltano/meltano/-/issues/3473) - Python Virtual Environments advanced concept added to docs by splitting it out from the Installation instructions.

### Fixes

- [#6216](https://github.com/meltano/meltano/pull/6216) - Replace all `jobId` with `stateId` to fix pipeline running bug.

## 2.0.3 - (2022-06-15)

---

### Changes

- [#6186](https://github.com/meltano/meltano/pull/6186) Improve CLI startup performance

## 2.0.2 - (2022-06-14)

---

### Fixes

- [#6174](https://github.com/meltano/meltano/issues/6174) Fix issue where loading schedules could cause Meltano UI to crash.

### Docs

- [#6184](https://github.com/meltano/meltano/pull/6184) Bugfix in getting-started guide installation instructions - _Thanks, **[Martin Morset (@dingobar)](https://github.com/dingobar)**!_

### Misc

- [#6149](https://github.com/meltano/meltano/pull/6149),[#6142](https://github.com/meltano/meltano/pull/6142) Add anonymized telemetry handling for exceptions.

## 2.0.1 - (2022-06-09)

---

### Fixes

- [#6143](https://github.com/meltano/meltano/issues/6143) Resolve issue where Meltano UI would not start.

## 2.0.0 - (2022-06-08)

---

_**Meltano 2.0** is a major update with multiple new features and some breaking changes. See our [2.0 Migration Guide](https://docs.meltano.com/reference/v2-migration) for more information._

### New

- [#3283](https://github.com/meltano/meltano/issues/3208) Support `meltano add` directly from Hub.
- [#2924](https://gitlab.com/meltano/meltano/-/issues/2924) Add job support via new `meltano job` command and support for referencing jobs in `meltano run` commands.
- [#5923](https://github.com/meltano/meltano/pull/5923) Add support for jobs to schedules and improves general schedule cli UX.
- [#3348](https://github.com/meltano/meltano/issues/3348) Add [`env_var_strict_mode`](https://docs.meltano.com/reference/settings#ffenv_var_strict_mode) feature flag to raise an exception if unset environment variables are referenced in settings.
- [#6060](https://github.com/meltano/meltano/pull/6060) Generate lockfiles when running `meltano add` to install new plugins (now enabled by default).
- [#3355](https://github.com/meltano/meltano/pull/3355) New paradigm of explicit plugin dependencies using `requires:`, replaces implicitly "related" plugins.
- [#6033](https://github.com/meltano/meltano/pull/6033) Let plugin in `meltano.yml` override capabilities and extend settings of parent/lockfile.

### Changes

- [#5957](https://github.com/meltano/meltano/pull/5957) Remove the auto-add functionality that applied to transform plugins and plugins with matching `namespace`.
- [#6043](https://github.com/meltano/meltano/pull/6034) Let Meltano settings be stored under environments.

### Breaks

- [#3427](https://gitlab.com/meltano/meltano/-/issues/3427) Drop support for the legacy "Dashboards" and "Explore" UX in Meltano UI.
- [#3427](https://gitlab.com/meltano/meltano/-/issues/3427) Drop support for legacy `model` and `dashboard` plugin types.
- [#3048](https://github.com/meltano/meltano/issues/3048) Drop support for `env_aliases` feature and remove its references in `discovery.yml`.
- [#5957](https://github.com/meltano/meltano/pull/5957) Drop support for the `--include-related` CLI flag.

### Fixes

- [#5979](https://github.com/meltano/meltano/issues/5979) Fixes `meltano remove` bug where lock files were not removed if they include a variant in the file name.
- [#6015](https://github.com/meltano/meltano/issues/6015) Fixes a bug where `meltano config meltano set` would not always set a value.

### Under the Hood

- Improved [telemetry](https://handbook.meltano.com/data-team/telemetry#philosophy-of-telemetry) coverage across the product.

## 1.105.0 - (2022-05-19)

---

### New

- [#3298](https://gitlab.com/meltano/meltano/-/issues/3298) Add adapter-specific dbt plugins for Redshift, Postgres, and BigQuery.
- [#3482](https://gitlab.com/meltano/meltano/-/issues/3482) Expand project-set environment variables in Environment-level `env:`.

### Changes

- [#3174](https://gitlab.com/meltano/meltano/-/issues/3174) - We now recommend [pipx](https://pypa.github.io/pipx/) over manually created virtual environments.
- [#3484](https://gitlab.com/meltano/meltano/-/issues/3484) Use `SettingsService.feature_flag` convention for lockfiles.
- [#3447](https://gitlab.com/meltano/meltano/-/issues/3447) Make setting-level `env:` declaration a one-way injection into the plugin execution context.

### Fixes

- [#3483](https://gitlab.com/meltano/meltano/-/issues/3483) Fixes a bug where pipx installed meltano can not find executable(.exe) meltano dependency packages. _Thanks **[Dan Norman](https://gitlab.com/BuzzCutNorman)**!_
- [#3500](https://gitlab.com/meltano/meltano/-/issues/3500) Fixes bug where lock file was added but not used.

## 1.104.0 - (2022-05-13)

---

### New

- [#3031](https://gitlab.com/meltano/meltano/-/issues/3031) Add lock artifacts during `meltano add` for stability and portability of plugin definitions.

### Changes

- [#3385](https://gitlab.com/meltano/meltano/-/issues/3385) Add feature flags for experimental features

### Fixes

- [#3468](https://gitlab.com/meltano/meltano/-/issues/3468) Fixes bug where container spec's entrypoint was not passed along to the Docker runtime.

## 1.103.1 - (2022-05-05)

---

### Fixes

- [#3462](https://gitlab.com/meltano/meltano/-/issues/3462) Adds missing telemetry for `meltano state`

## 1.103.0 - (2022-05-05)

---

### New

- [#2490](https://gitlab.com/meltano/meltano/-/issues/2490) Inherited plugins with identical `pip_url` field values to parent now share a single venv.

### Changes

- [#3407](https://gitlab.com/meltano/meltano/-/issues/3407) Allow `--custom` when adding transformers.

### Fixes

- [#3446](https://gitlab.com/meltano/meltano/-/issues/3446) Fixes bug where `meltano run` could pass `None` as argument to a plugin command.

## 1.102.0 - (2022-04-28)

---

### New

- [#3146](https://gitlab.com/meltano/meltano/-/issues/3146) Add `--dry-run` option to `meltano run`.
- [#2754](https://gitlab.com/meltano/meltano/-/issues/2754) New `meltano state` command to manage job states.

### Fixes

- [#3392](https://gitlab.com/meltano/meltano/-/issues/3392) Fixes bug in meltano ui where pipelines tab would fail to load when a pipeline had no interval set.

## 1.101.0 - (2022-04-21)

---

### New

- [#3377](https://gitlab.com/meltano/meltano/-/issues/3377) Add active environment as variable `MELTANO_ENVIRONMENT` in Plugin execution environment.

### Fixes

- [#3405](https://gitlab.com/meltano/meltano/-/issues/3405) Add missing `database_uri` key to JSON schema for `meltano.yml`
- [#3406](https://gitlab.com/meltano/meltano/-/issues/3406) Add missing `plugins/mappers` key to JSON schema for `meltano.yml` and fix `mappings` key in mapper objects.
- [#3390](https://gitlab.com/meltano/meltano/-/issues/3390) Fixes bug where `meltano init` failed to create prerequisite directories.
- [#3391](https://gitlab.com/meltano/meltano/-/issues/3391) Fixes bug where `meltano run` would invoke the wrong plugin command when the same plugin was used multiple times.

## 1.100.0 - (2022-04-14)

---

### New

- [#3105](https://gitlab.com/meltano/meltano/-/issues/3105) Add a Snowflake-specific dbt plugin that uses the correspondent adapter.

### Fixes

- [#3373](https://gitlab.com/meltano/meltano/-/issues/3373) Add missing `default_environment` key to the JSON schema for `meltano.yml`.
- [#3324](https://gitlab.com/meltano/meltano/-/issues/3324) Change example git URL for custom plugin to a generic URL.

## 1.99.0 - (2022-04-01)

---

### New

- [#3103](https://gitlab.com/meltano/meltano/-/issues/3103) Allow users to set a default Environment in `meltano.yml`.
- [#3318](https://gitlab.com/meltano/meltano/-/issues/3318) `meltano init` will ask for a project_name if none is passed during invocation.
- [!2561](https://gitlab.com/meltano/meltano/-/merge_requests/2561) Add `dragon` command Easter egg.

### Fixes

- [#3233](https://gitlab.com/meltano/meltano/-/issues/3233) Fix issue related `meltano test` attempting to instantiate plugins that are not installed.
- [#3347](https://gitlab.com/meltano/meltano/-/issues/3347) Fix an issue in `meltano run` on python 3.7 where an AttributeError exception would occur while closing stdin of a spawned subprocess.
- [#3349](https://gitlab.com/meltano/meltano/-/issues/3349) Resolve missing `schedule` commands in anonymous usage tracking.
- [#3264](https://gitlab.com/meltano/meltano/-/issues/3264) Fix broken links to http://docs.meltano.com.

## 1.98.1 - (2022-03-14)

---

### Fixes

- [#3334](https://gitlab.com/meltano/meltano/-/issues/3334) Set the `executable` of `meltano-map-transformer` to `meltano-map-transform`.

## 1.98.0 - (2022-03-10)

---

### Changes

- [#3316](https://gitlab.com/meltano/meltano/-/issues/3316) Improve the `meltano init` experience with beautified text and cleaner logging
- [#3317](https://gitlab.com/meltano/meltano/-/issues/3317) Improve Snowplow documentation and simplify telemetry notification during `meltano init`
- [#3319](https://gitlab.com/meltano/meltano/-/issues/3319) Limit Snowplow tracker logs to the command line to `ERROR` level by default.
- [#3217](https://gitlab.com/meltano/meltano/-/issues/3217) Allow user to configure Sendgrid asm*group_id. \_Thanks, **[@davesgonechina](https://gitlab.com/davesgonechina)**!*
- [#3321](https://gitlab.com/meltano/meltano/-/issues/3321) Switch Snowplow tracker endpoint to `https`.

### Fixes

- [#3306](https://gitlab.com/meltano/meltano/-/issues/3306) Fix Environments bug where custom configuration values that were not defined either as a setting or custom configuration in the primary plugin definition were not passed to the plugin in the Environment context.

## 1.97.0 - (2022-03-03)

---

### New

- [#2527](https://gitlab.com/meltano/meltano/-/issues/2527), [#2528](https://gitlab.com/meltano/meltano/-/issues/2528) Add CRON interval mechanism and modal to `/pipelines` page.
- [#3017](https://gitlab.com/meltano/meltano/-/issues/3017) Add Snowplow Tracking to Meltano.
- [#3130](https://gitlab.com/meltano/meltano/-/issues/3130) Add support for incremental jobs to `meltano run`.

### Changes

- [#3282](https://gitlab.com/meltano/meltano/-/issues/3282) Expand `meltano elt` failure information to help new users find debug logging. _Thanks, **[Derek Visch](https://gitlab.com/vischous)**!_

### Fixes

- [#3289](https://gitlab.com/meltano/meltano/-/issues/3289) In `target-bigquery` default variant `adswerve`, set the default of the `merge_state_messages` setting to `false` so state objects are not merged by the target.
- [#3301](https://gitlab.com/meltano/meltano/-/issues/3301) Fix a typo that causes requests to the `/install/batch` endpoint to fail.

## 1.96.0 - (2022-02-18)

---

### New

- [#2299](https://gitlab.com/meltano/meltano/-/issues/2299) Introduces stream map support for `meltano run` via a new Singer compatible Mapper plugin type.
- [#2205](https://gitlab.com/meltano/meltano/-/issues/2205) Add Docker support via a new `container_spec` option for plugin commands.
- [#2454](https://gitlab.com/meltano/meltano/-/issues/2454) Added support for the Great Expectations data validation utility.

### Changes

- [#3122](https://gitlab.com/meltano/meltano/-/issues/3122) Newly created Meltano projects are now initialized with default environments: `prod`, `staging`, and `dev`.

### Fixes

- [#3257](https://gitlab.com/meltano/meltano/-/issues/3257) Resolves installation failures by pinning `MarkupSafe` library version to `<2.1.0`.

## 1.95.0 - (2022-02-11)

---

### Changes

- [!2525](https://gitlab.com/meltano/meltano/-/merge_requests/2525) Updates the `discovery_url` default setting to use https://discovery.meltano.com/discovery.yml

### Fixes

- [#3190](https://gitlab.com/meltano/meltano/-/issues/3190) Fix `meltano test` bug where plugin name clashes with file bundle name

## 1.94.0 - (2022-02-04)

---

### New

- [#1587](https://gitlab.com/meltano/meltano/-/issues/1587) Add "Retry" button to pipeline logs view and list when run failed

## 1.93.0 - (2022-01-28)

---

### Changes

- [#3176](https://gitlab.com/meltano/meltano/-/issues/3176) Support dbt v1.0
- [!2504](https://gitlab.com/meltano/meltano/-/merge_requests/2504) Reorganized pipeline edit buttons in the UI
- [!2464](https://gitlab.com/meltano/meltano/-/merge_requests/2464) Bump version of 'flatten-dict' library dependency. _Thanks to **[Robin Grenholm](https://gitlab.com/rgrenholm)**_ !

### Fixes

- [#3181](https://gitlab.com/meltano/meltano/-/issues/3181) Create an empty `output/` folder in new Meltano projects.
- [#3180](https://gitlab.com/meltano/meltano/-/issues/3180) Fix env usage in discovery.yml and JSON schema
- [#3169](https://gitlab.com/meltano/meltano/-/issues/3169) Meltano Upgrade CTA in UI has unnecessary link

## 1.92.0 - (2022-01-21)

---

### Changes

- [#2991](https://gitlab.com/meltano/meltano/-/issues/2991) Remove support for python 3.6. Bumps the base docker image to 3.8.

### Fixes

- [#3024](https://gitlab.com/meltano/meltano/-/issues/3024) Make `meltano upgrade` work when Meltano is installed with pipx.
- [#3115](https://gitlab.com/meltano/meltano/-/issues/3115) Ensure multi-yaml `include_paths` are correctly referenced even if Meltano is not called from the root directory.
- [#3167](https://gitlab.com/meltano/meltano/-/issues/3167) Add sub-schema for meltano.yml environments.
- [#3024](https://gitlab.com/meltano/meltano/-/issues/3024) Make `meltano upgrade` work when Meltano is installed with pipx.
- [#3161](https://gitlab.com/meltano/meltano/-/issues/3161) Make URLs in `--help` clickable.

[#3161](https://gitlab.com/meltano/meltano/-/issues/3161) Make URLs in `--help` clickable.

## 1.91.0 - (2022-01-13)

---

### New

- [#3153](https://gitlab.com/meltano/meltano/-/issues/3153) Published JSON Schemas for `meltano.yml` and `discovery.yml`. _Thanks to **[Zachary Wynegar](https://gitlab.com/zdwynegar)** for the initial [MR 1804](https://gitlab.com/meltano/meltano/-/merge_requests/1804) and inspiration this!_
- [#3001](https://gitlab.com/meltano/meltano/-/issues/3001) Always print log advice on ELT failure.

### Fixes

- [#3132](https://gitlab.com/meltano/meltano/-/issues/3132) Bump `pyhumps` dependency to fix a bug in converting `SCREAMING_SNAKE_CASE` variables in the API.
- [#3116](https://gitlab.com/meltano/meltano/-/issues/3116) Fix a unicode decode issue during discovery when debug logging is enabled.
- [#2716](https://gitlab.com/meltano/meltano/-/issues/2716) Add `--help `docs for all Meltano CLI commands and options.

## 1.90.1 - (2021-12-16)

---

### Fixes

- [#3124](https://gitlab.com/meltano/meltano/-/issues/3124) Fix an error in `meltano run` invocations where tap discover calls triggered an exception.

## 1.90.0 - (2021-12-15)

---

### New

- [#2301](https://gitlab.com/meltano/meltano/-/issues/2301), [#3043](https://gitlab.com/meltano/meltano/-/issues/3043) Preview release of new [`meltano run`](https://docs.meltano.com/reference/command-line-interface#run) command.
- [#2838](https://gitlab.com/meltano/meltano/-/issues/2838) Adds the [`meltano test`](https://docs.meltano.com/reference/command-line-interface#test) command which defines first-class test and validation capabilities for Meltano plugins and projects.

### Changes

- [#2967](https://gitlab.com/meltano/meltano/-/issues/2967) Set the `meltanolabs` variant as the default tap-google-analytics extractor.
- [#3085](https://gitlab.com/meltano/meltano/-/issues/3085), [#3111](https://gitlab.com/meltano/meltano/-/issues/3111) Upgrade `target-bigquery` default variant `adswerve` to [`0.11.3`](https://github.com/adswerve/target-bigquery/releases/tag/0.11.3).
- [#3113](https://gitlab.com/meltano/meltano/-/issues/3113) Pin tag [`v1.4.27`](https://gitlab.com/meltano/tap-salesforce/-/tags/v1.4.27) of `tap-salesforce` default variant `meltano`.
- [#3119](https://gitlab.com/meltano/meltano/-/issues/3119) Bump `meltano` variant of `tap-salesforce` to tag [`v1.5.0`](https://gitlab.com/meltano/tap-salesforce/-/tags/v1.5.0).

## 1.89.0 - (2021-12-02)

---

### New

- [#3060](https://gitlab.com/meltano/meltano/-/issues/3060) Set `splitio` variant as the default tap-fastly extractor.
- [#3076](https://gitlab.com/meltano/meltano/-/issues/3076) Set `transferwise` as the default target-postgres loader.
- [#2967](https://gitlab.com/meltano/meltano/-/issues/2967) Set `meltanolabs` as the default tap-google-analytics extractor.

### Changes

- [#2772](https://gitlab.com/meltano/meltano/-/issues/2772) Transition to a new structured log format with support for additional formats like JSON and key=value, configurable via stock python logging yaml configs.
- [#2443](https://gitlab.com/meltano/meltano/-/issues/2443) Bump dbt version to 0.21.1

## 1.88.0 - (2021-11-18)

---

### New

- [#3021](https://gitlab.com/meltano/meltano/-/issues/3021) Added CLI for high-level Environment management.

- [#3003](https://gitlab.com/meltano/meltano/-/issues/3003) Add `matatika` variant of tap-solarvista extractor.

## 1.87.1 - (2021-11-09)

---

### Changes

- [#3042](https://gitlab.com/meltano/meltano/-/issues/3042) Hides non-default `meltano` variants from the UI.

### Fixes

- [#3015](https://gitlab.com/meltano/meltano/-/issues/3015) Add missing settings to default target-snowflake: `role`, `batch_wait_limit_seconds`, `archive_load_files`, `archive_load_files_s3_prefix`, and `archive_load_files_s3_bucket`
- [#3047](https://gitlab.com/meltano/meltano/-/issues/3047) Don't fail if primary `meltano.yml` file is missing top-level entries.
- [#3049](https://gitlab.com/meltano/meltano/-/issues/3049) Fix installation issues caused by breaking change in WTForms library v3.0.x.

## 1.87.0 - (2021-11-05)

---

### New

- [#2456](https://gitlab.com/meltano/meltano/-/issues/2456) Let project plugin definitions and config be defined in multiple individual YAML files. _Thanks, **[Matthew Thurman](https://gitlab.com/mathurmag)** for the inspiration and first draft!_

### Breaks

- [#2977](https://gitlab.com/meltano/meltano/-/issues/2977) Disable the Explore and Dashboards tabs in the UI by default.

## 1.86.0 - (2021-10-28)

---

### New

- [#2869](https://gitlab.com/meltano/meltano/-/issues/2869) Introduce top-level "Environments" within `meltano.yml`

### Changes

- [#2968](https://gitlab.com/meltano/meltano/-/issues/2968) Set `singer-io` as the default tap-marketo extractor.
- [#2970](https://gitlab.com/meltano/meltano/-/issues/2970) Set `singer-io` as the default tap-stripe extractor.
- [#2971](https://gitlab.com/meltano/meltano/-/issues/2971) Set `meltanolabs` as the default target-sqlite loader.

### Fixes

- [#3027](https://gitlab.com/meltano/meltano/-/issues/3027) Fixes an issue where elt invocation could hang if the tap produced large amounts of error output during discovery.

## 1.85.0 - (2021-10-21)

---

### Changes

- [#2986](https://gitlab.com/meltano/meltano/-/issues/2986) Set `transferwise` as the default target-snowflake loader.
- [#2966](https://gitlab.com/meltano/meltano/-/issues/2966) Set `singer-io` as the default tap-adwords extractor.
- [#2964](https://gitlab.com/meltano/meltano/-/issues/2964) Set `singer-io` as the default tap-facebook extractor.
- [#2963](https://gitlab.com/meltano/meltano/-/issues/2963) Set `meltanolabs` as the default tap-csv extractor.
- [#2965](https://gitlab.com/meltano/meltano/-/issues/2965) Set `meltanolabs` as the default tap-gitlab extractor.
- [2339](https://gitlab.com/meltano/meltano/-/merge_requests/2339) Update `elt` log format to include subtask field. Lines are now prefixed with `<name> | <subtask>` which may cause issues with existing log parsers.

### Fixes

- [#2997](https://gitlab.com/meltano/meltano/-/issues/2997) Bump required version of `jsonschema`.

## 1.84.0 - (2021-10-07)

---

### New

- [#2357](https://gitlab.com/meltano/meltano/-/merge_requests/2357) Use dbt [`v0.21.0`](https://github.com/dbt-labs/dbt/releases/tag/v0.21.0) by default for new dbt installs
- [2363](https://gitlab.com/meltano/meltano/-/merge_requests/2363), [2360](https://gitlab.com/meltano/meltano/-/merge_requests/2360) Small branding and logo updates throughout - and introducing Melty to the community!

### Fixes

- [2349](https://gitlab.com/meltano/meltano/-/merge_requests/2349) Fixes test extractor API endpoint to work with new PluginTestService. _Thanks, **[ReubenFrankel](https://gitlab.com/ReubenFrankel)**!_

## 1.83.0 - (2021-09-30)

---

### New

- [#2647](https://gitlab.com/meltano/meltano/-/issues/2647) Extend `meltano select` with flag to remove rules.

## 1.82.0 - (2021-09-23)

---

### Changes

- [#2782](https://gitlab.com/meltano/meltano/-/issues/2782) Switches all extractors and loaders in discovery.yml to `variants` syntax
- [#2950](https://gitlab.com/meltano/meltano/-/issues/2950) Update werkzeug to `2.0`. _Thanks, **[Keith Siilats](https://gitlab.com/siilats)**!_

### Fixes

- [#2881](https://gitlab.com/meltano/meltano/-/issues/2881) Send CLI error messages to `stderr`.

## 1.81.0 - (2021-09-16)

---

### New

- [#2609](https://gitlab.com/meltano/meltano/-/issues/2609) Add `meltano config <plugin> test` command to test an extractor plugin's configuration. _Thanks, **[ReubenFrankel](https://gitlab.com/ReubenFrankel)**!_

### Changes

- [#2930](https://gitlab.com/meltano/meltano/-/issues/2930) Update sqlfluff configuration to support DBT. _Thanks, **[Charles Julian Knight](https://gitlab.com/rabidaudio)**!_
- [#2681](https://gitlab.com/meltano/meltano/-/issues/2681) Now includes discovery log output when running `meltano elt` with `--log-level=debug`

### Fixes

- [#2866](https://gitlab.com/meltano/meltano/-/issues/2866) Avoid running discovery when invoking a tap in a mode other than sync

## 1.80.1 - (2021-09-10)

---

### Fixes

- [#2928](https://gitlab.com/meltano/meltano/-/issues/2928) Fix tap discovery failure when tap produces IO on stderr

## 1.80.0 - (2021-09-09)

---

### New

- [#2906](https://gitlab.com/meltano/meltano/-/issues/2906) Increase speed of `meltano install` for already installed plugins

* [#2906](https://gitlab.com/meltano/meltano/-/issues/2906) Increase speed of `meltano install` for already installed plugins

### Changes

- [#2897](https://gitlab.com/meltano/meltano/-/issues/2897) Refactor to move to asynchronous plugin executions and invocations

### Fixes

- [#2573](https://gitlab.com/meltano/meltano/-/issues/2573) Fix misleading error about missing `airflow.cfg` instead of missing Airflow executable

## 1.79.2 - (2021-09-07)

---

### Fixes

- [#2922](https://gitlab.com/meltano/meltano/-/issues/2922) Fix error during installation of some plugins caused by a `setuptools` release. _Thanks, **[Maarten van Gijssel](https://gitlab.com/mvgijssel)**!_

## 1.79.1 - (2021-08-17)

---

### Fixes

- [#2893](https://gitlab.com/meltano/meltano/-/issues/2893) Fix error when invoking a target outside pipeline context
- [#2627](https://gitlab.com/meltano/meltano/-/issues/2627) Invalidate catalog cache after reinstalling a tap

## 1.79.0 - (2021-08-13)

---

### New

- [#2545](https://gitlab.com/meltano/meltano/-/issues/2545) Add support for Python 3.9
- [#2849](https://gitlab.com/meltano/meltano/-/issues/2849) Use dbt [`v0.20`](https://github.com/fishtown-analytics/dbt/releases/tag/v0.20.1) by default for new dbt installs
- [#2576](https://gitlab.com/meltano/meltano/-/issues/2576) Use Airflow [v2.1](https://airflow.apache.org/docs/apache-airflow/2.1.0/changelog.html) by default for new Airflow installs
- [#2871](https://gitlab.com/meltano/meltano/-/issues/2871) Add `discovery_url_auth` project setting to support authenticated retrieval of `discovery.yml`
- [#2855](https://gitlab.com/meltano/meltano/-/issues/2855) Allow `executable` to be overridden through plugin inheritance
- [#2860](https://gitlab.com/meltano/meltano/-/issues/2860) Allow commands to use alternate executables

### Changes

- [#2868](https://gitlab.com/meltano/meltano/-/issues/2868) Refactor to allow SingerTarget to inject a BookmarkWriter via a new PluginInvoker callback
- [#2575](https://gitlab.com/meltano/meltano/-/issues/2575) Support version-specific pip constraint files by allowing the special var `${MELTANO__PYTHON_VERSION}` in plugin pip_url's (bumps `discovery.yml` version ([#2890](https://gitlab.com/meltano/meltano/-/issues/2890)) to signal the required upgrade)

### Fixes

- [#2882](https://gitlab.com/meltano/meltano/-/issues/2882) Allow multiple taps / targets to be invoked at the same time by adding a UUID to config.json
- [#2381](https://gitlab.com/meltano/meltano/-/issues/2381) Implement selection logic for all Singer discoverable metadata (`inclusion` and `selected-by-default`)

## 1.78.0 - (2021-07-15)

---

### New

- [#2814](https://gitlab.com/meltano/meltano/-/issues/2814) Add `mashey` variant of `tap-ask-nicely`
- [#2815](https://gitlab.com/meltano/meltano/-/issues/2815) Add `singer-io` variant of `tap-github`
- [#2816](https://gitlab.com/meltano/meltano/-/issues/2816) Add `singer-io` variant of `tap-google-sheets`
- [#2817](https://gitlab.com/meltano/meltano/-/issues/2817) Add `singer-io` variant of `tap-pendo`
- [#2818](https://gitlab.com/meltano/meltano/-/issues/2818) Add `singer-io` variant of `tap-hubspot`
- [#2821](https://gitlab.com/meltano/meltano/-/issues/2821) Add `singer-io` variant of `tap-jira`
- [#2823](https://gitlab.com/meltano/meltano/-/issues/2823) Add `transferwise` variant of `tap-twilio`

### Fixes

- [#2951](https://gitlab.com/meltano/meltano/-/issues/2851) Default to skipping transforms in Meltano UI pipeline creation
- [#2758](https://gitlab.com/meltano/meltano/-/issues/2758) Fix misleading error message when calling `meltano invoke airflow <args>`
- [#2826](https://gitlab.com/meltano/meltano/-/issues/2826) Make plugin installation serial during `meltano add ...`
- [#2828](https://gitlab.com/meltano/meltano/-/issues/2828) Fix coroutine error when `python3-venv` is missing during plugin installation.

### Breaks

## 1.77.0 - (2021-06-17)

---

### Changes

- [#2694](https://gitlab.com/meltano/meltano/-/issues/2694) Use dbt [`v0.19.1`](https://github.com/fishtown-analytics/dbt/releases/tag/v0.19.1) by default for new dbt installs
- [#2694](https://gitlab.com/meltano/meltano/-/issues/2694) Add support for dbt [`config-version: 2`](https://docs.getdbt.com/docs/guides/migration-guide/upgrading-to-0-17-0)
- [#2622](https://gitlab.com/meltano/meltano/-/issues/2622) Make `hotgluexyz` the default variant for the CSV loader

### Fixes

- [#2741](https://gitlab.com/meltano/meltano/-/issues/2741) Fix duplication of config values when complex settings are applied to Singer plugins.

## 1.76.0 - (2021-06-10)

---

### Fixes

- [#2755](https://gitlab.com/meltano/meltano/-/issues/2755) Fix SQLAlchemy `cache_ok` warning messages when running `meltano elt`
- [#2773](https://gitlab.com/meltano/meltano/-/issues/2773) Fix `tap-chargebee`, `tap-intacct` and `tap-quickbooks` definitions that had `properties` capability instead of `catalog`
- [#2784](https://gitlab.com/meltano/meltano/-/issues/2784) Fix catalog discovery error when using custom plugins with no `pip_url` set

## 1.75.0 - (2021-05-28)

---

### Changes

- [#2745](https://gitlab.com/meltano/meltano/-/issues/2745) Allow `meltano` commands to be used from a subdirectory of a project
- [#2341](https://gitlab.com/meltano/meltano/-/issues/2341) Add support for already-installed plugins by making `pip_url` optional in custom plugin definitions
- [#2341](https://gitlab.com/meltano/meltano/-/issues/2341) Allow non-pip plugins to be declared using relative `executable` paths and `executable` programs already on the PATH

## 1.74.0 - (2021-05-10)

---

### New

- [#2353](https://gitlab.com/meltano/meltano/-/issues/2353) Add `meltano remove` command

## 1.73.0 - (2021-04-29)

---

### New

- [#2621](https://gitlab.com/meltano/meltano/-/issues/2621) Add `twilio-labs` variant of `tap-zendesk`

### Changes

- [#2705](https://gitlab.com/meltano/meltano/-/issues/2705) Speed up `meltano install` by installing plugins in parallel
- [#2709](https://gitlab.com/meltano/meltano/-/issues/2709) Add support for setting `kind` in settings prompt when using `meltano add --custom`

## 1.72.0 - (2021-04-22)

---

### New

- [#2560](https://gitlab.com/meltano/meltano/-/issues/2560) Add support for shortcut commands to `invoke`
- [#2560](https://gitlab.com/meltano/meltano/-/issues/2560) Add support for `sqlfluff` utility for linting SQL transforms
- [#2613](https://gitlab.com/meltano/meltano/-/issues/2613) Add `mashey` variant of `tap-slack`
- [#2689](https://gitlab.com/meltano/meltano/-/issues/2689) Add documentation for using a custom Python Package Index (PyPI)
- [#2426](https://gitlab.com/meltano/meltano/-/issues/2426) Add `transferwise` variant of `target-redshift`

### Changes

- [#2082](https://gitlab.com/meltano/meltano/-/issues/2082) Updated database_uri documentation to show how to target a PostgreSQL schema
- [#2107](https://gitlab.com/meltano/meltano/-/issues/2107) Updated 'create a custom extractor' tutorial to use the new SDK

### Fixes

- [#2526](https://gitlab.com/meltano/meltano/-/issues/2526) When target process fails before tap, report target output instead of `BrokenPipeError` or `ConnectionResetError`

## 1.71.0 - (2021-03-23)

---

### New

- [#2544](https://gitlab.com/meltano/meltano/-/issues/2544) Add support for `utility` plugin type
- [#2614](https://gitlab.com/meltano/meltano/-/issues/2614) Add `mashey` variant of `tap-zoom`

### Fixes

- [#2581](https://gitlab.com/meltano/meltano/-/issues/2581) Only expand `$ALL_CAPS` env vars in `meltano.yml` config values to prevent false positive matches in passwords

## 1.70.0 - (2021-02-23)

---

### New

- [#2590](https://gitlab.com/meltano/meltano/-/issues/2590) Add `hotgluexyz` variant of `tap-chargebee`
- [#2593](https://gitlab.com/meltano/meltano/-/issues/2593) Add `hotgluexyz` variant of `tap-intacct`

### Changes

- [#2356](https://gitlab.com/meltano/meltano/-/issues/2356) Disallow two pipelines with the same job ID to run at the same time by default

### Fixes

- [#2585](https://gitlab.com/meltano/meltano/-/issues/2585) Fix bug with finding a schedule based on namespace for a custom plugin

## 1.69.0 - (2021-02-16)

---

### New

- [#2558](https://gitlab.com/meltano/meltano/-/issues/2558) Add support for Airflow 2.0
- [#2577](https://gitlab.com/meltano/meltano/-/issues/2577) Add `hotgluexyz` variant of `tap-quickbooks`

## 1.68.0 - (2021-02-11)

---

### New

- [#2557](https://gitlab.com/meltano/meltano/-/issues/2557) Add support for entity and attribute selection to tap-gitlab

### Changes

- [#2559](https://gitlab.com/meltano/meltano/-/issues/2559) Bump Airflow version to 1.10.14

### Fixes

- [#2543](https://gitlab.com/meltano/meltano/-/issues/2543) Fix packages dependencies that claim Python 3.9 is supported when it actually isn't.

## 1.67.0 - (2021-01-26)

---

### Fixes

- [#2540](https://gitlab.com/meltano/meltano/-/issues/2540) `meltano schedule run` exit code now matches exit code of wrapped `meltano elt`
- [#2525](https://gitlab.com/meltano/meltano/-/issues/2525) `meltano schedule run` no longer requires `meltano` to be in the `PATH`

## 1.66.0 - (2021-01-18)

---

### New

- [#2483](https://gitlab.com/meltano/meltano/-/issues/2483) Every second, `meltano elt` records a heartbeat timestamp on the pipeline run row in the system database as long as the pipeline is running.
- [#2483](https://gitlab.com/meltano/meltano/-/issues/2483) Before running the new pipeline, `meltano elt` automatically marks runs with the same Job ID that have become stale as failed. A run is considered stale when 5 minutes have elapsed since the last recorded heartbeat. Older runs without a heartbeat are considered stale if they are still in the running state 24 hours after starting.
- [#2483](https://gitlab.com/meltano/meltano/-/issues/2483) `meltano schedule list` (which is run periodically by `meltano invoke airflow scheduler`) automatically marks any stale run as failed.
- [#2502](https://gitlab.com/meltano/meltano/-/issues/2502) Add `User-Agent` header with Meltano version to request for remote `discovery.yml` manifest (typically https://www.meltano.com/discovery.yml)
- [#2503](https://gitlab.com/meltano/meltano/-/issues/2503) Include project ID in `X-Project-ID` header and `project_id` query param in request for remote `discovery.yml` manifest when `send_anonymous_usage_stats` setting is enabled.

## 1.65.0 - (2021-01-12)

---

### New

- [#2392](https://gitlab.com/meltano/meltano/-/issues/2392) Add 'elt.buffer_size' setting with default value of 10MiB to let extractor output buffer size and line length limit (maximum message size) be configured as appropriate for the extractor and loader in question.

### Fixes

- [#2501](https://gitlab.com/meltano/meltano/-/issues/2501) Don't lose `version` when caching `discovery.yml`.

## 1.64.1 - (2021-01-08)

---

### Fixes

- [#2500](https://gitlab.com/meltano/meltano/-/issues/2500) Ensure all buffered messages (records) output by extractor make it to loader when extractor finishes early.

## 1.64.0 - (2021-01-07)

---

### Fixes

- [#2478](https://gitlab.com/meltano/meltano/-/issues/2478) Fix runaway memory usage (and possible out-of-memory error) when extractor outputs messages at higher rate than loader can process them, by enabling flow control with a 64KB buffer size limit

## 1.63.0 - (2021-01-04)

---

### New

- [#2308](https://gitlab.com/meltano/meltano/-/issues/2308) Verify that system database connection is still viable when checking it out of connection pool.
- [#2308](https://gitlab.com/meltano/meltano/-/issues/2308) Add `database_max_retries` and `database_retry_timeout` settings to configure retry attempts when the first connection to the DB fails.

### Fixes

- [#2486](https://gitlab.com/meltano/meltano/-/issues/2486) Remove `state` capability from `tap-google-analytics` because it's not actually currently supported yet

## 1.62.0 - (2020-12-23)

---

### New

- [#2390](https://gitlab.com/meltano/meltano/-/issues/2390) Let a plugin inherit its base plugin (package) description and configuration from another one using `--inherit-from=<name>` on `meltano add` or `inherit_from: <name>` in `meltano.yml`, so that the same package can be used in a project multiple times with different configurations.

### Changes

- [#2479](https://gitlab.com/meltano/meltano/-/issues/2479) Use extractor `load_schema` (usually its namespace) as default for target-bigquery `dataset_id` setting, as it already is for target-snowflake and target-postgres `schema`

## 1.61.0 - (2020-12-09)

---

### New

- [#2476](https://gitlab.com/meltano/meltano/-/issues/2476) Add missing tap-salesforce `is_sandbox` setting
- [#2471](https://gitlab.com/meltano/meltano/-/issues/2471) Make tap-bigquery discoverable
- [#2227](https://gitlab.com/meltano/meltano/-/issues/2227) Add `meltano schedule run <name>` command to run scheduled pipeline by name

### Changes

- [#2477](https://gitlab.com/meltano/meltano/-/issues/2477) Show array and object settings in configuration UI as unsupported instead of hiding them entirely
- [#2477](https://gitlab.com/meltano/meltano/-/issues/2477) Unhide tap-csv and tap-spreadsheets-anywhere in UI

### Fixes

- [#2379](https://gitlab.com/meltano/meltano/-/issues/2379) Take into account schedule `env` when running pipeline from UI using "Run" button

## 1.60.1 - (2020-12-07)

---

### Fixes

- [#2473](https://gitlab.com/meltano/meltano/-/issues/2473) Fix meltano/meltano Docker image entrypoint

## 1.60.0 - (2020-12-02)

---

### New

- [#2367](https://gitlab.com/meltano/meltano/-/issues/2367) Adopt Poetry for dependency and build management

### Changes

- [#2457](https://gitlab.com/meltano/meltano/-/issues/2457) Hide settings of kind `object` or `array` in UI

### Fixes

- [#2457](https://gitlab.com/meltano/meltano/-/issues/2457) Fix configuration of tap-adwords `primary_keys` and target-snowflake and target-postgres (transferwise variants) `schema_mapping`
- [#2463](https://gitlab.com/meltano/meltano/-/issues/2463) Fix casting of tap-postgres `max_run_seconds`, `logical_poll_total_seconds`, and `break_at_end_lsn` setting values
- [#2466](https://gitlab.com/meltano/meltano/-/issues/2466) Stop requiring specific version of `cryptography` that's incompatible with latest `pyOpenSSL`

## 1.59.0 - (2020-11-23)

---

### Changes

- [#2450](https://gitlab.com/meltano/meltano/-/issues/2450) Remove undocumented plugin configuration profile functionality

### Fixes

- [#2451](https://gitlab.com/meltano/meltano/-/issues/2451) Correctly show CLI error messages in log output
- [#2453](https://gitlab.com/meltano/meltano/-/issues/2453) Correctly pass value of `tap-facebook`'s `insights_buffer_days` setting to tap as integer instead of boolean
- [#2387](https://gitlab.com/meltano/meltano/-/issues/2387) Order of attributes in `meltano select --list --all` is set to alphabetical order.
- [#2458](https://gitlab.com/meltano/meltano/-/issues/2458) Adds missing `mysql-logo.png`

## 1.58.0 - (2020-11-12)

---

### New

- [#2438](https://gitlab.com/meltano/meltano/-/issues/2438) Add missing `replica_set`, `ssl`, `verify_mode`, and `include_schemas_in_destination_stream_name` settings to `tap-mongodb`
- [#2389](https://gitlab.com/meltano/meltano/-/issues/2389) Let user disable autoscrolling in UI job log modal
- [#2307](https://gitlab.com/meltano/meltano/-/issues/2307) Add `ui.session_cookie_secure` setting to let `Secure` flag be enabled on session cookies when Meltano UI is served over HTTPS

### Changes

- [#2307](https://gitlab.com/meltano/meltano/-/issues/2307) The `Secure` flag is no longer enabled on Meltano UI session cookies unconditionally and by default

### Fixes

- [#2396](https://gitlab.com/meltano/meltano/-/issues/2396) Support unquoted `YYYY-MM-DD` date values in `meltano.yml` by converting them to ISO8601 strings before passing them to plugins
- [#2445](https://gitlab.com/meltano/meltano/-/issues/2445) Fix 'Test Connection' and 'Save' buttons being disabled in UI Configuration modal despite required fields being populated
- [#2307](https://gitlab.com/meltano/meltano/-/issues/2307) Fix logging into Meltano UI in Google Chrome when running without HTTPS

## 1.57.0 - (2020-11-10)

---

### New

- [#2433](https://gitlab.com/meltano/meltano/-/issues/2433) Add `datamill-co` variant of `target-postgres`
- [#2425](https://gitlab.com/meltano/meltano/-/issues/2425) Add `transferwise` variant of `target-postgres`
- [#2404](https://gitlab.com/meltano/meltano/-/issues/2404) Add `singer-io` variant of `tap-recharge`
- [#2410](https://gitlab.com/meltano/meltano/-/issues/2410) Add `transferwise` variant of `tap-postgres`
- [#2411](https://gitlab.com/meltano/meltano/-/issues/2411) Add `transferwise` variant of `tap-mysql`
- [#2407](https://gitlab.com/meltano/meltano/-/issues/2407) Refactor discovery.yaml to keep things in lexicographically ascending order and in correct format
- [#2435](https://gitlab.com/meltano/meltano/-/issues/2435) Add new `stringify` setting `value_post_processor` that will convert values to their JSON string representation
- [#2437](https://gitlab.com/meltano/meltano/-/issues/2437) Add `meltano invoke` `--dump` option with possible values `config` and `catalog` (for extractors) to dump content of plugin-specific generated file

### Changes

- [#2368](https://gitlab.com/meltano/meltano/-/issues/2433) Make `datamill-co` variant of `target-postgres` the default instead of `meltano`

### Fixes

### Breaks

## 1.56.0 - (2020-11-02)

---

### New

- [#2374](https://gitlab.com/meltano/meltano/-/issues/2374) Add `target-bigquery` discoverable plugin definition
- [#1956](https://gitlab.com/meltano/meltano/-/issues/1956) Add support for Python 3.8

## 1.55.0 - (2020-10-30)

---

### New

- [#2368](https://gitlab.com/meltano/meltano/-/issues/2368) Add `transferwise` and `datamill-co` variants of `target-snowflake`

### Changes

- [#2368](https://gitlab.com/meltano/meltano/-/issues/2368) Make `datamill-co` variant of `target-snowflake` the default instead of `meltano`
- [#2380](https://gitlab.com/meltano/meltano/-/issues/2380) Add `target_` prefix to `namespace`s of discoverable loaders target-postgres, target-snowflake, and target-sqlite

### Fixes

- [#2373](https://gitlab.com/meltano/meltano/-/issues/2373) `meltano init` emits warning instead of failing when underlying filesystem doesn't support symlinks
- [#2391](https://gitlab.com/meltano/meltano/-/issues/2391) Add missing `max_workers` setting to `tap-salesforce` discoverable plugin definition
- [#2400](https://gitlab.com/meltano/meltano/-/issues/2400) Constrain Airflow installation to specific set of known-to-work requirements to prevent it from breaking unexpectedly

## 1.54.0 - (2020-10-08)

---

### Changes

- [#2057](https://gitlab.com/meltano/meltano/-/issues/2057) Bump Airflow version to 1.10.12
- [#2224](https://gitlab.com/meltano/meltano/-/issues/2224) Delete (if present) and recreate virtual environments for all plugins when running meltano install.

### Fixes

- [#2334](https://gitlab.com/meltano/meltano/-/issues/2334) Omit keys for settings with `null` values from `config.json` files generated for taps and targets, to support plugins that check if a config key is present instead of checking if the value is non-null.
- [#2376](https://gitlab.com/meltano/meltano/-/issues/2376) Fix `meltano elt ... --transform={run,only}` raising `PluginMissingError` when a default transform for the extractor is discoverable but not installed
- [#2377](https://gitlab.com/meltano/meltano/-/issues/2377) Ensure arbitrary env vars defined in `.env` are passed to invoked plugins

## 1.53.0 - (2020-10-06)

---

### New

- [#2134](https://gitlab.com/meltano/meltano/-/issues/2134) Let different variants of plugins be discovered and let users choose which to add to their project

### Changes

- [#2112](https://gitlab.com/meltano/meltano/-/issues/2112) Stop inheriting Meltano venv when invoking Airflow

### Fixes

- [#2372](https://gitlab.com/meltano/meltano/-/issues/2372) Upgrade `pip` and related tools to the latest version in plugin venvs

## 1.52.0 - (2020-09-28)

---

### Fixes

- [#2360](https://gitlab.com/meltano/meltano/-/issues/2360) Remove automatic install of extractors, loaders, and transforms if they are not present.

- [#2348](https://gitlab.com/meltano/meltano/-/issues/2348) Invalidate `meltano select` catalog discovery cache when extractor configuration is changed

## 1.51.0 - (2020-09-21)

---

### New

- [#2355](https://gitlab.com/meltano/meltano/-/issues/2355) Add `meltano elt` `--dump` option with possible values `catalog`, `state`, `extractor-config`, and `loader-config` to dump content of pipeline-specific generated file

### Fixes

- [#2358](https://gitlab.com/meltano/meltano/-/issues/2358) Don't unintentionally deselect all attributes other than those marked `inclusion: automatic` when using extractor `select_filter` extra or `meltano elt`'s `--select <entity>` option

## 1.50.0 - (2020-09-17)

---

### New

- [#2291](https://gitlab.com/meltano/meltano/-/issues/2291) Add `catalog` extractor extra to allow a catalog to be provided manually
- [#2291](https://gitlab.com/meltano/meltano/-/issues/2291) Add `--catalog` option to `meltano elt` to allow a catalog to be provided manually
- [#2289](https://gitlab.com/meltano/meltano/-/issues/2289) Add `state` extractor extra to allow state file to be provided manually
- [#2289](https://gitlab.com/meltano/meltano/-/issues/2289) Add `--state` option to `meltano elt` to allow state file to be provided manually

### Fixes

- [#2352](https://gitlab.com/meltano/meltano/-/issues/2352) `meltano elt` `--select` and `--exclude` no longer unexpectedly select entities for extraction that match the wildcard pattern but weren't selected originally.

## 1.49.0 - (2020-09-15)

---

### New

- [#2279](https://gitlab.com/meltano/meltano/-/issues/2279) Populate primary setting env var and aliases when invoking plugin or expanding env vars
- [#2349](https://gitlab.com/meltano/meltano/-/issues/2349) Allow plugin setting (default) values to reference pipeline plugin extras using generic env vars, e.g. `MELTANO_EXTRACT__<EXTRA>`
- [#2281](https://gitlab.com/meltano/meltano/-/issues/2281) Allow plugin extra (default) values to reference plugin name, namespace, profile using generic env vars, e.g. `MELTANO_EXTRACTOR_NAMESPACE`
- [#2280](https://gitlab.com/meltano/meltano/-/issues/2280) Allow plugin extra (default) values to reference plugin settings using env vars, e.g. `target_schema: $PG_SCHEMA`
- [#2278](https://gitlab.com/meltano/meltano/-/issues/2278) Read setting values from `<PLUGIN_NAME>_<SETTING_NAME>` env vars, taking precedence over `<PLUGIN_NAMESPACE>_<SETTING_NAME>` but not custom `env`
- [#2350](https://gitlab.com/meltano/meltano/-/issues/2350) Add `MELTANO_TRANSFORM_*` transform pipeline env vars for transformer (configuration) to access
- [#2282](https://gitlab.com/meltano/meltano/-/issues/2282) Add new extractor extra `load_schema` and use it as default loader `schema` instead of namespace
- [#2284](https://gitlab.com/meltano/meltano/-/issues/2284) Add new loader extra `dialect` and use it as default dbt `target` and Meltano UI SQL dialect instead of namespace
- [#2283](https://gitlab.com/meltano/meltano/-/issues/2283) Add new loader extra `target_schema` and use it as default dbt `source_schema` instead of loader `schema`
- [#2285](https://gitlab.com/meltano/meltano/-/issues/2285) Add new transform extra `package_name` and use it in dbt's `dbt_project.yml` and `--models` argument instead of namespace

### Changes

- [#2279](https://gitlab.com/meltano/meltano/-/issues/2279) Fall back on setting values from `<PLUGIN_NAME>_<SETTING_NAME>` and `<PLUGIN_NAMESPACE>_<SETTING_NAME>` env vars if a custom `env` is defined but not used
- [#2278](https://gitlab.com/meltano/meltano/-/issues/2278) Stop unnecessarily prepopulating `env` on a newly added custom plugin's settings definitions
- [#2208](https://gitlab.com/meltano/meltano/-/issues/2208) Standardize on setting env vars prefixed with plugin name, not namespace or custom `env`

## 1.48.0 - (2020-09-07)

---

### New

- [#2340](https://gitlab.com/meltano/meltano/-/issues/2340) Print full error message when extractor catalog discovery fails
- [#2223](https://gitlab.com/meltano/meltano/-/issues/2223) Print clear error message when `meltano invoke` or `meltano elt` attempts to execute a plugin that hasn't been installed yet
- [#2345](https://gitlab.com/meltano/meltano/-/issues/2345) Make `tap-csv` `files` a known setting
- [#2155](https://gitlab.com/meltano/meltano/-/issues/2155) Add `select_filter` extractor extra to allow extracting a subset of selected entities
- [#2155](https://gitlab.com/meltano/meltano/-/issues/2155) Add `--select` and `--exclude` options to `meltano elt` to allow extracting a subset of selected entities

### Changes

- [#2167](https://gitlab.com/meltano/meltano/-/issues/2167) Include extractor and loader name in autogenerated `meltano elt` job ID
- [#2343](https://gitlab.com/meltano/meltano/-/issues/2343) Automatically delete generated plugin config files at end of `meltano elt` and `meltano invoke`

### Fixes

- [#2167](https://gitlab.com/meltano/meltano/-/issues/2167) Make sure autogenerated `meltano elt` job ID matches in system database and `.meltano/{run,logs}/elt`
- [#2347](https://gitlab.com/meltano/meltano/-/issues/2347) Have `meltano config <plugin> set --store=dotenv` store valid JSON values for arrays and objects
- [#2346](https://gitlab.com/meltano/meltano/-/issues/2346) Correctly cast environment variable string value when overriding custom array and object settings

### Breaks

- [#2344](https://gitlab.com/meltano/meltano/-/issues/2344) Move `meltano elt` output logs from `.meltano/run/elt` to `.meltano/logs/elt`
- [#2342](https://gitlab.com/meltano/meltano/-/issues/2342) Store pipeline-specific generated plugin config files (`tap.config.json`, `tap.properties.json`, etc) under `.meltano/run/elt/<job_id>/<run_id>` instead of `.meltano/run/<plugin_name>`. Users who were explicitly putting a catalog file at `.meltano/run/<plugin_name>/tap.properties.json` should use `.meltano/extractors/<plugin_name>/tap.properties.json` instead.

## 1.47.0 - (2020-09-03)

---

### New

- [#2210](https://gitlab.com/meltano/meltano/-/issues/2210) Print documentation and repository URLs when adding a new plugin to the project
- [#2277](https://gitlab.com/meltano/meltano/-/issues/2277) Add `tap-bing-ads` as a known extractor
- [#2328](https://gitlab.com/meltano/meltano/-/issues/2328) Add new `upcase_string` setting `value_processor` that will convert string values to uppercase

### Changes

- [#2216](https://gitlab.com/meltano/meltano/-/issues/2216) Add stream properties defined in an extractor's `schema` extra to catalog if they do not exist in the discovered stream schema yet

### Fixes

- [#2338](https://gitlab.com/meltano/meltano/-/issues/2338) Once again change `target-csv` to use `singer-io/target-csv` instead of the Meltano fork
- [#2235](https://gitlab.com/meltano/meltano/-/issues/2235) Make embed links accessible when not authenticated
- [#2328](https://gitlab.com/meltano/meltano/-/issues/2328) Always convert `target-snowflake` `schema` setting value to uppercase before passing it to plugin

## 1.46.0 - (2020-08-27)

---

### New

- [!1820](https://gitlab.com/meltano/meltano/-/merge_requests/1820) Add 'tap-spreadsheets-anywhere' as an extractor

### Changes

- [#2309](https://gitlab.com/meltano/meltano/-/issues/2309) Pretty print `meltano schedule list --format=json` output
- [#2312](https://gitlab.com/meltano/meltano/-/issues/2312) Don't unnecessarily run discovery and generate catalog when running `meltano invoke <extractor> --help`, making it less likely to fail

## 1.45.0 - (2020-08-17)

---

### New

- [#2071](https://gitlab.com/meltano/meltano/-/issues/2071) Add new "Loaders" page to UI
- [#2222](https://gitlab.com/meltano/meltano/-/issues/2222) Add OAuth credentials settings to `tap-google-analytics`

### Changes

- [#2197](https://gitlab.com/meltano/meltano/-/issues/2197) Change `target-csv` to use `singer-io/target-csv` instead of the Meltano fork

### Fixes

- [#2268](https://gitlab.com/meltano/meltano/-/issues/2268) Fix bug causing custom plugins not to show up in `meltano discover` and have "Unknown" label in UI

## 1.44.0 - (2020-08-11)

---

### Fixes

- [#2219](https://gitlab.com/meltano/meltano/-/issues/2219) Don't fail on large (record) messages output by extractors (Singer taps) by increasing subprocess output buffer size from 64KB to 1MB.
- [#2215](https://gitlab.com/meltano/meltano/-/issues/2215) Have `meltano invoke <plugin> --help` pass `--help` flag to plugin, instead of showing `meltano invoke` help message

## 1.43.0 - (2020-08-04)

---

### New

- [#2116](https://gitlab.com/meltano/meltano/-/issues/2116) Prefix `meltano elt` output with `meltano`, `tap-foo`, `target-bar` and `dbt` labels as appropriate
- [!1778](https://gitlab.com/meltano/meltano/-/merge_requests/1788) Clearly print reason that tap, target or dbt failed by repeating last output line
- [#2214](https://gitlab.com/meltano/meltano/-/issues/2214) Log Singer messages output by tap and target when `meltano elt` is run with `--log-level` flag (or `cli.log_level` setting) set to `debug`

### Changes

- [!1778](https://gitlab.com/meltano/meltano/-/merge_requests/1788) Change stored error message when job was interrupted by KeyboardInterrupt from 'KeyboardInterrupt()' to 'The process was interrupted'
- [!1778](https://gitlab.com/meltano/meltano/-/merge_requests/1788) Disable noisy SettingsService logging when `cli.log_level` setting (or `--log-level` flag) is set to `debug`

### Fixes

- [#2212](https://gitlab.com/meltano/meltano/-/issues/2212) Don't show extractor extras `_select`, `_metadata`, and `_schema` as required in UI configuration form
- [#2213](https://gitlab.com/meltano/meltano/-/issues/2213) Provide extra context when `meltano invoke airflow` fails because of `airflow initdb` failing
- [!1778](https://gitlab.com/meltano/meltano/-/merge_requests/1788) Fail gracefully when `meltano install` fails to install plugin(s)

## 1.42.0 - (2020-07-28)

---

### New

- [#2162](https://gitlab.com/meltano/meltano/-/issues/2162) Print link to plugin documentation in `meltano add <plugin>` and `meltano config <plugin> list` output

### Changes

- [#2200](https://gitlab.com/meltano/meltano/-/issues/2200) Consistently handle CLI errors
- [#2147](https://gitlab.com/meltano/meltano/-/issues/2147) Continuously persist state messages output by loader (forwarded from extractor) so that subsequent runs can pick up where a failed run left off
- [#2198](https://gitlab.com/meltano/meltano/-/issues/2198) Don't touch project files that may be readonly when installing transform or dashboard plugins.

### Fixes

- [#2199](https://gitlab.com/meltano/meltano/-/issues/2199) Fix `meltano discover` only listing custom plugins, not known (discovered) ones
- [#2166](https://gitlab.com/meltano/meltano/-/issues/2166) Don't fail on large extractor state messages by increasing loader output buffer size from 64 to 128KB
- [#2180](https://gitlab.com/meltano/meltano/-/issues/2180) Mark pipeline job as failed when process is interrupted (SIGINT) or terminated (SIGTERM).

## 1.41.1 - (2020-07-23)

---

### New

- [#2196](https://gitlab.com/meltano/meltano/-/issues/2196) Pretty print and apply appropriate nesting to `meltano config` output
- [#2003](https://gitlab.com/meltano/meltano/-/issues/2003) Let extractor extra `select` be interacted with as `_select` setting
- [!1774](https://gitlab.com/meltano/meltano/-/merge_requests/1774) Let transform extra `vars` be interacted with as `_vars` setting
- [!1774](https://gitlab.com/meltano/meltano/-/merge_requests/1774) Add support for `kind: object` settings, which can gather nested values from across setting stores
- [!1774](https://gitlab.com/meltano/meltano/-/merge_requests/1774) Add support for `aliases: [...]` on setting definitions
- [!1774](https://gitlab.com/meltano/meltano/-/merge_requests/1774) Add support for `value_processor: 'nest_object'` on setting definitions
- [#2145](https://gitlab.com/meltano/meltano/-/issues/2145) Let discovered catalog schema be modified using schema rules stored in extractor `schema` extra (aka `_schema` setting)

### Changes

- [#2070](https://gitlab.com/meltano/meltano/issues/2070) List installed and available extractors separately on Extractors page
- [!1774](https://gitlab.com/meltano/meltano/-/merge_requests/1774) Replace `update.*` file bundle settings with `update` extra (aka `_update` setting)
- [!1774](https://gitlab.com/meltano/meltano/-/merge_requests/1774) Replace `metadata.*` extractor settings with `metadata` extra (aka `_metadata` setting)
- [#1764](https://gitlab.com/meltano/meltano/-/merge_requests/1764) Interpret `meltano config <plugin> set` value as JSON to allow non-string values to be set more easily

### Fixes

- [!1774](https://gitlab.com/meltano/meltano/-/merge_requests/1774) Fix poor performance of setting lookups using more memoization

## 1.41.0 - (2020-07-20)

---

### New

- [#2174](https://gitlab.com/meltano/meltano/-/issues/2174) Add `/api/health` health check route
- [#2125](https://gitlab.com/meltano/meltano/-/issues/2125) Add `--full-refresh` flag to `meltano elt` to perform a full refresh, ignoring the state left behind by any previous runs with the same job ID.
- [#2181](https://gitlab.com/meltano/meltano/-/issues/2181) Show custom Meltano UI logo (`ui.logo_url` setting) on sign-in page when authentication is enabled.

### Changes

- [#2175](https://gitlab.com/meltano/meltano/-/issues/2175) Clarify that not supporting discovery mode means that the `state` capability is not advertised
- [#2195](https://gitlab.com/meltano/meltano/-/issues/2195) Slightly increase size of custom Meltano UI logo (`ui.logo_url`) in navbar

### Fixes

- [#2168](https://gitlab.com/meltano/meltano/-/issues/2168) Don't select entity attributes marked as unsupported

## 1.40.1 - (2020-07-16)

---

### New

- [#2171](https://gitlab.com/meltano/meltano/-/issues/2171) Add better logging and error handling to `meltano config`
- [#2154](https://gitlab.com/meltano/meltano/-/issues/2154) Add 'project_readonly' setting to block changes to containerized project files, but still allow UI and CLI to store configuration in system database
- [#2157](https://gitlab.com/meltano/meltano/-/issues/2157) Add `ui.analysis` setting which can be disabled to hide all functionality related to Analysis from the UI
- [#2169](https://gitlab.com/meltano/meltano/-/issues/2169) Log warning when pipeline state was found but extractor does not advertise `state` capability

### Changes

- [#2171](https://gitlab.com/meltano/meltano/-/issues/2171) `meltano config <plugin> set` will now automatically store settings in `meltano.yml` or `.env` as appropriate.
- [#2127](https://gitlab.com/meltano/meltano/-/issues/2127) Config stored in `meltano.yml` or `.env` can now be edited in the UI when read-only mode is not enabled

### Fixes

- [#2109](https://gitlab.com/meltano/meltano/-/issues/2109) Fix bug causing adding extractor with related transform plugin to project in UI to fail when dbt hasn't yet been installed
- [#2170](https://gitlab.com/meltano/meltano/-/issues/2170) Restore support for referencing arbitrary env vars defined in `.env` from `meltano.yml` using env var expansion
- [#2115](https://gitlab.com/meltano/meltano/-/issues/2115) Stop `meltano` commands from leaving empty `.meltano/run` directory behind when run in non-project dir

## 1.40.0 - (2020-07-14)

---

### New

- [#2153](https://gitlab.com/meltano/meltano/-/issues/2153) Add `logo_url` property to custom extractor and loader definitions to show a custom logo in Meltano UI

## 1.39.1 - (2020-07-09)

---

### New

- [#2141](https://gitlab.com/meltano/meltano/-/issues/2141) Add `ui.session_cookie_domain` setting, to be used instead of `ui.server_name` when hostname matching is not desirable.
- [#2142](https://gitlab.com/meltano/meltano/-/issues/2142) Let `discovery.yml` manifest URL be overwritten using `discovery_url` setting.
- [#2083](https://gitlab.com/meltano/meltano/-/issues/2083) Add `ui.anonymous_readonly` setting to allow anonymous users read-only access when `ui.authentication` is enabled.
- [#2108](https://gitlab.com/meltano/meltano/-/issues/2108) Show icon with tooltip in UI when read-only mode is enabled
- [#2120](https://gitlab.com/meltano/meltano/-/issues/2120) Add `ui.logo_url` setting to allow the customization of the logo shown in the top left of the Meltano UI interface.

### Changes

- [#2140](https://gitlab.com/meltano/meltano/-/issues/2140) Only have `meltano ui` complain about missing `ui.server_name`, `ui.secret_key` and `ui.password_salt` settings when `ui.authentication` is enabled
- [#2083](https://gitlab.com/meltano/meltano/-/issues/2083) Stop allowing anonymous users read-only access when `ui.authentication` and `ui.readonly` are both enabled.

### Fixes

- [#2151](https://gitlab.com/meltano/meltano/-/issues/2151) Fix `meltano ui` never printing `Meltano UI is now available at [URL]` if `ui.server_name` is set
- [#2152](https://gitlab.com/meltano/meltano/-/issues/2152) Fix `meltano ui` printing all `gunicorn.error` logs twice

## 1.39.0 - (2020-07-07)

---

### New

- [#2100](https://gitlab.com/meltano/meltano/-/issues/2100) Let settings be stored directly in `.env` using `meltano config set --store=dotenv`
- [#2099](https://gitlab.com/meltano/meltano/-/issues/2099) Let Meltano settings be configured using `meltano config meltano {list,set,unset,reset}`

### Changes

- [#2100](https://gitlab.com/meltano/meltano/-/issues/2100) Have `meltano ui setup` store secrets in `.env` instead of `ui.cfg`

### Fixes

- [#2135](https://gitlab.com/meltano/meltano/-/issues/2135) Fix UI "Explore" page for custom (as opposed to plugin-based) topics and models
- [#2136](https://gitlab.com/meltano/meltano/-/issues/2136) Show error message in Analyze UI when pipeline for extractor is missing, even if extractor is installed
- [#2131](https://gitlab.com/meltano/meltano/-/issues/2131) Have "true" environment variables take precedence over those defined in `.env`

## 1.38.1 - (2020-07-03)

---

### New

- [#2128](https://gitlab.com/meltano/meltano/-/issues/2128) Allow alternative env vars to be specified for settings using `env_aliases` array
- [#2128](https://gitlab.com/meltano/meltano/-/issues/2128) Allow negated env var to be defined for boolean settings using `!` prefix in `env_aliases` array
- [#2129](https://gitlab.com/meltano/meltano/-/issues/2129) Cast values of `kind: integer` settings set through environment variables
- [#2132](https://gitlab.com/meltano/meltano/-/issues/2132) Support common `WEB_CONCURRENCY` env var to set `meltano ui` concurrency (workers)
- [#2091](https://gitlab.com/meltano/meltano/-/issues/2091) Support common `PORT` env var to set `meltano ui` bind port

### Changes

- [#2094](https://gitlab.com/meltano/meltano/-/issues/2069) Turn "Connections" page into "Extractors" management UI
- [#2130](https://gitlab.com/meltano/meltano/-/issues/2130) Have CLI respect `MELTANO_PROJECT_ROOT` env var when set instead of looking at current directory

## 1.38.0 - (2020-06-30)

---

### New

- [#2122](https://gitlab.com/meltano/meltano/-/issues/2122) Allow custom (`meltano.yml`-`config`-defined) settings to be overridden using environment
- [#2123](https://gitlab.com/meltano/meltano/-/issues/2123) Show current values and their source in `meltano config <plugin> list`

### Changes

- [#2102](https://gitlab.com/meltano/meltano/-/issues/2101) Improve `discovery.yml` incompatibility handling and error messages

### Fixes

- [#2121](https://gitlab.com/meltano/meltano/-/issues/2121) Don't include empty `plugins` object in new project `meltano.yml`

### Breaks

- [#2105](https://gitlab.com/meltano/meltano/-/issues/2105) Stop automatically running Airflow scheduler as part of Meltano UI

## 1.37.1 - (2020-06-26)

---

### Fixes

- [#2113](https://gitlab.com/meltano/meltano/-/issues/2113) Fix bug causing `meltano invoke airflow` to fail because `AIRFLOW_HOME` was not set correctly.

## 1.37.0 - (2020-06-25)

---

### New

- [#2048](https://gitlab.com/meltano/meltano/-/issues/2048) Add `docker` and `gitlab-ci` file bundles to allow instant containerization
- [#2068](https://gitlab.com/meltano/meltano/-/issues/2068) Add interface to schedule new pipelines to Pipelines page
- [#2081](https://gitlab.com/meltano/meltano/-/issues/2081) Add `url` config option to `target-postgres`
- [#2060](https://gitlab.com/meltano/meltano/-/issues/2060) Add `--format=json` option to `meltano schedule list` so that a project's schedules can be processed programmatically

## 1.36.1 - (2020-06-19)

### New

- [#2067](https://gitlab.com/meltano/meltano/-/issues/2067) Add pipeline name, loader, and transform columns to Pipelines table
- [#2103](https://gitlab.com/meltano/meltano/-/issues/2103) Support nested objects in `meltano.yml` `config` objects
- [#2103](https://gitlab.com/meltano/meltano/-/issues/2103) Allow nested properties to be set using `meltano config` by specifying a list of property names: `meltano config <plugin_name> set <property> <subproperty> <value>`
- [#2026](https://gitlab.com/meltano/meltano/-/issues/2026) Allow Singer stream and property metadata to be configured using special nested `config` properties `metadata.<entity>.<key>` and `metadata.<entity>.<attribute>.<key>`.

### Fixes

- [#2102](https://gitlab.com/meltano/meltano/-/issues/2102) Fix potential `meltano upgrade` failures by having it invoke itself with `--skip-package` after upgrading the package to ensure it always uses the latest code.

## 1.36.0 - (2020-06-15)

---

### New

- [#2095](https://gitlab.com/meltano/meltano/-/issues/2089) Support singular and plural plugin types in CLI arguments
- [#2095](https://gitlab.com/meltano/meltano/-/issues/2089) Allow list of plugin names of same type to be provided to `meltano add` and `meltano install`
- [#2089](https://gitlab.com/meltano/meltano/-/issues/2089) Add new 'files' plugin type to allow plugin-specific files to be added to a Meltano project automatically
- [#2090](https://gitlab.com/meltano/meltano/-/issues/2090) Allow SERVER_NAME, SECRET_KEY, and SECURITY_PASSWORD_SALT to be set using environment instead of ui.cfg

### Fixes

- [#2096](https://gitlab.com/meltano/meltano/-/issues/2096) Remove noisy migration-related logging from CLI command output
- [#2089](https://gitlab.com/meltano/meltano/-/issues/2089) Don't add Airflow and dbt-specific files to Meltano project until plugins are added explicitly
- [#2089](https://gitlab.com/meltano/meltano/-/issues/2089) Don't add docker-compose.yml to Meltano project by default

## 1.35.1 - (2020-06-11)

---

### Changes

- [#2094](https://gitlab.com/meltano/meltano/-/issues/2094) Consistently refer to plugin types and names in CLI output

### Fixes

- [#2092](https://gitlab.com/meltano/meltano/-/issues/2092) Only install plugins related to plugins of the specified type when running `meltano install <plugin_type> --include-related`
- [#2093](https://gitlab.com/meltano/meltano/-/issues/2093) Print error when transform plugin is installed before dbt

## 1.35.0 - (2020-06-09)

---

### New

- [#2013](https://gitlab.com/meltano/meltano/-/issues/2013) Add `--store` option to `meltano config` with possible values `db` and `meltano_yml`
- [#2087](https://gitlab.com/meltano/meltano/-/issues/2087) Add `--plugin-type` option to `meltano config` and `meltano invoke`
- [#2088](https://gitlab.com/meltano/meltano/-/issues/2088) Add `meltano upgrade` subcommands `package`, `files`, `database`, and `models`

### Changes

- [#2064](https://gitlab.com/meltano/meltano/-/issues/2064) Print environment-specific instructions when `meltano upgrade` is run from inside Docker
- [#2013](https://gitlab.com/meltano/meltano/-/issues/2013) Have `meltano config` store in meltano.yml instead of system database by default
- [#2087](https://gitlab.com/meltano/meltano/-/issues/2087) Skip plugins that are not configurable or invokable when finding plugin by name in `meltano config` and `meltano invoke`

### Fixes

- [#2080](https://gitlab.com/meltano/meltano/-/issues/2080) Don't try to overwrite .gitignore when upgrading Meltano and project
- [#2065](https://gitlab.com/meltano/meltano/-/issues/2065) Don't have `meltano upgrade` complain when `meltano ui`'s `gunicorn` isn't running
- [#2085](https://gitlab.com/meltano/meltano/-/issues/2085) Don't change order of object and set values when meltano.yml is updated programatically
- [#2086](https://gitlab.com/meltano/meltano/-/issues/2086) Ensure "meltano config --format=json" prints actual JSON instead of Python object

## 1.34.2 - (2020-05-29)

---

### Fixes

- [#2076](https://gitlab.com/meltano/meltano/-/issues/2076) Fix bug that caused Airflow to look for DAGs in plugins dir instead of dags dir
- [#2077](https://gitlab.com/meltano/meltano/-/issues/2077) Fix potential dependency version conflicts by ensuring Meltano venv is not inherited by invoked plugins other than Airflow
- [#2075](https://gitlab.com/meltano/meltano/-/issues/2075) Update Airflow configand run `initdb` every time it is invoked
- [#2078](https://gitlab.com/meltano/meltano/-/issues/2078) Have Airflow DAG respect non-default system database URI set through `MELTANO_DATABASE_URI` env var or `--database-uri` option

## 1.34.1 - (2020-05-26)

---

### Fixes

- [#2063](https://gitlab.com/meltano/meltano/-/merge_requests/2063) Require `psycopg2-binary` instead of `psycopg2` so that build dependency `pg_config` doesn't need to be present on system

## 1.34.0 - (2020-05-26)

---

### New

- [!1664](https://gitlab.com/meltano/meltano/-/merge_requests/1664) Automatically populate `env` properties on newly added custom plugin `settings` in `meltano.yml`
- [!1664](https://gitlab.com/meltano/meltano/-/merge_requests/1664) Have `meltano config <plugin> list` print default value along with setting name and env var
- [!1664](https://gitlab.com/meltano/meltano/-/merge_requests/1664) Pass configuration environment variables when invoking plugins
- [!1664](https://gitlab.com/meltano/meltano/-/merge_requests/1664) Set `MELTANO_EXTRACTOR_NAME`, `MELTANO_EXTRACTOR_NAMESPACE`, and `MELTANO_EXTRACT_{SETTING...}` environment variables when invoking loader or transformer
- [!1664](https://gitlab.com/meltano/meltano/-/merge_requests/1664) Set `MELTANO_LOADER_NAME`, `MELTANO_LOADER_NAMESPACE`, and `MELTANO_LOAD_{SETTING...}` environment variables when invoking transformer
- [!1664](https://gitlab.com/meltano/meltano/-/merge_requests/1664) Allow dbt project dir, profiles dir, target, source schema, target schema, and models to be configured like any other plugin, with defaults based on pipeline-specific environment variables
- [#2029](https://gitlab.com/meltano/meltano/-/issues/2029) Allow target-postgres and target-snowflake schema to be overridden through config, with default based on pipeline's extractor's namespace
- [#2062](https://gitlab.com/meltano/meltano/-/issues/2062) Support `--database-uri` option and `MELTANO_DATABASE_URI` env var on `meltano init`
- [#2062](https://gitlab.com/meltano/meltano/-/issues/2062) Add support for PostgreSQL 12 as a system database by updating SQLAlchemy

### Changes

- [!1664](https://gitlab.com/meltano/meltano/-/merge_requests/1664) Infer compatibility between extractor and transform based on namespace rather than name
- [!1664](https://gitlab.com/meltano/meltano/-/merge_requests/1664) Determine transform dbt model name based on namespace instead of than replacing `-` with `_` in name
- [!1664](https://gitlab.com/meltano/meltano/-/merge_requests/1664) Don't pass environment variables with "None" values to plugins if variables were unset
- [!1664](https://gitlab.com/meltano/meltano/-/merge_requests/1664) Determine Meltano Analyze schema based on transformer's `target_schema` or loader's `schema` instead of `MELTANO_ANALYZE_SCHEMA` env var
- [#2053](https://gitlab.com/meltano/meltano/-/issues/2053) Bump dbt version to 0.16.1

### Fixes

- [#2059](https://gitlab.com/meltano/meltano/-/issues/2059) Properly handle errors in before/after install hooks

## 1.33.0 - (2020-05-21)

---

### Changes

- [#2028](https://gitlab.com/meltano/meltano/-/issues/2028) Improve descriptions and default values of `meltano add --custom` prompts

### Fixes

- [#2042](https://gitlab.com/meltano/meltano/-/issues/2042) Fix bug causing Connection Setup UI to fail when plugin docs URL is not set
- [#2045](https://gitlab.com/meltano/meltano/-/issues/2045) Hide plugin logo in UI if image file could not be found
- [#2043](https://gitlab.com/meltano/meltano/-/issues/2043) Use plugin name in UI when label is not set, instead of not showing anything
- [#2044](https://gitlab.com/meltano/meltano/-/issues/2044) Don't show button to open Log Modal on Pipelines page if pipeline has never run

## 1.32.1 - (2020-05-15)

---

### Fixes

- [#2024](https://gitlab.com/meltano/meltano/-/issues/2024) Have plugin venvs not inherit Meltano venv to prevent wrong versions of modules from being loaded

## 1.32.0 - (2020-05-11)

---

### New

- [#2019](https://gitlab.com/meltano/meltano/-/issues/2019) Ask for setting names when adding a new custom plugin

### Changes

- [#2011](https://gitlab.com/meltano/meltano/-/issues/2011) Make tap-gitlab private_token setting optional for easier extraction of public groups and projects
- [#2012](https://gitlab.com/meltano/meltano/-/issues/2012) Add target-jsonl loader

### Fixes

- [#2010](https://gitlab.com/meltano/meltano/-/issues/2010) Fix bug causing dot-separated config keys to not be nested in generated tap or target config
- [#2020](https://gitlab.com/meltano/meltano/-/issues/2020) Fix bug that caused `meltano select` to add `select` option to every plugin in `meltano.yml` instead of just the specified one
- [#2021](https://gitlab.com/meltano/meltano/-/issues/2021) Only ask for capabilities when adding a custom extractor, not a loader or other plugin

## 1.31.0 - (2020-05-04)

---

### Changes

- [#1987](https://gitlab.com/meltano/meltano/-/issues/1987) Restore GitLab and Zendesk data sources in UI
- [#2005](https://gitlab.com/meltano/meltano/-/issues/2005) Add "Don't see your data source here?" option in UI
- [#2008](https://gitlab.com/meltano/meltano/-/issues/2008) Clarify that pipelines UI only supports target-postgres
- [#2007](https://gitlab.com/meltano/meltano/-/issues/2007) Don't install airflow, dbt and target-postgres by default as part of 'meltano init'
- [#2007](https://gitlab.com/meltano/meltano/-/issues/2007) Only run 'airflow scheduler' as part of 'meltano ui' when airflow is installed
- [#2007](https://gitlab.com/meltano/meltano/-/issues/2007) Install airflow, dbt, and target-postgres on DigitalOcean images

## 1.30.1 - (2020-04-23)

---

### Fixes

- [#1985](https://gitlab.com/meltano/meltano/-/issues/1985) Fixed bug with Airflow installs WTForms 2.3.0 instead of 2.2.1, which is incompatible

## 1.30.0 - (2020-04-20)

---

### New

- [#1953](https://gitlab.com/meltano/meltano/-/issues/1953) Show design attribute descriptions in tooltips in report builder
- [#1787](https://gitlab.com/meltano/meltano/-/issues/1787) Show Shopify extractor in UI

### Changes

- [!1611](https://gitlab.com/meltano/meltano/-/merge_requests/1611) Only show design description if it is different from design label

## 1.29.1 - (2020-04-16)

---

### New

- [#1948](https://gitlab.com/meltano/meltano/-/issues/1948) Show Intercom button in bottom right on MeltanoData.com instances
- [#1930](https://gitlab.com/meltano/meltano/-/issues/1930) Add button to remove report from dashboard when editing dashboard
- [#1845](https://gitlab.com/meltano/meltano/-/issues/1845) Add button to delete report to report builder interface
- [#1849](https://gitlab.com/meltano/meltano/-/issues/1849) Add button to rename report to report builder interface
- [#1951](https://gitlab.com/meltano/meltano/-/issues/1951) Add button to edit dashboard name and description to dashboard page

### Changes

- [!1607](https://gitlab.com/meltano/meltano/-/merge_requests/1607) Move date range picker into results area of report builder interface
- [!1608](https://gitlab.com/meltano/meltano/-/merge_requests/1608) Make report title more prominent in report builder

## 1.29.0 - (2020-04-13)

---

## 1.28.1 - (2020-04-09)

---

### New

- [#1940](https://gitlab.com/meltano/meltano/-/issues/1940) Show Google Ads extractor in UI

### Changes

- [#1941](https://gitlab.com/meltano/meltano/-/issues/1941) Suggest disabling ad blocker if inline docs iframe for an Ads or Analytics extractor failed to load
- [#1667](https://gitlab.com/meltano/meltano/-/issues/1667) Have 'meltano init' create system database and install airflow, dbt, and target-postgres plugins

### Fixes

- [#1942](https://gitlab.com/meltano/meltano/-/issues/1942) Ensure navigation bar is hidden in production when docs are viewed inline

## 1.28.0 - (2020-04-06)

---

### New

- [#1937](https://gitlab.com/meltano/meltano/-/issues/1937) Add optional `plugin_type` argument to `meltano install` to only (re)install plugins of a certain type

### Fixes

- [#1938](https://gitlab.com/meltano/meltano/-/issues/1938) Display error message when viewing dashboard before pipeline has run

## 1.27.3 - (2020-04-02)

---

### Fixes

- [#1938](https://gitlab.com/meltano/meltano/-/issues/1938) Fix regression causing dashboards and reports not to load when readonly mode is enabled (like on the demo instance)

## 1.27.2 - (2020-04-02)

---

### Fixes

- [#1936](https://gitlab.com/meltano/meltano/-/issues/1936) Fix regression causing UI to fail when analytics/tracking is enabled

## 1.27.1 - (2020-04-02)

---

### New

- [#1477](https://gitlab.com/meltano/meltano/-/issues/1477) Allow read-only mode and authentication to be used at the same time, to allow anonymous read-only access and only require authentication for write actions.
- [#1914](https://gitlab.com/meltano/meltano/-/issues/1914) Allow default dashboards and reports to be updated in place if package contains snapshots of older versions
- [#1933](https://gitlab.com/meltano/meltano/-/issues/1933) Allow Meltano UI Google Analytics ID to be overridden using environment variable

### Changes

- [#1896](https://gitlab.com/meltano/meltano/-/issues/1896) Set pipeline update interval to daily by default, to start after first successful manual run
- [#1888](https://gitlab.com/meltano/meltano/-/issues/1888) Explain in "Edit Connection" button tooltip why it may be disabled
- [#1890](https://gitlab.com/meltano/meltano/-/issues/1890) Clarify that changing Start Date requires a new pipeline to be set up
- [#1892](https://gitlab.com/meltano/meltano/-/issues/1892) Clarify in Run Log modal that the "Explore" button can also be found on the Connections page
- [#1891](https://gitlab.com/meltano/meltano/-/issues/1891) Show data source logo and label in Run Log modal header insteadof pipeline ID
- [#1893](https://gitlab.com/meltano/meltano/-/issues/1893) Hide "Download Log" button while pipeline is running instead of disabling it
- [#1894](https://gitlab.com/meltano/meltano/-/issues/1894) Suggest connecting a data source on Pipelines page when there are no pipelines yet
- [#1912](https://gitlab.com/meltano/meltano/-/issues/1912) Suggest user gets in touch if the report they're looking for is not included by default

### Fixes

- [#1911](https://gitlab.com/meltano/meltano/-/issues/1911) Display "Last updated: Updating..." instead of "Last updated: 1969-12-31" on reports while pipeline is running
- [#1910](https://gitlab.com/meltano/meltano/-/issues/1910) Fix pipeline "Start date" and report "Data starting from" off-by-1 errors caused by timezone differences

## 1.27.0 - (2020-03-30)

---

### Changes

- [#1909](https://gitlab.com/meltano/meltano/-/issues/1909) Suggest disabling ad blocker if request related to an Ads or Analytics extractor was blocked by browser
- [#1886](https://gitlab.com/meltano/meltano/-/issues/1886) Don't prepopulate date fields that are not required and are better left blank
- [#1887](https://gitlab.com/meltano/meltano/-/issues/1887) Hide End Date fields in connection setup since our end-users will want to import everything
- [#1905](https://gitlab.com/meltano/meltano/-/issues/1905) Hide Google Analytics Reports field from UI since startup founder end-users will stick with default

### Fixes

- [#1920](https://gitlab.com/meltano/meltano/-/issues/1920) Fix extractor logo on Google Analytics Explore page
- [#1895](https://gitlab.com/meltano/meltano/-/issues/1895) Fix bug causing newly created pipeline not to show as running when it is
- [#1906](https://gitlab.com/meltano/meltano/-/issues/1906) Fix "Test Connection" for extractors that require a file to be uploaded, like Google Analytics
- [#1931](https://gitlab.com/meltano/meltano/-/issues/1931) Validate uploaded file path when saving or testing connection settings

## 1.26.2 - (2020-03-26)

---

### Fixes

- [#1883](https://gitlab.com/meltano/meltano/-/issues/1883) Fix dashboard and embedded reports failing to load when design has no joins

## 1.26.1 - (2020-03-26)

---

### Changes

- [#1854](https://gitlab.com/meltano/meltano/-/issues/1854) Remove non-marketing-sales data sources from UI
- [#1881](https://gitlab.com/meltano/meltano/-/issues/1881) Store in system database when user was last active
- [#1846](https://gitlab.com/meltano/meltano/-/issues/1846) Freeze reports with relative date filters in time when shared or embedded
- [#1847](https://gitlab.com/meltano/meltano/-/issues/1847) Show date range on embedded reports and dashboards
- [#1847](https://gitlab.com/meltano/meltano/-/issues/1847) Show date range on reports on dashboards

## 1.26.0 - (2020-03-23)

---

### Changes

- [#1188](https://gitlab.com/meltano/meltano/-/issues/1188) Allow sorting by timeframe period columns (e.g. "Creation Date: Month", "Creation Date: Year")
- [#1873](https://gitlab.com/meltano/meltano/-/issues/1873) Display error message when viewing model/design/report before pipeline has run
- [#1874](https://gitlab.com/meltano/meltano/-/issues/1874) Print full error when initial model compilation fails
- [#1875](https://gitlab.com/meltano/meltano/-/issues/1875) Automatically run query when sorting is changed
- [#1876](https://gitlab.com/meltano/meltano/-/issues/1876) Don't store Analyze UI state in report file
- [#1877](https://gitlab.com/meltano/meltano/-/issues/1877) Allow designs to reference the same table more than once
- [#1878](https://gitlab.com/meltano/meltano/-/issues/1878) Recompile models when meltano is upgraded

## 1.25.1 - (2020-03-19)

---

### New

- [#1799](https://gitlab.com/meltano/meltano/issues/1799) Improve date range UX by displaying the date range associated with each attribute in the `<select>` (previously the user had to manually check each one-by-one to see if it had an associated date range filter)

### Changes

- [#1799](https://gitlab.com/meltano/meltano/issues/1799) Update "Date Range(s)" button label to account for pluralization
- [#1799](https://gitlab.com/meltano/meltano/issues/1799) Fallback to inline text and only display the date range `<select>` if there are two or more date ranges to filter on
- [#1799](https://gitlab.com/meltano/meltano/issues/1799) Update date range picker to initialize at the first attribute with a valid date range
- [#1799](https://gitlab.com/meltano/meltano/issues/1799) Update the Report Builder's "jump to date range dropdown" buttons (small calendar icon button associated with the left pane's attribute items) to automatically focus the date range that's associated

### Fixes

- [#1872](https://gitlab.com/meltano/meltano/-/issues/1872) Delete state left over from different pipeline run for same extractor
- [#1779](https://gitlab.com/meltano/meltano/-/issues/1779) Fix loading report directly by URL when design request completes before reports request

## 1.25.0 - (2020-03-16)

---

### New

- [#1843](https://gitlab.com/meltano/meltano/issues/1843) Update the Google Ads Extractor selected attributes definition to also extract the Ad Network and Device segments for the Ads Performance Reports.

### Changes

- [#1852](https://gitlab.com/meltano/meltano/-/issues/1852) Move Pipelines after Connections in navbar
- [#1850](https://gitlab.com/meltano/meltano/-/issues/1850) Rename Connections tab "Connection" and "Pipeline" buttons to "Edit Connection", and "View Pipeline"
- [#1856](https://gitlab.com/meltano/meltano/-/issues/1856) Remove "Custom" data source option from UI
- [#1867](https://gitlab.com/meltano/meltano/-/issues/1867) Make timeframe table headings more human-friendly

### Fixes

- [#1848](https://gitlab.com/meltano/meltano/-/issues/1848) Fix Explore page "Report Builder" column loading when model name and model topic name do not match

## 1.24.1 - (2020-03-12)

---

### New

- [!1523](https://gitlab.com/meltano/meltano/merge_requests/1523) Add support for relative date filter definitions to Meltano Filters. That means that filters over dates and times can have a `[+-]N[dmy]` format instead of a fixed date. That allows Meltano to generate a date relative to a pivot date provided by in the query definition or `NOW()`.
- [#1830](https://gitlab.com/meltano/meltano/issues/1830) Add relative vs. absolute date ranges to date range picker of Report Builder

### Changes

- [#1830](https://gitlab.com/meltano/meltano/issues/1830) Update date ranges calendars with "Today" marker for improved UX

## 1.24.0 - (2020-03-09)

---

### Changes

- [#1831](https://gitlab.com/meltano/meltano/issues/1831) Change main navigation "Reports" to "Explore" and update its nested CTAs to link to a landing page per data source
- [#1705](https://gitlab.com/meltano/meltano/issues/1705) Remove `meltano permissions` feature now that it has been extracted into https://gitlab.com/gitlab-data/permifrost.
- Updated "Report Builder" page with a header to better communicate what the page is for.

### Fixes

- [#1840](https://gitlab.com/meltano/meltano/-/issues/1840) Format InputDateIso8601 value as YYYY-MM-DD since a full timestamp value could represent a different date in UTC and local timezone
- [#1842](https://gitlab.com/meltano/meltano/issues/1842) Fix empty filter attributes bug for non-join designs

## 1.23.2 - (2020-03-05)

---

### New

- [#1820](https://gitlab.com/meltano/meltano/issues/1820) Add Vertical Bar chart type to Report chart options

### Changes

- [#1820](https://gitlab.com/meltano/meltano/issues/1820) Updated chart type selection as a dropdown for improved UX (ensures the chart icon is adorned with its label)

### Fixes

- [#1837](https://gitlab.com/meltano/meltano/issues/1837) Fix tap-mongodb database name setting
- [#1838](https://gitlab.com/meltano/meltano/issues/1838) Properly handle dates and timezones in date range picker
- [#1838](https://gitlab.com/meltano/meltano/issues/1838) Ensure records on boundary dates are included when using date range picker with column of type "time"

## 1.23.1 - (2020-03-04)

---

### Fixes

- [#1836](https://gitlab.com/meltano/meltano/issues/1820) Don't crash when gunicorn is sent HUP signal to reload Meltano service

## 1.23.0 - (2020-03-02)

---

### New

- [#1601](https://gitlab.com/meltano/meltano/issues/1601) Add Explore landing pages per data source to act as an aggregate jump-off point to related dashboards, reports, report templates, and more

### Changes

- [#1601](https://gitlab.com/meltano/meltano/issues/1601) Change "Reports" CTA in each Pipeline and the JobLog modal to link to its corresponding and newly added Explore page
- [#1698](https://gitlab.com/meltano/meltano/issues/1698) Change information architecture to separate Connections and Pipelines into distinct pages

### Fixes

- [#1811](https://gitlab.com/meltano/meltano/issues/1811) Fix an issue when installing a custom plugin.
- [#1794](https://gitlab.com/meltano/meltano/issues/1794) Remove the notification field when notifications are disabled.
- [#1815](https://gitlab.com/meltano/meltano/issues/1815) Fix `mapActions` misplacement in `computed` vs. `methods`
- [#1468](https://gitlab.com/meltano/meltano/issues/1468) Update asn1crypto to get Meltano to work on macOS Catalina

## 1.22.2 - (2020-02-27)

---

### Fixes

- [#1809](https://gitlab.com/meltano/meltano/issues/1809) Fix LogModal padding render issue and `TypeError` with proper conditional check prior to dereferencing
- [#1810](https://gitlab.com/meltano/meltano/issues/1810) Fix an issue where Notifications would not be sent when the application used multiple workers

## 1.22.1 - (2020-02-26)

---

### New

- [#1783](https://gitlab.com/meltano/meltano/issues/1873) Add Shopify extractor as a hidden plugin
- [#1499](https://gitlab.com/meltano/meltano/issues/1499) Add date range selector to Analyze UI (requires a `type=date` or `type=time` in each model needing this functionality)

### Changes

- [#1777](https://gitlab.com/meltano/meltano/issues/1777) Update Meltano Analyze to only preselect the first column and aggregate attributes when no attributes have a `require`d setting
- [#1796](https://gitlab.com/meltano/meltano/issues/1796) Update date range and filter changes to trigger autorun if enabled

### Fixes

- [#1798](https://gitlab.com/meltano/meltano/issues/1798) Add OK button to toasts that couldn't be dismissed previously, to prevent them from getting in the way of modal buttons
- [#1803](https://gitlab.com/meltano/meltano/issues/1803) Ensure SMTP credentials can be set via environment variables
- [#1778](https://gitlab.com/meltano/meltano/issues/1778) Fix missing pipeline date when visiting page directly from URL

## 1.22.0 - (2020-02-24)

---

### New

- [#1646](https://gitlab.com/meltano/meltano/issues/1646) Add default Stripe dashboard
- [#1759](https://gitlab.com/meltano/meltano/issues/1759) Add default reports and dashboard for Google Ads data
- [#1775](https://gitlab.com/meltano/meltano/issues/1775) Add default dashboard for GitLab extractor
- [#1714](https://gitlab.com/meltano/meltano/issues/1714) Add support for a `required` setting in Models so Analyze can still work with more complex reporting scenarios (Facebook and Google Adwords need this)
- [#1780](https://gitlab.com/meltano/meltano/issues/1780) Add default reports and dashboard for Facebook Ads data

## 1.21.2 - (2020-02-18)

---

### New

- [#1740](https://gitlab.com/meltano/meltano/issues/1740) Add "Sharing Reports and Dashboards" section to Getting Started guide
- [#1484](https://gitlab.com/meltano/meltano/issues/1484) Add a subscription field to be notified when a Pipeline will be completed.

### Changes

- [#1740](https://gitlab.com/meltano/meltano/issues/1740) Update Getting Started guide screenshots with up-to-date UI

### Fixes

- [#1751](https://gitlab.com/meltano/meltano/issues/1751) Custom report ordering now works based on user customization
- [#1756](https://gitlab.com/meltano/meltano/issues/1756) Fix embed app to properly render based on `report` or `dashboard` type

## 1.21.1 - (2020-02-17)

---

### Fixes

- [#1754](https://gitlab.com/meltano/meltano/issues/1754) Fix duplicate "Share" button and Reports dropdown clipping issue

## 1.21.0 - (2020-02-17)

---

### New

- [#609](https://gitlab.com/meltano/meltano/issues/609) Add the Google Ads Extractor to Meltano as a hidden plugin. It will be fully enabled on Meltano UI once OAuth support is added. It uses the tap defined in https://gitlab.com/meltano/tap-adwords/
- [#1693](https://gitlab.com/meltano/meltano/issues/1693) Add default transformations for the Google Ads Extractor. They are using the dbt package defined in https://gitlab.com/meltano/dbt-tap-adwords
- [#1694](https://gitlab.com/meltano/meltano/issues/1694) Add default Meltano Models for the Google Ads Extractor. They are defined in https://gitlab.com/meltano/model-adwords
- [#1695](https://gitlab.com/meltano/meltano/issues/1695) Add documentation for the Google Ads Extractor
- [#1723](https://gitlab.com/meltano/meltano/issues/1723) Add various mobile and widescreen related style tweaks to improve base layout at mobile and widescreen widths

### Changes

- [!1460](https://gitlab.com/meltano/meltano/merge_requests/1460) Remove the FTP access from Meltano hosted instances
- [#1629](https://gitlab.com/meltano/meltano/issues/1629) Add "Share Dashboard" functionality
- [#1629](https://gitlab.com/meltano/meltano/issues/1629) Update report "Embed" button to "Share" and include a share link to accompany the embed snippet

### Fixes

- [#1680](https://gitlab.com/meltano/meltano/issues/1680) Fix initial "Last Run" button of a pipeline run to properly open the corresponding job log

## 1.20.1 - (2020-02-13)

---

### New

- [#1650](https://gitlab.com/meltano/meltano/issues/1650) create TOS page and add TOS link to website footer

### Changes

- [#1681](https://gitlab.com/meltano/meltano/issues/1681) Update `transform` during pipeline save to conditionally set `skip` vs. `run` to prevent wasted cycles for extractors that lack transformations
- [#1696](https://gitlab.com/meltano/meltano/issues/1696) Update dashboards list to be alphabetically sorted
- [#1710](https://gitlab.com/meltano/meltano/issues/1710) Hide `tap-fastly` in UI

### Fixes

- [#1696](https://gitlab.com/meltano/meltano/issues/1696) Fix duplicate chart renders when dashboard is loaded
- [#1696](https://gitlab.com/meltano/meltano/issues/1696) Fix "Add to Dashboards" button when loading an existing report (additionally updated `disabled` button states)
- [#1711](https://gitlab.com/meltano/meltano/issues/1711) Disable fields of all kinds when a plugin setting is protected or set in env or meltano.yml
- [#1712](https://gitlab.com/meltano/meltano/issues/1712) Fix lock icon tooltip message on plugin settings that were set in env or meltano.yml
- [#1677](https://gitlab.com/meltano/meltano/issues/1677) Properly represent values of boolean settings that were set using environment verariables in UI

## 1.20.0 - (2020-02-10)

---

### New

- [#1682](https://gitlab.com/meltano/meltano/issues/1682) Use human-readable update interval labels

### Changes

- [#1514](https://gitlab.com/meltano/meltano/issues/1514) Remove DBT docs integration
- [#1679](https://gitlab.com/meltano/meltano/issues/1679) Prevent the `hidden` settings from being sent to the front-end, potentially causing configuration failure

### Fixes

- [#1675](https://gitlab.com/meltano/meltano/issues/1675) Fix future grant diffing for databases and schemas
- [#1674](https://gitlab.com/meltano/meltano/issues/1674) Fix duplicate pipelines bug resulting from recent addition to view and update existing connections

## 1.19.2 - (2020-02-06)

---

### Fixes

- [#1672](https://gitlab.com/meltano/meltano/issues/1672) Pin Werkzeug version to 0.16.1 since 1.0.0 is unsupported by Flask-BabelEx

## 1.19.1 - (2020-02-06)

---

### Fixes

- [#1671](https://gitlab.com/meltano/meltano/issues/1671) Fix error handling bug that caused a console error that impacted further UI interaction

## 1.19.0 - (2020-02-06)

---

### New

- [#1545](https://gitlab.com/meltano/meltano/issues/1545) Add read-only report embed functionality via embeddable `iframe` copy-to-clipboard snippet
- [#1606](https://gitlab.com/meltano/meltano/issues/1606) Update UI after successful plugin configuration with auto installed reports and dashboards
- [#1614](https://gitlab.com/meltano/meltano/issues/1614) Add 'Fix Connection' and 'View Connection' CTAs to Integrations with corresponding pipelines
- [#1550](https://gitlab.com/meltano/meltano/issues/1550) Add the Meltano OAuth Service integration to manage the OAuth flow in the plugin configuration

### Changes

- [#1594](https://gitlab.com/meltano/meltano/issues/1594) Improve onboarding UX by moving the "Update Interval" selection to a post-successful-pipeline action
- [#1594](https://gitlab.com/meltano/meltano/issues/1594) Update pipelines to be sorted alphabetically to match data sources organization
- [#1659](https://gitlab.com/meltano/meltano/issues/1659) Update query attribute toggling and results UX when autorun query is on (via 500ms debounce)
- [#1475](https://gitlab.com/meltano/meltano/issues/1475) GitLab extractor in the UI steers user towards a single data source

### Fixes

- [#1657](https://gitlab.com/meltano/meltano/issues/1657) Fix `update_dashboard` error when payload lacked a `new_settings` key
- [#1602](https://gitlab.com/meltano/meltano/issues/1602) Fix instances where `<a disabled='...'>` vs. `<button disabled='...'>` didn't functionally disable the button (previously they were only disabled visually)
- [#1656](https://gitlab.com/meltano/meltano/issues/1656) Fix conditional header in docs to support Meltano.com and inline docs within the Meltano app

## 1.18.0 - (2020-02-03)

---

### New

- [#1154](https://gitlab.com/meltano/meltano/issues/1154) Adds non-dry mode to `meltano permissions` on Snowflake so that queries can be executed
- [#1578](https://gitlab.com/meltano/meltano/issues/1578) User can request help to delete their data from their MeltanoData instance

### Changes

- [#1516](https://gitlab.com/meltano/meltano/issues/1516) Pipelines now show extractor label rather than name
- [#1652](https://gitlab.com/meltano/meltano/issues/1652) Removes the `--full-refresh` command from `meltano permissions`

### Fixes

- [#1595](https://gitlab.com/meltano/meltano/issues/1595) Updates `meltano permissions` to only revoke permissions on databases defined in the spec
- [#1588](https://gitlab.com/meltano/meltano/issues/1588) Update `scrollTo` behavior in Job Log to work across browsers
- [#1660](https://gitlab.com/meltano/meltano/issues/1660) Fix minor action/mutation bug when loading a report in Analyze
- [#1607](https://gitlab.com/meltano/meltano/issues/1607) Fix inaccurate error during report additions/removal from dashboards (via refactor SSOT reports store)

## 1.17.1 - (2020-01-29)

---

### Changes

- [#1625](https://gitlab.com/meltano/meltano/issues/1625) Update docs on meltano.com to only include extractors and loaders provided in the hosted version of Meltano.
- [#1590](https://gitlab.com/meltano/meltano/issues/1590) Add additional targets to `dbt clean`
- [#1655](https://gitlab.com/meltano/meltano/issues/1655) Add UX message to close buttons in Job Log Modal to reinforce that the pipeline still runs after closing (Ben's hover idea)

### Fixes

- [#1618](https://gitlab.com/meltano/meltano/issues/1618) Fix an issue where an expired session would not redirect to the Login page
- [#1630](https://gitlab.com/meltano/meltano/issues/1630) Fix an integrations setup bug that prevented subsequent pipelines to be created unless a full page refresh occurred

## 1.17.0 - (2020-01-27)

---

### New

- [#1462](https://gitlab.com/meltano/meltano/issues/1462) User will be able to reorder dashboard reports
- [#1482](https://gitlab.com/meltano/meltano/issues/1482) Add future grants and revocations for schemas, tables, and views for roles in the `meltano permissions` command
- [#1376](https://gitlab.com/meltano/meltano/issues/1376) Add last updated date to reports
- [#1409](https://gitlab.com/meltano/meltano/issues/1409) Add data start date to Analysis page

- [#1241](https://gitlab.com/meltano/meltano/issues/1241) Add `dashboard` plugin type to enable bundling curated reports and dashboards for data sources
- [#1241](https://gitlab.com/meltano/meltano/issues/1241) Add `--include-related` flag to `meltano add` and `meltano install` to automatically install related plugins based on namespace
- [#1241](https://gitlab.com/meltano/meltano/issues/1241) Add default dashboard and reports for Google Analytics

### Changes

- [#1481](https://gitlab.com/meltano/meltano/issues/1481) Add table and view revocations for roles in the `meltano permissions` command
- [#1459](https://gitlab.com/meltano/meltano/issues/1459) Users can no longer install tap-carbon-intensity from the UI

### Fixes

- [#1600](https://gitlab.com/meltano/meltano/issues/1600) Fix tooltip for Data Source "Connect" buttons
- [#1605](https://gitlab.com/meltano/meltano/issues/1605) Fix an infinite loop causing extraneous API calls to the configuration endpoint
- [#1561](https://gitlab.com/meltano/meltano/issues/1561) Fix `onFocusInput()` to properly focus-and-auto-scroll to `<input type='file'>`s in the data source docs UI
- [#1561](https://gitlab.com/meltano/meltano/issues/1561) Fix `<input type='file'>` styling to better accommodate flexible widths

## 1.16.1 - (2020-01-23)

---

### New

- [#1592](https://gitlab.com/meltano/meltano/issues/1592) Add MAX and MIN aggregate functions to Meltano Models
- [#1552](https://gitlab.com/meltano/meltano/issues/1552) Add "Custom" data source CTA to link to the create custom data source docs
- [#1462](https://gitlab.com/meltano/meltano/issues/1462) User will be able to reorder dashboard reports

### Changes

- [#1510](https://gitlab.com/meltano/meltano/issues/1510) Remove breadcrumbs (not currently useful)
- [#1589](https://gitlab.com/meltano/meltano/issues/1589) Add dbt-specific files to a .gitignore
- [#1402](https://gitlab.com/meltano/meltano/issues/1402) Onboarding redesign to minimize steps and friction ('Extractors' as 'Data Sources', pipelines are secondary to 'Data Source' integrations, and removed loader, transform, and pipeline name as editable in favor of preselected values in accordance with our hosted solution)
- [#1402](https://gitlab.com/meltano/meltano/issues/1402) Local development now requires `.env` to connect a `target-postgres` loader (docs update to follow in [#1586](https://gitlab.com/meltano/meltano/issues/1586) )
- [#1410](https://gitlab.com/meltano/meltano/issues/1410) Update the Design UI to expose timeframes explicitly

### Fixes

- [#1573](https://gitlab.com/meltano/meltano/issues/1573) Fix docs `shouldShowNavbar` conditional and improve query string `embed=true` parsing
- [#1579](https://gitlab.com/meltano/meltano/issues/1579) Make color contrast for CTA buttons accessible
- [#1410](https://gitlab.com/meltano/meltano/issues/1410) Fix a problem with Report that has timeframes selections

### Breaks

## 1.16.0 - (2020-01-20)

---

### New

- [#1556](https://gitlab.com/meltano/meltano/issues/1556) Add default transformations for the Facebook Ads Extractor. They are using the dbt package defined in https://gitlab.com/meltano/dbt-tap-facebook
- [#1557](https://gitlab.com/meltano/meltano/issues/1557) Add default Meltano Models for the Facebook Ads Extractor. They are defined in https://gitlab.com/meltano/model-facebook
- [#1560](https://gitlab.com/meltano/meltano/issues/1560) Make the Facebook Ads Extractor available by default on Meltano UI

### Changes

- [#1541](https://gitlab.com/meltano/meltano/issues/1541) Revert `tap-csv`'s `kind: file` to text input for `csv_files_definition` as we don't fully support `tap-csv` via the UI with single (definition json) and multiple (csv files) file uploading
- [#1477](https://gitlab.com/meltano/meltano/issues/1477) Add a `read-only` mode to Meltano to disable all modifications from the UI

### Fixes

### Breaks

## 1.15.1 - (2020-01-16)

---

### New

- [#608](https://gitlab.com/meltano/meltano/issues/608) Add the Facebook Ads Extractor to Meltano as a hidden plugin. It will be fully enabled on Meltano UI once bundled Transformations and Models are added. It uses the tap defined in https://gitlab.com/meltano/tap-facebook/
- [meltano/model-stripe#2](https://gitlab.com/meltano/model-stripe/issues/2) Add timeframes to the Stripe models
- [#1533](https://gitlab.com/meltano/meltano/issues/1533) Add documentation for the Facebook Ads Extractor

### Changes

- [#1527](https://gitlab.com/meltano/meltano/issues/1527) Update the dashboard modal header to properly differentiate between "Create" and "Edit"
- [#1456](https://gitlab.com/meltano/meltano/issues/1456) 404 Error page now has better back functionality and ability to file new issues directly from the page

### Fixes

- [#1538](https://gitlab.com/meltano/meltano/issues/1538) Fix timeframes not properly displaying on the base table
- [#1574](https://gitlab.com/meltano/meltano/issues/1574) Fix an issue with Meltano crashing after a succesful login
- [#1568](https://gitlab.com/meltano/meltano/issues/1568) Restore support for custom plugins that don't have their available settings defined in discovery.yml

## 1.15.0 - (2020-01-13)

---

### New

- [#1483](https://gitlab.com/meltano/meltano/issues/1483) Add login audit columns to track last login time
- [#1480](https://gitlab.com/meltano/meltano/issues/1480) Add tests to `meltano permissions` command for Snowflake
- [#1392](https://gitlab.com/meltano/meltano/issues/1392) Add inline docs to Extractor configurations in iteration toward improving data setup onboarding

### Changes

- [#1480](https://gitlab.com/meltano/meltano/issues/1480) Add schema revocations for roles in the `meltano permissions` command
- [#1458](https://gitlab.com/meltano/meltano/issues/1458) Remove tap-carbon-intensity-sqlite model from default installation
- [#1458](https://gitlab.com/meltano/meltano/issues/1458) Update docs to reflect new getting started path and updated screenshots
- [#1513](https://gitlab.com/meltano/meltano/issues/1513) Remove dead code related to `/model` route that we no longer link to in favor of the contextual Analyze CTAs and the `MainNav.vue`'s Analyze dropdown
- [#1542](https://gitlab.com/meltano/meltano/issues/1542) Update version, logout, and help UI partial (upper right) to have less prominence and more clearly communicate the "Sign Out" action

### Fixes

- [#1480](https://gitlab.com/meltano/meltano/issues/1480) Fix database revocations corner case for roles in the `meltano permissions` command
- [#1553](https://gitlab.com/meltano/meltano/issues/1553) Fix bug occurring when loading a report that lacks join tables
- [#1540](https://gitlab.com/meltano/meltano/issues/1540) Meltano Analyze will now leverage Pipelines instead of Loaders in the connection dropdown
- [#1540](https://gitlab.com/meltano/meltano/issues/1540) Meltano Analyze will now infer the connection to use instead of it being provided by the user

### Breaks

## 1.14.3 - (2020-01-09)

---

### Fixes

- [#1521](https://gitlab.com/meltano/meltano/issues/1521) Sanitize user-submitted string before using it in file path

## 1.14.2 - (2020-01-09)

---

### New

- [#1391](https://gitlab.com/meltano/meltano/issues/1391) Lock all settings that are controlled through environment variables
- [#1393](https://gitlab.com/meltano/meltano/issues/1393) Add contextual Analyze CTAs for each Pipeline in the Pipelines list
- [#1551](https://gitlab.com/meltano/meltano/issues/1551) Add dbt clean before compile and runs

### Changes

- [#1424](https://gitlab.com/meltano/meltano/issues/1424) Update pipeline elapsed time display to be more human friendly

### Fixes

- [#1430](https://gitlab.com/meltano/meltano/issues/1430) Fix the state not stored for pipelines when Transforms run
- [#1448](https://gitlab.com/meltano/meltano/issues/1448) Fix `AnalyzeList.vue` to display message and link when lacking contextual models

### Breaks

## 1.14.1 - (2020-01-06)

---

### Fixes

- [#1520](https://gitlab.com/meltano/meltano/issues/1520) Fix bug when updating a dashboard that could undesirably overwrite another existing dashboard

### Breaks

## 1.14.0 - (2019-12-30)

---

### New

- [#1461](https://gitlab.com/meltano/meltano/issues/1461) Display toasted notification for report adding to dashboard
- [#1419](https://gitlab.com/meltano/meltano/issues/1419) Add ability to edit and delete dashboards
- [#1411](https://gitlab.com/meltano/meltano/issues/1411) Add download log button to Job Log Modal

### Changes

- [#1311](https://gitlab.com/meltano/meltano/issues/1311) Remove unused meltano/meltano/runner docker image
- [#1502](https://gitlab.com/meltano/meltano/issues/1502) Update configuration file uploads to occur on save vs. file picker completion

### Fixes

- [#1518](https://gitlab.com/meltano/meltano/issues/1518) Fix bug that caused all text fields to show up as required in configuration modals
- [#1446](https://gitlab.com/meltano/meltano/issues/1446) Fix bug that could result in a broken report when the report URL was manually modified
- [#1411](https://gitlab.com/meltano/meltano/issues/1411) Fix bug when reading too large a job log file

## 1.13.0 - (2019-12-23)

---

### New

- [#1269](https://gitlab.com/meltano/meltano/issues/1269) Add `kind: file` so single file uploads can be used with extractors (`tap-google-analytics`'s `key_file_location` is the first user)
- [#1494](https://gitlab.com/meltano/meltano/issues/1494) Add `LIKE` options to Analyze Filter UI so users better understand what filtering patterns are available

### Changes

- [#1399](https://gitlab.com/meltano/meltano/issues/1399) Log Modal now has a prompt to explain potential factors in required time for pipelines to complete
- [#1433](https://gitlab.com/meltano/meltano/issues/1433) Remove `/orchestrate` route and thus the Airflow iframe as this is overkill for our current target users

### Fixes

- [#1434](https://gitlab.com/meltano/meltano/issues/1434) Fix Analyze CTAs to only enable if at least one related pipeline has succeeded
- [#1447](https://gitlab.com/meltano/meltano/issues/1447) Various fixes around loading and reloading reports to mitigate false positive `sqlErrorMessage` conditions
- [#1509](https://gitlab.com/meltano/meltano/issues/1509) Allow plugin profile config to be set through meltano.yml

## 1.12.2 - (2019-12-20)

---

### New

- [#1437](https://gitlab.com/meltano/meltano/issues/1437) Users can now share their dashboards with an automatically generated email

### Changes

- [#1466](https://gitlab.com/meltano/meltano/issues/1466) Filters now have clear language and indiciation that they use AND for chaining
- [#1464](https://gitlab.com/meltano/meltano/issues/1464) Remove the "only" option for transforms in Create Pipeline form

- [#1399](https://gitlab.com/meltano/meltano/issues/1399) Log Modal now has a prompt to explain potential factors in required time for pipelines to complete
- [#1431](https://gitlab.com/meltano/meltano/issues/1431) Add "pipeline will still run if modal is closed" message in the Job Log Modal

### Changes

- [#1422](https://gitlab.com/meltano/meltano/issues/1422) Update start date field to have a recommendation

### Fixes

- [#1447](https://gitlab.com/meltano/meltano/issues/1447) Various fixes around loading and reloading reports to mitigate false positive `sqlErrorMessage` conditions
- [#1443](https://gitlab.com/meltano/meltano/issues/1443) Fix tooltip clipping in modals
- [#1500](https://gitlab.com/meltano/meltano/issues/1500) Fix `meltano install` not running the migrations.

## 1.12.1 - (2019-12-18)

---

### Changes

- [#1403](https://gitlab.com/meltano/meltano/issues/1403) Remove "Orchestrate", "Model", and "Notebook" from the main navigation until each respective UI is more useful (the `/orchestrate` and `/model` routes still exist)
- [#1476](https://gitlab.com/meltano/meltano/issues/1476) Add database and warehouse revocations for roles in the `meltano permissions` command
- [#1473](https://gitlab.com/meltano/meltano/issues/1473) Update Release issue template to recent guidelines

## 1.12.0 - (2019-12-16)

---

### New

- [#1374](https://gitlab.com/meltano/meltano/issues/1374) Add role revocation for users and roles in the `meltano permissions` command
- [#1377](https://gitlab.com/meltano/meltano/issues/1377) Document cleanup steps after MeltanoData testing
- [#1438](https://gitlab.com/meltano/meltano/issues/1438) Add documentation for DNS spoofing error
- [#1436](https://gitlab.com/meltano/meltano/issues/1436) Add video walkthrough on how to setup Google Analytics so that the Meltano Extractor can be able to access the Google APIs and the Google Analytics data.

### Changes

- [#1350](https://gitlab.com/meltano/meltano/issues/1350) Switch to all lower case for Snowflake permission comparisons in the `meltano permissions` command
- [#1449](https://gitlab.com/meltano/meltano/issues/1449) Hide the Marketo Extractor form Meltano UI
- [#1397](https://gitlab.com/meltano/meltano/issues/1397) Optimize workflow for MeltanoData setup
- [#1423](https://gitlab.com/meltano/meltano/issues/1423) Update sidebar and docs to include Ansible

## 1.11.2 - (2019-12-13)

---

### Changes

- [#1435](https://gitlab.com/meltano/meltano/issues/1435) Change "Model" to "Analyze" so the Pipeline CTA is actionable and less abstract
- [#1432](https://gitlab.com/meltano/meltano/issues/1432) Changed "Close" to "Back" in Log Modal to help mitigate "Am I ending the pipeline?" concerns

### Fixes

- [#1439](https://gitlab.com/meltano/meltano/issues/1439) Fix relative elapsed time since last run time display in the Pipelines UI
- [#1441](https://gitlab.com/meltano/meltano/issues/1441) Fix auto advance to "Create Pipeline" when coming from "Load" step (previously "Transform" step, but this has been removed from the UI)
- [#1440](https://gitlab.com/meltano/meltano/issues/1440) Allow installed plugins to appear in UI even if hidden in configuration

## 1.11.1 - (2019-12-12)

---

### New

- [#1351](https://gitlab.com/meltano/meltano/issues/1351) Add "Create Meltano Account" promo for `meltano.meltanodata.com`
- [#1055](https://gitlab.com/meltano/meltano/issues/1055) Add "Disable" button to Tracking Acknowledgment toast so user's can opt-out from the UI
- [#1408](https://gitlab.com/meltano/meltano/issues/1408) Add "Last Run" context to each pipeline
- [#1408](https://gitlab.com/meltano/meltano/issues/1408) Add "Started At", "Ended At", and "Elapsed" to Job Log modal
- [#1390](https://gitlab.com/meltano/meltano/issues/1390) Display of extractors and loaders can now be configured through the `hidden` property in `discovery.yml`

### Changes

- [#1398](https://gitlab.com/meltano/meltano/issues/1398) Update default Transform from "Skip" to "Run"
- [#1406](https://gitlab.com/meltano/meltano/issues/1406) Update Analyze Query section CSS for improved UX (visually improved organization and scanability)
- [#1417](https://gitlab.com/meltano/meltano/issues/1417) Update SCSS variable usage in components for SSOT styling
- [#1408](https://gitlab.com/meltano/meltano/issues/1408) Updated date and time displays to be human-friendly (`moment.js`)
- [#1268](https://gitlab.com/meltano/meltano/issues/1268) Remove Transform step from UI (Create Schedule still allows choosing "Skip" or "Only" but will intelligently default to "Skip" or "Run")

## 1.11.0 - (2019-12-09)

---

### New

- [#1361](https://gitlab.com/meltano/meltano/issues/1361) Add `kind: hidden` to `discovery.yml` so certain connector settings can validate with a default `value` but remain hidden from the user for improved UX

### Changes

- [#1389](https://gitlab.com/meltano/meltano/issues/1389) Temporary Profiles feature removal (conditionally removed if 2+ profiles not already created so existing users can continue using multiple profiles if created)
- [#1373](https://gitlab.com/meltano/meltano/issues/1373) Update MeltanoData deletion process with 1Password

### Fixes

- [#1401](https://gitlab.com/meltano/meltano/issues/1401) Fix double instance of self hosted CTA on desktop sites

## 1.10.2 - (2019-12-06)

---

### Changes

- [#1371](https://gitlab.com/meltano/meltano/issues/1371) Provide more specific instructions for Google Analytics configuration
- [#1381](https://gitlab.com/meltano/meltano/issues/1381) Update the default directory for client_secrets.json for the Google Analytics Extractor to be located under the extract/ directory and not the project's root.
- [#1345](https://gitlab.com/meltano/meltano/issues/1345) Update the documentation for the [Salesforce Extractor](https://www.meltano.com/plugins/extractors/salesforce.html) to contain additional information on Security Tokens
- [#1383](https://gitlab.com/meltano/meltano/issues/1383) Add CTA for hosted solution signup to navigation

### Fixes

- [#1379](https://gitlab.com/meltano/meltano/issues/1379) Fix an issue with Airflow scheduling too many jobs.
- [#1386](https://gitlab.com/meltano/meltano/issues/1386) Fix connector modal clipping issue where small browser heights prevented accessing the "Save" area

### Breaks

## 1.10.1 - (2019-12-05)

---

### Changes

- [#1373](https://gitlab.com/meltano/meltano/issues/1373) Update MeltanoData deletion process with 1Password
- [#1373](https://gitlab.com/meltano/meltano/issues/1373) Update Analyze dropdown as scrollable to better display model CTAs (scrollable dropdown vs. scrolling entire page)

### Fixes

- [#1373](https://gitlab.com/meltano/meltano/issues/1373) Fix formatting on custom containers in MeltanoData guide

## 1.10.0 - (2019-12-04)

---

### New

- [#1343](https://gitlab.com/meltano/meltano/issues/1343) Add current Meltano version to main navigation

### Changes

- [#1358](https://gitlab.com/meltano/meltano/issues/1358) Update MeltanoData guide with maintenance and debugging instructions
- [#1337](https://gitlab.com/meltano/meltano/issues/1337) Add CTA to installations for free hosted dashboards
- [#1365](https://gitlab.com/meltano/meltano/issues/1365) Add process for deleting meltanodata instances
- [#1340](https://gitlab.com/meltano/meltano/issues/1340) Update connector settings UI to communicate the required status of each setting
- [#1357](https://gitlab.com/meltano/meltano/issues/1357) Update LogModal Analyze CTAs so Analyze can preselect the correct loader for a given analysis

### Fixes

- [#1364](https://gitlab.com/meltano/meltano/issues/1364) Fix instructions to SSH into MeltanoData.com instance

## 1.9.1 - (2019-12-04)

---

### Fixes

- [#1355](https://gitlab.com/meltano/meltano/issues/1355) Upgrade version of `discovery.yml` so that not upgraded Meltano instances with a pre v1.9.0 Meltano version do not break.

## 1.9.0 - (2019-12-03)

---

### New

- [marketing#103](https://gitlab.com/meltano/meltano-marketing/issues/103) Add Google Site Verification token to site
- [#1346](https://gitlab.com/meltano/meltano/issues/1346) Add new tutorial for using FileZilla with a Meltano project
- [#1292](https://gitlab.com/meltano/meltano/issues/1292) Add guide for setting up Meltano projects on meltanodata.com

### Changes

- [#1341](https://gitlab.com/meltano/meltano/issues/1341) Various `discovery.yml` and connector configuration UI updates to improve UX.
- [#1341](https://gitlab.com/meltano/meltano/issues/1341) Updated documentation to communicate the various optional settings of a connector

### Fixes

- [#1334](https://gitlab.com/meltano/meltano/issues/1334) Fix automatic population of airflow.cfg after installation
- [#1344](https://gitlab.com/meltano/meltano/issues/1344) Fix an ELT automatic discovery error when running Meltano on Python3.6

## 1.8.0 - (2019-12-02)

---

### New

- [#764](https://gitlab.com/meltano/meltano/issues/764) Add plugin profiles to enable multiple configurations for extractors
- [#1081](https://gitlab.com/meltano/meltano/issues/1081) Add ability to delete data pipelines
- [#1217](https://gitlab.com/meltano/meltano/issues/1217) Add "Test Connection" button to validate connection settings prior to ELT runs
- [#1236](https://gitlab.com/meltano/meltano/issues/1236) Add contextual Analyze CTAs in the Job Log UI
- [#1271](https://gitlab.com/meltano/meltano/issues/1271) Add labels in discovery.yml for easy brand definition

### Changes

- [#1323](https://gitlab.com/meltano/meltano/issues/1323) Add CTA to send users to Typeform to provide info for setting up a hosted dashboard

- [#1323](https://gitlab.com/meltano/meltano/issues/1323) Add CTA to send users to Typeform to provide info for setting up a hosted dashboard
- [#1271](https://gitlab.com/meltano/meltano/issues/1271) Improve messaging on tap and target settings modals
- [#1226](https://gitlab.com/meltano/meltano/issues/1226) Update Pipelines main navigation link to show all data pipeline schedules if that step has been reached
- [#1323](https://gitlab.com/meltano/meltano/issues/1323) Add CTA to send users to Typeform to provide info for setting up a hosted dashboard
- [#1271](https://gitlab.com/meltano/meltano/issues/1271) Improve messaging on tap and target settings modals
- [#1246](https://gitlab.com/meltano/meltano/issues/1246) Update the [Salesforce API + Postgres](https://www.meltano.com/tutorials/salesforce-and-postgres.html) Tutorial to use Meltano UI for setting up the Extractor and Loader, running the ELT pipeline and analyzing the results.

- [#1225](https://gitlab.com/meltano/meltano/issues/1225) Update dbt docs link to be conditional so the user doesn't experience 404s

## 1.7.2 - (2019-11-26)

---

### Fixes

- [#1318](https://gitlab.com/meltano/meltano/merge_requests/1318/) Pin dbt version to `v0.14.4` to address Meltano Transformation failing when using dbt `v0.15.0`

## 1.7.1 - (2019-11-25)

---

### Fixes

- [#1184](https://gitlab.com/meltano/meltano/merge_requests/1184/) Fix `contextualModels` implementation for contextual CTAs in Job Log modal

## 1.7.0 - (2019-11-25)

---

### New

- [#1236](https://gitlab.com/meltano/meltano/issues/1236) Add contextual Analyze CTAs in the Job Log UI

### Fixes

- [#1298](https://gitlab.com/meltano/meltano/issues/1298) Let default entity selection be configured in discovery.yml under `select`
- [#1298](https://gitlab.com/meltano/meltano/issues/1298) Define default entity selection for tap-salesforce
- [#1304](https://gitlab.com/meltano/meltano/issues/1304) Fix Meltano subprocess fetching large catalogs (e.g. for Salesforce) getting stuck do to the subprocess' stderr buffer filling and the process getting deadlocked.

## 1.6.0 - (2019-11-18)

---

### New

- [#1235](https://gitlab.com/meltano/meltano/issues/1235) Add help link button in the app
- [#1285](https://gitlab.com/meltano/meltano/issues/1285) Add link to YouTube guidelines for release instructions
- [#1277](https://gitlab.com/meltano/meltano/issues/1277) Move sections that don't apply to outside contributors from Contributing and Roadmap docs to Handbook: Release Process, Release Schedule, Demo Day, Speedruns, DigitalOcean Marketplace

### Changes

- [#1257](https://gitlab.com/meltano/meltano/issues/1257) Prevent modified logo file upon each build
- [#1289](https://gitlab.com/meltano/meltano/issues/1289) Dismiss all modals when using the escape key
- [#1282](https://gitlab.com/meltano/meltano/issues/1282) Remove Entity Selection from the UI (still available in CLI) and default to "All" entities for a given data source
- [#1303](https://gitlab.com/meltano/meltano/issues/1303) Update the configuration options for the Salesforce Extractor to only include relevant properties. Remove properties like the client_id that were not used for username/password authentication.
- [#1308](https://gitlab.com/meltano/meltano/issues/1308) Update the configuration options for the Marketo Extractor to use a Start Date instead of a Start Time.

### Fixes

- [#1297](https://gitlab.com/meltano/meltano/issues/1297) Get actual latest ELT job log by sorting matches by creation time with nanosecond resolution
- [#1297](https://gitlab.com/meltano/meltano/issues/1297) Fix pipeline failure caused by jobs that require true concurrency being executed on CI runners that don't

## 1.5.0 - (2019-11-11)

---

### New

- [#1222](https://gitlab.com/meltano/meltano/issues/1222) Include static application security testing (SAST) in the pipeline
- [#1164](https://gitlab.com/meltano/meltano/issues/1164) Add "transform limitations" message to Transform UI
- [#1272](https://gitlab.com/meltano/meltano/issues/1272) Add Vuepress plugin to generate a sitemap on website build
- [meltano-marketing#89](https://gitlab.com/meltano/meltano-marketing/issues/89) Adds basic title and meta descriptions to all public-facing website & documentation pages.

### Changes

- [#1239](https://gitlab.com/meltano/meltano/issues/1239) Update header buttons layout on small viewports
- [#1019](https://gitlab.com/meltano/meltano/issues/1019) Automatically update package.json file versions
- [#1253](https://gitlab.com/meltano/meltano/issues/1253) Do not allow `meltano` command invocation without any argument
- [#1192](https://gitlab.com/meltano/meltano/issues/1192) Improve helper notes associated with each Extract, Load, and Transform step to better communicate the purpose of each
- [#1201](https://gitlab.com/meltano/meltano/issues/1201) Improved "Auto Advance" messaging regarding Entity Selection. We also doubled the default toast time to improve likelihood of reading feedback.
- [#1191](https://gitlab.com/meltano/meltano/issues/1191) update Google Analytics extractor documentation to explain how to set up the Google Analytics API, and remove duplicate instructions from the [Google Analytics API + Postgres tutorial](http://meltano.com/tutorials/google-analytics-with-postgres.html#prerequisites)
- [#1199](https://gitlab.com/meltano/meltano/issues/1199) Add example and sample CSV files to the CSV extractor documentation
- [#1247](https://gitlab.com/meltano/meltano/issues/1247) Update the [Loading CSV Files to a Postgres Database](https://www.meltano.com/tutorials/csv-with-postgres.html) Tutorial to use Meltano UI for setting up the Extractor and Loader, running the ELT pipeline and analyzing the results. Also provide all the files used in the tutorial (transformations, models, etc) as downloadable files.
- [#1279] Revise ["Roadmap" section](https://meltano.com/docs/roadmap.html) of the docs with clarified persona, mission, vision, and re-order content
- [#1134](https://gitlab.com/meltano/meltano/issues/1134) Update the [GitLab API + Postgres](https://www.meltano.com/tutorials/gitlab-and-postgres.html). Include video walk-through and update the end to end flow to only use Meltano UI.
- [#95](https://gitlab.com/meltano/meltano-marketing/issues/95) Update the DigitalOcean CTA to go to the public directory page for the Meltano droplet
- [#1270](https://gitlab.com/meltano/meltano/issues/1270) Main navigation "Pipeline" to "Pipelines" to reinforce multiple vs. singular (conflicts a bit with the verb approach of the other navigation items but we think it's worth it for now)
- [#1240](https://gitlab.com/meltano/meltano/issues/1240) Provide clarity around how Airflow can be used directly in documentation and UI
- [#1263](https://gitlab.com/meltano/meltano/issues/1263) Document lack of Windows support and suggest WSL, Docker

### Fixes

- [#1259](https://gitlab.com/meltano/meltano/issues/1259) Fix `meltano elt` not properly logging errors happening in the ELT process
- [#1183](https://gitlab.com/meltano/meltano/issues/1183) Fix a race condition causing the `meltano.yml` to be empty in some occurence
- [#1258](https://gitlab.com/meltano/meltano/issues/1258) Fix format of custom extractor's capabilities in meltano.yml
- [#1215](https://gitlab.com/meltano/meltano/issues/1215) Fix intercom documentation footer overlap issue.
- [#1215](https://gitlab.com/meltano/meltano/issues/1215) Fix YouTube iframes to be responsive (resolves unwanted side-effect of horizontal scrollbar at mobile/tablet media queries)

## 1.4.0 - (2019-11-04)

---

### New

- [#1208](https://gitlab.com/meltano/meltano/issues/1208) Add description to `Plugin` definition and updated `discovery.yml` and UI to consume it
- [#1195](https://gitlab.com/meltano/meltano/issues/1195) Add temporary message in configuration communicating their global nature until "Profiles" are implemented
- [#1245](https://gitlab.com/meltano/meltano/issues/1245) Add detailed information on the documentation about events tracked by Meltano when Anonymous Usage Data tracking is enabled.
- [#1228](https://gitlab.com/meltano/meltano/issues/1228) Add preselections of the first column and aggregate of base table to initialize Analyze with data by default.

### Changes

- [#1244](https://gitlab.com/meltano/meltano/issues/1244) Add instructions on how to deactivate a virtual environment
- [#1082](https://gitlab.com/meltano/meltano/issues/1082) Meltano will now enable automatically DAGs created in Airflow
- [#1231](https://gitlab.com/meltano/meltano/issues/1231) Update CLI output during project initialization
- [#1126](https://gitlab.com/meltano/meltano/issues/1126) Minor UI updates to improve clarity around Schedule step and Manual vs Orchestrated runs
- [#1210](https://gitlab.com/meltano/meltano/issues/1210) Improved SQLite loader configuration context (name and description)
- [#1185](https://gitlab.com/meltano/meltano/issues/1185) Remove majority of unimplemented placeholder UI buttons
- [#1166](https://gitlab.com/meltano/meltano/issues/1166) Clarify in documentation that plugin configuration is stored in the `.meltano` directory, which is in `.gitignore`.
- [#1200](https://gitlab.com/meltano/meltano/issues/1200) Link to new Getting Help documentation section instead of issue tracker where appropriate

- [#1227](https://gitlab.com/meltano/meltano/issues/1227) Update Notebook `MainNav` link to jump to our Jupyter Notebook docs

### Fixes

- [#1075](https://gitlab.com/meltano/meltano/issues/1075) Fix a bug that caused `target-csv` to fail.
- [#1233](https://gitlab.com/meltano/meltano/issues/1233) Fix the Design page failing to load a Design that has timeframes on the base table
- [#1187](https://gitlab.com/meltano/meltano/issues/1187) Updated configuration to support `readonly` kind to prevent unwanted editing
- [#1187](https://gitlab.com/meltano/meltano/issues/1187) Updated configuration to setting resets to prevent unwanted editing
- [#1187](https://gitlab.com/meltano/meltano/issues/1187) Updated configuration to conditionally reset certain settings to prevent unwanted editing
- [#1187](https://gitlab.com/meltano/meltano/issues/1187) Updated configuration to prevent unwanted editing until we handle this properly with role-based access control
- [#1187](https://gitlab.com/meltano/meltano/issues/1187) Updated certain connector configuration settings with a `readonly` flag to prevent unwanted editing in the UI. This is temporary and will be removed when we handle this properly with role-based access control.
- [#1198](https://gitlab.com/meltano/meltano/issues/1198) Fix "More Info." link in configuration to properly open a new tab via `target="_blank"`

- [#1229](https://gitlab.com/meltano/meltano/issues/1229) Improve extractor schema autodiscovery error messages and don't attempt autodiscovery when it is known to not be supported, like in the case of tap-gitlab
- [#1207](https://gitlab.com/meltano/meltano/issues/1207) Updated all screenshots in Getting Started Guide to reflect the most current UI

## 1.3.0 - (2019-10-28)

---

### New

- [#991](https://gitlab.com/meltano/meltano/issues/991) Add e2e tests for simple sqlite-carbon workflow
- [#1103](https://gitlab.com/meltano/meltano/issues/1103) Add Intercom to Meltano.com to interact with our users in real-time
- [#1130](https://gitlab.com/meltano/meltano/issues/1130) Add Tutorial for extracting data from Google Analytics and loading the extracted data to Postgres
- [#1168](https://gitlab.com/meltano/meltano/issues/1168) Speedrun video added to home page and new release issue template
- [#1182](https://gitlab.com/meltano/meltano/issues/1182) Add `null`able date inputs so optional dates aren't incorrectly required in validation
- [#1169](https://gitlab.com/meltano/meltano/issues/1169) Meltano now generates the dbt documentation automatically

### Changes

- [!1061](https://gitlab.com/meltano/meltano/merge_requests/1061) Update the Getting Started Guide and the Meltano.com documentation with the new UI and information about job logging and how to find the most recent run log of a pipeline.
- [#1213](https://gitlab.com/meltano/meltano/issues/1213) Add VuePress use and benefits to documentation
- [#922](https://gitlab.com/meltano/meltano/issues/922) Document the importance of transformations and how to get started
- [#1167](https://gitlab.com/meltano/meltano/issues/1167) Iterate on docs to improve readability and content updates

### Fixes

- [#1173](https://gitlab.com/meltano/meltano/issues/1173) Fix `sortBy` drag-and-drop bug in Analyze by properly using `tryAutoRun` vs. `runQuery`
- [#1079](https://gitlab.com/meltano/meltano/issues/1079) `meltano elt` will now run in isolation under `.meltano/run/elt`
- [#1204](https://gitlab.com/meltano/meltano/issues/1204) move project creation steps out of the local installation section of the docs and into the Getting Started Guide
- [#782](https://gitlab.com/meltano/meltano/issues/782) Update timeframe label and fix timeframe attributes to properly display in the Result Table

## 1.2.1 - (2019-10-22)

---

### New

- [#1123](https://gitlab.com/meltano/meltano/issues/1123) Add first-class "Submit Issue" CTA to help expedite resolution when a running job fails. Also updated the "Log" CTA in the Pipelines UI to reflect a failed state.

### Fixes

- [#1172](https://gitlab.com/meltano/meltano/issues/1172) Fix analytics issue related to app version

## 1.2.0 - (2019-10-21)

---

### New

- [#1121](https://gitlab.com/meltano/meltano/issues/1121) Add ability to configure listen address of Meltano and Airflow
- [#1022](https://gitlab.com/meltano/meltano/issues/1022) Add "Autorun Query" toggle and persist the user's choice across sessions
- [#1060](https://gitlab.com/meltano/meltano/issues/1060) Auto advance to Job Log from Pipeline Schedule creation
- [#1111](https://gitlab.com/meltano/meltano/issues/1111) Auto advance to Loader installation step when an extractor lacks entity selection

### Changes

- [#1013](https://gitlab.com/meltano/meltano/issues/1013) Toast initialization and analytics initialization cleanup

### Fixes

- [#1050](https://gitlab.com/meltano/meltano/issues/1050) Fix a bug where the Job log would be created before the `transform` are run.
- [#1122](https://gitlab.com/meltano/meltano/issues/1122) `meltano elt` will now properly run when using `target-snowflake`.
- [#1159](https://gitlab.com/meltano/meltano/issues/1159) Minor UI fixes (proper `MainNav` Model icon active color during Analyze route match & "Run" auto query related cleanup) and `...NameFromRoute` refactor renaming cleanup

## 1.1.0 - (2019-10-16)

---

### New

- [#1106](https://gitlab.com/meltano/meltano/issues/1106) Add description metadata to the GitLab extractor's Ultimate License configuration setting
- [#1057](https://gitlab.com/meltano/meltano/issues/1057) Auto advance to Entity Selection when an extractor lacks configuration settings
- [#51](https://gitlab.com/meltano/meltano-marketing/issues/51) Update Google Analytics to track `appVersion`, custom `projectId`, and to properly use the default `clientId`. The CLI also now uses `client_id` to differentiate between a CLI client id (not versioned) and the project id (versioned).
- [#1012](https://gitlab.com/meltano/meltano/issues/1012) Add intelligent autofocus for improved UX in both Extractor and Loader configuration
- [#758](https://gitlab.com/meltano/meltano/issues/758) Update 'meltano permissions' to add --full-refresh command to revoke all privileges prior to granting
- [#1113](https://gitlab.com/meltano/meltano/issues/1113) Update 'meltano permissions' to have the ability to find all schemas matching a partial name such as `snowplow_*`
- [#1114](https://gitlab.com/meltano/meltano/issues/1114) Update 'meltano permissions' to include the OPERATE privilege for Snowflake warehouse

### Changes

- Compress meltano-logo.png
- [#1080](https://gitlab.com/meltano/meltano/issues/1080) Temporarily disable Intercom until userId strategy is determined
- [#1058](https://gitlab.com/meltano/meltano/issues/1058) Updated the selected state of grouped buttons to fill vs. stroke. Updated the docs to reflect the reasoning to ensure consistency in Meltano's UI visual language
- [#1068](https://gitlab.com/meltano/meltano/issues/1068) Replace dogfooding term in docs to speedrun
- [#1101](https://gitlab.com/meltano/meltano/issues/1101) Add new tour video to home page
- [#1101](https://gitlab.com/meltano/meltano/issues/1101) Update design to improve readability and contrast
- [#1115](https://gitlab.com/meltano/meltano/issues/1115) Update 'meltano permissions' to not require an identially named role for a given user

### Fixes

- [#1120](https://gitlab.com/meltano/meltano/issues/1120) Fix a concurrency bug causing `meltano select` to crash.
- [#1086](https://gitlab.com/meltano/meltano/issues/1086) Fix a concurrency issue when the `meltano.yml` file was updated.
- [#1112](https://gitlab.com/meltano/meltano/issues/1112) Fix the "Run" button to improve UX by properly reflecting the running state for auto-running queries
- [#1023](https://gitlab.com/meltano/meltano/issues/1023) Fix last vuex mutation warning with editable `localConfiguration` clone approach

### Breaks

## 1.0.1 - (2019-10-07)

---

### Fixes

- Patch technicality due to PyPI limitation (v1 already existed from a publish mistake seven+ months ago) with needed changelog New/Changes/Fixes section headers

## 1.0.0 - (2019-10-07)

---

### New

- [#1020](https://gitlab.com/meltano/meltano/issues/1020) Update Command Line Tools documentation to reflect a standard format with opportunities for improvement in the future
- [#524](https://gitlab.com/meltano/meltano/issues/524) There is a new Plugins section on the site to contain all ecosystem related libraries (i.e., extractors, loaders, etc.)

### Changes

- [#1087](https://gitlab.com/meltano/meltano/issues/1087) Fix `meltano select` not seeding the database when run as the first command.
- [#1090](https://gitlab.com/meltano/meltano/issues/1090) Update the namespace for all plugins. Also the default schema used will go back to including the `tap_` prefix to avoid conflicts with existing schemas (e.g. a local `gitlab` or `salesforce` schema). This also fixes `tap-csv` and `tap-google-analytics` not properly working after the latest Meltano release.
- [#1047](https://gitlab.com/meltano/meltano-marketing/issues/1047) Fix a bug where some configuration values were not redacted

### Fixes

### Breaks

- [#1085](https://gitlab.com/meltano/meltano/issues/1085) Fix Analyze model dropdown to properly reflect installed `models`
- [#1089](https://gitlab.com/meltano/meltano/issues/1089) Properly re-initialize the Analyze page after a new analysis is selected during an existing analysis (this issue surfaced due to the recent Analyze dropdown CTAs addition which enables an analysis change during an existing one)
- [#1092](https://gitlab.com/meltano/meltano/issues/1092) Fix async condition so the design store's `defaultState` is properly applied before loading a new design via `initializeDesign`

## 0.44.1 - (2019-10-03)

---

### New

- [#51](https://gitlab.com/meltano/meltano-marketing/issues/51) Add Google Analytics tracking acknowledgment in the UI
- [#926](https://gitlab.com/meltano/meltano/issues/926) Add step-by-step intructions for using the DigitalOcean one-click installer
- [#1076](https://gitlab.com/meltano/meltano/issues/1076) Enable Log button in pipelines UI after route change or hard refresh if a matching log exists
- [#1067](https://gitlab.com/meltano/meltano/issues/1067) Add Model landing page and update Analyze main navigation to a dropdown displaying the various analysis CTAs associated with each model
- [#1080](https://gitlab.com/meltano/meltano/issues/1080) Add live chat support on Meltano.com website using Intercom.io

### Changes

- [#1069](https://gitlab.com/meltano/meltano/issues/1069) Meltano will now use the schedule's name to run incremental jobs
- [#926](https://gitlab.com/meltano/meltano/issues/926) Move manual DigitalOcean Droplet configuration instructions to advanced tutorials
- Collapse Installation docs into a single section

### Fixes

- [#1071](https://gitlab.com/meltano/meltano/issues/1071) Fix `rehydratePollers` so the UI reflects running jobs after a hard refresh or route change (this surfaced from the recent [!963](https://gitlab.com/meltano/meltano/merge_requests/963) change)
- [#1075](https://gitlab.com/meltano/meltano/issues/1075) Fix an issue where `meltano elt` would fail when a previous job was found

## 0.44.0 - (2019-09-30)

---

### New

- [#950](https://gitlab.com/meltano/meltano/issues/950) Removed the Analyze connection configuration: Meltano will now infer connections out of each loader configuration.
- [#1002](https://gitlab.com/meltano/meltano/issues/1002) Analyze UI now displays the Topic's (analysis model's) description text if applicable
- [#1032](https://gitlab.com/meltano/meltano/issues/1032) Add 'Model' and 'Notebook' to main navigation to communicate that Meltano plans to empower users with modeling and notebooking functionality
- [#949](https://gitlab.com/meltano/meltano/issues/949) Add "Log" button and dedicated sub-UI for tracking an ELT run's status more granularly

- [#932](https://gitlab.com/meltano/meltano/issues/932) Meltano can now be upgraded from the UI directly.

### Changes

- [#1045](https://gitlab.com/meltano/meltano/issues/1045) Make it clear that 'meltano add' is not hanging while installing plugins
- [#1000](https://gitlab.com/meltano/meltano/issues/1000) Update Getting Started guide with updated screenshots and content
- [#854](https://gitlab.com/meltano/meltano/issues/854) Charts now use pretty labels rather than the ID
- [#1011](https://gitlab.com/meltano/meltano/issues/1011) Removed "Catch-up Date" in favor of default "Start Date" of extractor
- [#578](https://gitlab.com/meltano/meltano/issues/578) Remove support for `tap-zuora`.
- [#1002](https://gitlab.com/meltano/meltano/issues/1002) Update `discovery.yml` with explicit `kind: password` metadata (we infer and set input types of `password` as a safeguard, but the explicit setting is preferred)
- [#1049](https://gitlab.com/meltano/meltano/issues/1049) Change default `target-sqlite` database name to `warehouse` to not conflict with system database
- [#949](https://gitlab.com/meltano/meltano/issues/949) Update the way Meltano handles logs for ELT runs: Every elt run is logged in `.meltano/run/logs/{job_id}/elt_{timestamp}.log`. That allows Meltano to keep logs for multiple, or even concurrent, elt runs with the same `job_id`.
- [#949](https://gitlab.com/meltano/meltano/issues/949) Update "Create Pipeline" redirect logic based on the previous route being 'transforms' (this is a UX win setting up the user with the sub-UI for the next logical step vs. requiring a manual "Create" click)
- [#1051](https://gitlab.com/meltano/meltano/issues/1051) Automatically set SQLALCHEMY_DATABASE_URI config to system database URI

### Fixes

- [#1004](https://gitlab.com/meltano/meltano/issues/1004) Fix error when deselecting last attribute in Analyze
- [#1048](https://gitlab.com/meltano/meltano/issues/1048) Fix various actions that should have been mutations and did minor code convention cleanup
- [#1063](https://gitlab.com/meltano/meltano/issues/1063) Fix the "Explore" button link in Dashboards to properly account for the `namespace`

### Breaks

- [#1051](https://gitlab.com/meltano/meltano/issues/1051) Remove MELTANO_BACKEND e.a. in favor of --uri CLI option and MELTANO_DATABASE_URI env var
- [#1052](https://gitlab.com/meltano/meltano/issues/1052) Move system database into `.meltano` directory to indicate it is owned by the app and not supposed to be messed with directly by users

## 0.43.0 - (2019-09-23)

---

### New

- [#1014](https://gitlab.com/meltano/meltano/issues/1014) Meltano now logs all output from each `meltano elt` run in a log file that uses the unique job*id of the run. It can be found in `.meltano/run/logs/elt*{job_id}.log`.
- [#1014](https://gitlab.com/meltano/meltano/issues/1014) Meltano now logs all output from each `meltano elt` run in a log file that uses the unique job*id of the run. It can be found in `.meltano/run/logs/elt*{job_id}.log`.
- [#1014](https://gitlab.com/meltano/meltano/issues/1014) Meltano now logs all output from each `meltano elt` run in a log file that uses the unique `job_id` of the run. It can be found in `.meltano/run/logs/elt*{job_id}.log`.
- [#955](https://gitlab.com/meltano/meltano/issues/955) Establish baseline for demo day and how they should be run

### Changes

- [#891](https://gitlab.com/meltano/meltano/issues/891) Contributors can run webapp from root directory

### Fixes

- [#1005](https://gitlab.com/meltano/meltano/issues/1005) Fix installed plugins endpoints listing identically named plugins of different types under wrong type

## 0.42.1 - (2019-09-19)

---

### Changes

- [#987](https://gitlab.com/meltano/meltano/issues/987) Update routing to match labels (verbs vs. nouns) in effort to subtly reinforce action taking vs. solely "thing" management
- [#960](https://gitlab.com/meltano/meltano/issues/960) Improve UX by instantly displaying extractor and loader configuration UIs based on "Install" or "Configure" interaction as opposed to the prior delay (side effect of async `addPlugin`)
- [#996](https://gitlab.com/meltano/meltano/issues/996) Update conditional UI analytics stats tracking at runtime vs. build-time by sourcing state from the same backend `send_anonymous_usage_stats` flag

### Fixes

- [#992](https://gitlab.com/meltano/meltano/issues/992) Fix missing GA scripts
- [#989](https://gitlab.com/meltano/meltano/issues/989) Fix UI/UX documentation regarding recent removal of `view-header`
- [#994](https://gitlab.com/meltano/meltano/issues/994) Fix stale Pipelines Count in main navigation Pipeline badge
- [#999](https://gitlab.com/meltano/meltano/issues/999) Update yarn dependencies to resolve peer dependency warning
- [#1008](https://gitlab.com/meltano/meltano/issues/1008) Fix error on "Create Pipeline Schedule" modal when no plugins have been installed
- [#1015](https://gitlab.com/meltano/meltano/issues/1008) Support SQLite database name with and without '.db' extension
- [#1007](https://gitlab.com/meltano/meltano/issues/1007) Fix pipeline with failed job not being regarded as having completed
- [#998](https://gitlab.com/meltano/meltano/issues/998) Update Analyze UI with conditional loading indicator to prevent query generation prior to connection dialects being loaded (this solution is still useful for when inference supercedes our current manual dialect selection solution)
- [#1009](https://gitlab.com/meltano/meltano/issues/1009) Fix default ConnectorSettings validation to account for `false` (unchecked) checkbox values

### Breaks

## 0.42.0 - (2019-09-16)

---

### New

- [#976](https://gitlab.com/meltano/meltano/issues/976) Route changes will update page title in the web app

### Changes

- [Marketing #48](https://gitlab.com/meltano/meltano-marketing/issues/48) Update newsletter subscription links to redirect to our new newsletter [hosted by Substack](https://meltano.substack.com)

### Fixes

- [#965](https://gitlab.com/meltano/meltano/issues/965) Fix a regression that prevented the Meltano UI to reach the Meltano API when using an external hostname.
- [#986](https://gitlab.com/meltano/meltano/issues/986) Fix an issue where the Orchestration page would not show Airflow even when it was installed.
- [#969](https://gitlab.com/meltano/meltano/issues/969) Fix an issue where the Meltano Analyze connection would not respect the `port` configuration.
- [#964](https://gitlab.com/meltano/meltano/issues/964) Fix copy button overlap issue with top navigation
- [#970](https://gitlab.com/meltano/meltano/issues/970) Fix Meltano's m5o parser and compiler to properly namespace and isolate the definitions of different custom and packaged Topics.

## 0.41.0 - (2019-09-09)

---

### New

- [#980](https://gitlab.com/meltano/meltano/issues/980) Add Cypress for e2e testing pipeline
- [#579](https://gitlab.com/meltano/meltano/issues/579) Add `meltano schedule list` to show a project's schedules
- [#942](https://gitlab.com/meltano/meltano/issues/942) Add progress bars on various routes to improve UX feedback
- [#779](https://gitlab.com/meltano/meltano/issues/779) Add various UI polish details regarding iconography use, preloading feedback, breadcrumbs, container styling, navigation, and sub-navigation

### Changes

- [#906](https://gitlab.com/meltano/meltano/issues/906) `meltano ui` will now run in `production` per default

- [#942](https://gitlab.com/meltano/meltano/issues/942) Update Analyze Connections UI to match configuration-as-modal pattern for UX consistency regarding configuration
- [#779](https://gitlab.com/meltano/meltano/issues/779) Update all "This feature is queued..." temporary UI buttons to link to the Meltano repo issues page with a contextual search term

## 0.40.0 - (2019-09-04)

---

### New

- [#927](https://gitlab.com/meltano/meltano/issues/927) Document how to manually set up a Meltano Droplet on DigitalOcean

- [#916](https://gitlab.com/meltano/meltano/issues/916) Add Transform step as first-class and adjacent step to Extract and Load
- [#916](https://gitlab.com/meltano/meltano/issues/916) Improve Create Pipeline Schedule default selection UX by leveraging "ELT recents" concept
- [#936](https://gitlab.com/meltano/meltano/issues/936) Add "Refresh Airflow" button in Orchestrate to bypass route change or full-page refresh when iframe doesn't initially inflate as expected (this will likely be automated once the root cause is determined)
- [#899](https://gitlab.com/meltano/meltano/issues/899) Add deep linking improvements to reports and dashboards to better facilitate sharing
- [#899](https://gitlab.com/meltano/meltano/issues/899) Add "Edit" and "Explore" buttons to each report instance displayed in a dashboard to enable editing said report and exploring a fresh and unselected analysis of the same model and design
- [!546](https://gitlab.com/meltano/meltano/merge_requests/546) Add new Advanced Tutorial on how to Load CSV files to Postgres

### Changes

- [#909](https://gitlab.com/meltano/meltano/issues/909) Default names will be generated for Reports and Dashboards
- [#892](https://gitlab.com/meltano/meltano/issues/892) Improve experience for parsing Snowflake URL for ID by showing processing step
- [#935](https://gitlab.com/meltano/meltano/issues/935) Update Entity Selection to be nested in the Extract step so each ELT step is consecutive
- [#886](https://gitlab.com/meltano/meltano/issues/886) Add validation for grouping settings as the next iteration of improved form validation for generated connector settings

### Fixes

- [#931](https://gitlab.com/meltano/meltano/issues/931) Fix Analyze Connections identifier mismatch resulting from recent linting refactor
- [#919](https://gitlab.com/meltano/meltano/issues/919) Fix Airflow iframe automatic UI refresh
- [#937](https://gitlab.com/meltano/meltano/issues/937) Fix Chart.vue prop type error

## 0.39.0 - (2019-08-26)

---

### New

- [#838](https://gitlab.com/meltano/meltano/issues/838) Add indicator for speed run plugins
- [#870](https://gitlab.com/meltano/meltano/issues/870) Add global footer component in docs
- [#871](https://gitlab.com/meltano/meltano/issues/871) Add contributing link in footer of docs
- [#908](https://gitlab.com/meltano/meltano/issues/908) Add auto installation for Airflow Orchestrator for improved UX
- [#912](https://gitlab.com/meltano/meltano/issues/912) Auto run the ELT of a saved Pipeline Schedule by default
- [#907](https://gitlab.com/meltano/meltano/issues/907) Add auto select of "All" for Entities Selection step and removed the performance warning (a future iteration will address the "Recommended" implementation and the display of a resulting performance warning when "All" is selected and "Recommended" ignored)
- [#799](https://gitlab.com/meltano/meltano/issues/799) Standardized code conventions on the frontend and updated related documentation (issues related to further linting enforcement will soon follow)

### Changes

- [#838](https://gitlab.com/meltano/meltano/issues/838) Speed run plugins prioritized to top of the list
- [#896](https://gitlab.com/meltano/meltano/issues/896) Add documentation for how to do patch releases
- [#910](https://gitlab.com/meltano/meltano/issues/910) Update linting rules to enforce better standards for the frontend code base
- [#885](https://gitlab.com/meltano/meltano/issues/885) Add docs for all extractors and loaders
- [#885](https://gitlab.com/meltano/meltano/issues/885) All plugin modal cards show docs text if they have docs
- [#733](https://gitlab.com/meltano/meltano/issues/733) Improve error feedback to be more specific when plugin installation errors occur

### Fixes

- [#923](https://gitlab.com/meltano/meltano/issues/923) Fix contributing release docs merge conflict issue

## 0.38.0 - (2019-08-21)

---

### New

- [#746](https://gitlab.com/meltano/meltano/issues/746) Add CTA to specific dashboard in "Add to Dashboard" sub-UI
- [#746](https://gitlab.com/meltano/meltano/issues/746) Add toast feedback on success, update, or error for schedules, reports, and dashboards
- [#814](https://gitlab.com/meltano/meltano/issues/814) Install Airflow via the Orchestration UI (we may do this in the background automatically in the future)

### Changes

- [#901](https://gitlab.com/meltano/meltano/issues/901) Update entities plugins to be alphabetically sorted for consistency with extractors ordering

### Fixes

- [#746](https://gitlab.com/meltano/meltano/issues/746) Prevent duplicate schedule, report, and dashboard creation if there is an existing item
- [#976](https://gitlab.com/meltano/meltano/issues/900) Fix fallback v976e Route changes will update page title in the web appfor Iso8601 dates/times
- [#903](https://gitlab.com/meltano/meltano/issues/903) Fix columns display issue for the base table in Analyze

### Breaks

## 0.37.2 - (2019-08-19)

---

### Fixes

- [#894](https://gitlab.com/meltano/meltano/issues/894) Fix issue with static asset paths

## 0.37.1 - (2019-08-19)

---

### Fixes

- [#894](https://gitlab.com/meltano/meltano/issues/894) Fix build issues with new Vue CLI 3 build process

## 0.37.0 - (2019-08-19)

---

### New

- [#763](https://gitlab.com/meltano/meltano/issues/763) Add inference to auto install related plugins after a user installs a specific extractor
- [#867](https://gitlab.com/meltano/meltano/issues/867) Add fallback values (if they aren't set in the `discovery.yml`) for `start date`, `start time`, and `end date` for all connectors so the user has potentially one less interaction to make per connector configuration

### Changes

- [#342](https://gitlab.com/meltano/meltano/issues/342) Swap UI app directory "webapp" and upgrade to Vue CLI 3
- [#882](https://gitlab.com/meltano/meltano/issues/882) Update navigation and subnavigation labels to verbs vs. nouns to inspire action and productivity when using the UI
- [#700](https://gitlab.com/meltano/meltano/issues/700) Update documentation to remove "\$" and trim spaces to make CLI command copy/paste easier
- [#878](https://gitlab.com/meltano/meltano/issues/878) Write a [tutorial to help users get started with PostgreSQL](http://www.meltano.com/docs/loaders.html#postgresql-database)
- [#883](https://gitlab.com/meltano/meltano/issues/883) Break Extractors and Loaders sections out in the docs
- [#889](https://gitlab.com/meltano/meltano/issues/889) Allow for githooks to lint on commit
- [#835](https://gitlab.com/meltano/meltano/issues/835) Pipeline name in Schedule creation will have an automatic default

### Fixes

- [#872](https://gitlab.com/meltano/meltano/issues/872) Updated `tap-marketo` and `tap-stripe` to leverage password input type while also improving the input type password fallback
- [#882](https://gitlab.com/meltano/meltano/issues/882) Fix recent minor regression regarding `Dashboard` routing
- [#858](https://gitlab.com/meltano/meltano/issues/858) Fix `job_state` bug so that ELT run status polling can properly resume as expected
- [#890](https://gitlab.com/meltano/meltano/issues/890) Fix implementation of default configuration setting to use less code

## 0.36.0 - (2019-08-12)

---

### New

- [#793](https://gitlab.com/meltano/meltano/issues/793) Add introduction module to Connector Settings to allow for helper text as far as signup and documentation links
- [#796](https://gitlab.com/meltano/meltano/issues/796) Add dropdown option to Connector Settings to allow for more defined UI interactions
- [#802](https://gitlab.com/meltano/meltano/issues/802) Add support for Query Filters over columns that are not selected
- [#855](https://gitlab.com/meltano/meltano/issues/855) Add empty state to Dashboards and cleaned up styling for consistency with Analyze's layout
- [#856](https://gitlab.com/meltano/meltano/issues/856) Add contextual information to the Analyze Connection UI to aid user understanding
- [#800](https://gitlab.com/meltano/meltano/issues/800) Add save success feedback for connectors, entities, and connections
- [#817](https://gitlab.com/meltano/meltano/issues/817) Add [Meltano explainer video](https://www.youtube.com/watch?v=2Glsf89WQ5w) to the front page of Meltano.com

### Changes

- [#794](https://gitlab.com/meltano/meltano/issues/794) Update Snowflake fields to have descriptions and utilize tooltip UI
- [#853](https://gitlab.com/meltano/meltano/issues/853) Improve UX for multi-attribute ordering (wider sub-UI for easier reading, clear drop target, and clearer drag animation for reenforcing sorting interaction)
- [#735](https://gitlab.com/meltano/meltano/issues/735) Update Entities UI to only display entity selection "Configure" CTAs for installed (vs. previously all) extractors
- [#548](https://gitlab.com/meltano/meltano/issues/548) Update Meltano mission, vision and path to v1 on [roadmap page](https://meltano.com/docs/roadmap.html) of Meltano.com
- [#824](https://gitlab.com/meltano/meltano/issues/824) Update `meltano select` to use the unique `tap_stream_id` instead of the `stream` property for filtering streams. This adds support for taps with multiple streams with the same name, like, for example, the ones produced by `tap-postgres` when tables with the same name are defined in different schemas.
- [#842](https://gitlab.com/meltano/meltano/issues/842) Collapse Deployment section in the docs to be under [Installation](https://meltano.com/docs/installation.html)

### Fixes

- [#855](https://gitlab.com/meltano/meltano/issues/855) Fix bug that duplicated a dashboard's `reportIds` that also prevented immediate UI feedback when reports were toggled (added or removed) from a dashboard via Analyze's "Add to Dashboard" dropdown
- [#851](https://gitlab.com/meltano/meltano/issues/851) Fix report saving and loading to work with filters and sortBy ordering
- [#852](https://gitlab.com/meltano/meltano/issues/852) Update Scheduling UI to have "Run" button at all times vs conditionally to empower users to run one-off ELT pipelines even if Airflow is installed
- [#852](https://gitlab.com/meltano/meltano/issues/852) Update Scheduling UI "Interval" column with CTA to install Airflow while communicating why via tooltip
- [#852](https://gitlab.com/meltano/meltano/issues/852) Fix initial Orchestration page hydration to properly reflect Airflow installation status
- [#831](https://gitlab.com/meltano/meltano/issues/831) Update `meltano elt` to exit with 1 and report dbt's exit code on an error message when dbt exits with a non-zero code.
- [#857](https://gitlab.com/meltano/meltano/issues/857) Update PluginDiscoveryService to use the cached `discovery.yml` when Meltano can not connect to `meltano.com` while trying to fetch a fresh version of the discovery file.
- [#850](https://gitlab.com/meltano/meltano/issues/850) Fix entities response so entities display as expected (as assumed this simple fix was due to our recent interceptor upgrade)
- [#800](https://gitlab.com/meltano/meltano/issues/800) Fix connector and connection settings to display saved settings by default while falling back and setting defaults if applicable

## 0.35.0 - (2019-08-05)

---

### New

- [!781](https://gitlab.com/meltano/meltano/merge_requests/781) Add new Advanced Tutorial on how to use tap-postgres with Meltano
- [#784](https://gitlab.com/meltano/meltano/issues/784) Add multiple attribute ordering with drag and drop ordering in the UI

### Changes

- [#784](https://gitlab.com/meltano/meltano/issues/784) As part of multiple attribute sorting and keeping the attributes and results sub-UIs in sync, we know autorun queries based on user interaction after the initial explicit "Run" button interaction

## 0.34.2 - (2019-08-01)

---

### Fixes

- [#821](https://gitlab.com/meltano/meltano/issues/821) Fix `meltano config` not properly loading settings defined in the `meltano.yml`
- [#841](https://gitlab.com/meltano/meltano/issues/841) Fix a problem when model names were mangled by the API

## 0.34.1 - (2019-07-30)

---

### Fixes

- [#834](https://gitlab.com/meltano/meltano/issues/834) Fixed a problem with the Meltano UI not having the proper API URL set

## 0.34.0 - (2019-07-29)

---

### New

- [#757](https://gitlab.com/meltano/meltano/issues/757) Update 'meltano permissions' to add support for GRANT ALL and FUTURE GRANTS on tables in schemas
- [#760](https://gitlab.com/meltano/meltano/issues/760) Update 'meltano permissions' to add support for granting permissions on VIEWs
- [#812](https://gitlab.com/meltano/meltano/issues/812) `meltano ui` will now stop stale Airflow workers when starting
- [#762](https://gitlab.com/meltano/meltano/issues/762) Added run ELT via the UI (manages multiple and simultaneous runs)
- [#232](https://gitlab.com/meltano/meltano/issues/232) Meltano now bundles Alembic migrations to support graceful database upgrades

### Changes

- [#828](https://gitlab.com/meltano/meltano/issues/828) Docker installation instructions have been dogfooded, clarified, and moved to Installation section
- [#944](https://gitlab.com/meltano/meltano/issues/944) Update the Transform step's default to "Skip"

### Fixes

- [#807](https://gitlab.com/meltano/meltano/issues/807) Fix filter input validation when editing saved filters
- [#822](https://gitlab.com/meltano/meltano/issues/822) Fix pipeline schedule naming via slugify to align with Airflow DAG naming requirements
- [#820](https://gitlab.com/meltano/meltano/issues/820) Fix `meltano select` not properly connecting to the system database
- [#787](https://gitlab.com/meltano/meltano/issues/787) Fix results sorting to support join tables
- [#832](https://gitlab.com/meltano/meltano/issues/832) Fix schedule creation endpoint to return properly typed response (this became an issue as a result of our recent case conversion interceptor)
- [#819](https://gitlab.com/meltano/meltano/issues/819) Running the Meltano UI using gunicorn will properly update the system database

## 0.33.0 - (2019-07-22)

---

### New

- [#788](https://gitlab.com/meltano/meltano/issues/788) Reydrate filters in Analyze UI after loading a saved report containing filters

### Changes

- [#804](https://gitlab.com/meltano/meltano/issues/804) Connection set in the Design view are now persistent by Design

### Fixes

- [#788](https://gitlab.com/meltano/meltano/issues/788) Properly reset the default state of the Analyze UI so stale results aren't displayed during a new analysis
- [!806](https://gitlab.com/meltano/meltano/merge_requests/806) Fix filters editing to prevent input for `is_null` and `is_not_null` while also ensuring edits to existing filter expressions types adhere to the same preventitive input.
- [#582](https://gitlab.com/meltano/meltano/issues/582) Remove the `export` statements in the default `.env` initialized by `meltano init`.
- [#816](https://gitlab.com/meltano/meltano/issues/816) Fix `meltano install` failing when connections where specified in the `meltano.yml`
- [#786](https://gitlab.com/meltano/meltano/issues/786) Fixed an issue with the SQL engine would mixup table names with join/design names
- [#808](https://gitlab.com/meltano/meltano/issues/808) Fix filter aggregate value with enforced number via `getQueryPayloadFromDesign()` as `input type="number"` only informs input keyboards on mobile, and does not enforce the Number type as expected

## 0.32.2 - (2019-07-16)

---

### New

- [#759](https://gitlab.com/meltano/meltano/issues/759) Added filtering functionality to the Analyze UI while additionally cleaning it up from a UI/UX lens

## 0.32.1 - (2019-07-15)

---

### Fixes

- [#792](https://gitlab.com/meltano/meltano/issues/792) Fix an error when trying to schedule an extractor that didn't expose a `start_date`.

## 0.32.0 - (2019-07-15)

---

### New

- [!718](https://gitlab.com/meltano/meltano/merge_requests/718) Add support for filters (WHERE and HAVING clauses) to MeltanoQuery and Meltano's SQL generation engine
- [#748](https://gitlab.com/meltano/meltano/issues/748) Added the `Connections` plugin to move the Analyze connection settings to the system database
- [#748](https://gitlab.com/meltano/meltano/issues/748) Added the `meltano config` command to manipulate a plugin's configuration

### Fixes

[!726](https://gitlab.com/meltano/meltano/merge_requests/726) Fixed InputDateIso8601's default value to align with HTML's expected empty string default

## 0.31.0 - (2019-07-08)

---

### New

- [#766](https://gitlab.com/meltano/meltano/issues/766) Add Codeowners file so that the "approvers" section on MRs is more useful for contributors
- [#750](https://gitlab.com/meltano/meltano/issues/750) Various UX updates (mostly tooltips) to make the configuration UI for scheduling orchestration easier to understand
- [#739](https://gitlab.com/meltano/meltano/issues/739) Updated `discovery.yml` for better consistency of UI order within each connector's settings (authentication -> contextual -> start/end dates). Improved various settings' `kind`, `label`, and `description`. Added a `documentation` prop to provide a documentation link for involved settings (temp until we have better first class support for more complex setting types)

### Fixes

- [#737](https://gitlab.com/meltano/meltano/issues/737) Fixed UI flash for connector settings when installation is complete but `configSettings` has yet to be set
- [#751](https://gitlab.com/meltano/meltano/issues/751) Fixed the Orchestrations view by properly checking if Airflow is installed so the correct directions display to the user

## 0.30.0 - (2019-07-01)

---

### New

- [#736](https://gitlab.com/meltano/meltano/issues/736) Add "Cancel", "Next", and a message to the entities UI when an extractor doesn't support discovery and thus entity selection
- [#730](https://gitlab.com/meltano/meltano/issues/730) Updated Analyze Models page UI with improved content organization so it is easier to use
- [#710](https://gitlab.com/meltano/meltano/issues/710) Updated connector (extractor and loader) settings with specific control type (text, password, email, boolean, and date) per setting, added form validation, and added an inference by default for password and token fields as a protective measure
- [#719](https://gitlab.com/meltano/meltano/issues/719) Added InputDateIso8601.vue component to standardize date inputs in the UI while ensuring the model data remains in Iso8601 format on the frontend.
- [#643](https://gitlab.com/meltano/meltano/issues/643) Updated `minimallyValidated` computeds so that new users are intentionally funneled through the pipelines ELT setup UI (previously they could skip past required steps)
- [#752](https://gitlab.com/meltano/meltano/issues/752) Fix the schedule having no start_date when the extractor didn't expose a `start_date` setting

### Fixes

- [!703](https://gitlab.com/meltano/meltano/merge_requests/703) Fix `ScheduleService` instantiation due to signature refactor

## 0.29.0 - (2019-06-24)

---

### New

- [#724](https://gitlab.com/meltano/meltano/issues/724) Add the `model-gitlab-ultimate` plugin to Meltano. It includes .m5o files for analyzing data available for Gitlab Ultimate or Gitlab.com Gold accounts (e.g. Epics, Epic Issues, etc) fetched using the Gitlab API. Repository used: https://gitlab.com/meltano/model-gitlab-ultimate
- [#723](https://gitlab.com/meltano/meltano/issues/723) Add proper signage and dedicated sub-navigation area in views/pages. Standardized the view -> sub-view markup relationships for consistent layout. Directory refactoring for improved organization.
- [#612](https://gitlab.com/meltano/meltano/issues/612) Move the plugins' configuration to the database, enabling configuration from the UI

### Changes

- [#636](https://gitlab.com/meltano/meltano/issues/636) Refactored connector logo related logic into a ConnectorLogo component for code cleanliness, reusability, and standardization
- [#728](https://gitlab.com/meltano/meltano/issues/728) Change error notification button link to open the bugs issue template

### Fixes

- [#718](https://gitlab.com/meltano/meltano/issues/718) Fix dynamically disabled transforms always running. Transforms can now be dynamically disabled inside a dbt package and Meltano will respect that. It will also respect you and your time.
- [#684](https://gitlab.com/meltano/meltano/issues/684) Enables WAL on SQLite to handle concurrent processes gracefully
- [#732](https://gitlab.com/meltano/meltano/issues/732) Fix plugin installation progress bar that wasn't updating upon installation completion

## 0.28.0 - (2019-06-17)

---

### New

- [!683](https://gitlab.com/meltano/meltano/issues/683) Add `--start-date` to `meltano schedule` to give the control over the catch up logic to the users
- [#651](https://gitlab.com/meltano/meltano/issues/651) Added model installation in the Analyze UI to bypass an otherwise "back to the CLI step"
- [#676](https://gitlab.com/meltano/meltano/issues/676) Add pipeline schedule UI for viewing and saving pipeline schedules for downstream use by Airflow/Orchestration

### Changes

- [#708](https://gitlab.com/meltano/meltano/issues/708) Enable `tap-gitlab` to run using Gitlab Ultimate and Gitlab.com Gold accounts and extract Epics and Epic Issues.
- [#711](https://gitlab.com/meltano/meltano/issues/711) Add new call to action for submitting an issue on docs site
- [#717](https://gitlab.com/meltano/meltano/issues/717) Enable `dbt-tap-gitlab` to run using Gitlab Ultimate and Gitlab.com Gold accounts and generate transformed tables that depend on Epics and Epic Issues.

### Fixes

- [#716](https://gitlab.com/meltano/meltano/issues/716) Fix entities UI so only installed extractors can edit selections
- [#715](https://gitlab.com/meltano/meltano/issues/715) Remove reimport of Bulma in `/orchestration` route to fix borked styling

## 0.27.0 - (2019-06-10)

---

### New

- [!640](https://gitlab.com/meltano/meltano/merge_requests/640) Google Analytics logo addition for recent tap-google-analytics Extractor addition
- [#671](https://gitlab.com/meltano/meltano/issues/671) Add the `tap-google-analytics` transform to Meltano. It is using the dbt package defined in https://gitlab.com/meltano/dbt-tap-google-analytics
- [#672](https://gitlab.com/meltano/meltano/issues/672) Add the `model-google-analytics` plugin to Meltano. It includes .m5o files for analyzing data fetched from the Google Analytics Reporting API. Repository used: https://gitlab.com/meltano/model-google-analytics
- [#687](https://gitlab.com/meltano/meltano/issues/687) Implemented a killswitch to prevent undefined behaviors when a Meltano project is not compatible with the installed `meltano` version

### Fixes

- [#661](https://gitlab.com/meltano/meltano/issues/661) Fixed empty UI for extractors that lack configuration settings by providing feedback message with actionable next steps
- [#663](https://gitlab.com/meltano/meltano/issues/663) Fixed Airflow error when advancing to Orchestration step after installing and saving a Loader configuration
- [#254](https://gitlab.com/meltano/meltano/issues/254) Fixed `meltano init` not working on terminal with cp1252 encoding
- [#254](https://gitlab.com/meltano/meltano/issues/254) Fixed `meltano add/install` crashing on Windows
- [#664](https://gitlab.com/meltano/meltano/issues/664) Minor CSS fix ensuring Airflow UI height is usable (side-effect of recent reparenting)
- [#679](https://gitlab.com/meltano/meltano/issues/679) Fix an issue with `meltano select` emitting duplicate properties when the property used the `anyOf` type
- [#650](https://gitlab.com/meltano/meltano/issues/650) Add `MELTANO_DISABLE_TRACKING` environment variable to disable all tracking
- [#670](https://gitlab.com/meltano/meltano/issues/670) Update tests to not send tracking events

## 0.26.0 - (2019-06-03)

---

### New

- [#603](https://gitlab.com/meltano/meltano/issues/603) `meltano select` now supports raw JSON Schema as a valid Catalog
- [#537](https://gitlab.com/meltano/meltano/issues/537) Add Extractor for Google Analytics (`tap-google-analytics`) to Meltano. It uses the tap defined in https://gitlab.com/meltano/tap-google-analytics/

### Changes

- [#621](https://gitlab.com/meltano/meltano/issues/621) Added new tutorial for tap-gitlab
- [#657](https://gitlab.com/meltano/meltano/issues/657) Update Analyze page to have single purpose views

### Fixes

- [#645](https://gitlab.com/meltano/meltano/issues/645) Fixed confusion around Loader Settings and Analytics DB Connector Settings
- [#580](https://gitlab.com/meltano/meltano/issues/580) Fixed `project_compiler` so the Analyze page can properly display custom topics
- [#658](https://gitlab.com/meltano/meltano/issues/658) Fixed the Analyze page when no models are present
- [#603](https://gitlab.com/meltano/meltano/issues/603) Fix an issue where `meltano select` would incorrectly report properties as excluded
- [#603](https://gitlab.com/meltano/meltano/issues/603) Fix an issue where `meltano select` incorrectly flatten nested properties
- [#553](https://gitlab.com/meltano/meltano/issues/553) Fix an issue where running `meltano select --list` for the first time would incorrectly report properties

### Break

## 0.25.0 - (2019-05-28)

---

### New

- [#586](https://gitlab.com/meltano/meltano/issues/586) `meltano ui` now automatically start Airflow if installed; Airflow UI available at `Orchestration`.
- [#592](https://gitlab.com/meltano/meltano/issues/592) Added baseline UX feedback via toast for uncaught API response errors with a link to "Submit Bug"
- [#642](https://gitlab.com/meltano/meltano/issues/642) Improved UX during extractor plugin installation so settings can be configured _during_ installation as opposed to waiting for the (typically lengthy) install to complete
- [!647](https://gitlab.com/meltano/meltano/merge_requests/647) Added preloader for occasional lengthy extractor loading and added feedback for lengthy entities loading
- [#645](https://gitlab.com/meltano/meltano/issues/645) Added an Analyze landing page to facilitate future sub-UIs including the Analyze database settings; Added proper Loader Settings UI.

### Fixes

- [#645](https://gitlab.com/meltano/meltano/issues/645) Fixed confusion around Loader Settings and Analyze database settings

## 0.24.0 - (2019-05-06)

---

### New

- [#622](https://gitlab.com/meltano/meltano/issues/622) Added ELT flow UI Routes & Deep Linking to advance user through next steps after each step's save condition vs. requiring them to manually click the next step to advance
- [#598](https://gitlab.com/meltano/meltano/issues/598) Updated color and greyscale use in the context of navigation and interactive elements to better communicate UI hierarchy
- [#607](https://gitlab.com/meltano/meltano/issues/607) Add "All/Default/Custom" button bar UI for improved entities selection UX
- [#32](https://gitlab.com/meltano/meltano-marketing/issues/32) Integrate Algolia Search for docs
- [#590](https://gitlab.com/meltano/meltano/issues/590) Add documentation for deploying Meltano in ECS
- [#628](https://gitlab.com/meltano/meltano/issues/628) Add documentation for tap-mongodb
- [!605](https://gitlab.com/meltano/meltano/merge_requests/605) Added tooltips for areas of UI that are WIP for better communication of a feature's status

### Changes

- [375](https://gitlab.com/meltano/meltano/issues/375) Meltano can now run on any host/port

### Fixes

- [#595](https://gitlab.com/meltano/meltano/issues/595) Fix `meltano invoke` not working properly with `dbt`
- [#606](https://gitlab.com/meltano/meltano/issues/606) Fix `SingerRunner.bookmark_state()` to properly handle and store the state output from Targets as defined in the Singer.io Spec.

## 0.23.0 - (2019-04-29)

---

### New

- [#32](https://gitlab.com/meltano/meltano-marketing/issues/32) Integrate Algolia Search for docs

### Changes

- [#522](https://gitlab.com/meltano/meltano/issues/522) Update Carbon tutorial with new instructions and screenshots

## 0.22.0 - (2019-04-24)

---

### New

- [#477](https://gitlab.com/meltano/meltano/issues/477) Add ability for users to sign up for email newsletters
- [!580](https://gitlab.com/meltano/meltano/merge_requests/580) Add sorting to plugins for improved UX, both UI via extractors/loaders/etc. and `meltano discover all` benefit from sorted results
- [!528](https://gitlab.com/meltano/meltano/issues/528) Add documentation for RBAC alpha feature and environment variables

### Changes

- [#588](https://gitlab.com/meltano/meltano/issues/588) Updated core navigation and depth hierarchy styling to facilitate main user flow and improved information architecture
- [#591](https://gitlab.com/meltano/meltano/issues/591) Revert #484: remove `meltano ui` being run outside a Meltano project.
- [#584](https://gitlab.com/meltano/meltano/issues/584) Initial v1 for enabling user to setup ELT linearly through the UI via a guided sequence of steps

### Fixes

- [#600](https://gitlab.com/meltano/meltano/issues/600) Fix a bug with meltano select when the extractor would output an invalid schema
- [#597](https://gitlab.com/meltano/meltano/issues/597) Automatically open the browser when `meltano ui` is run

## 0.21.0 - (2019-04-23)

---

### New

- [#477](https://gitlab.com/meltano/meltano/issues/477) Add ability for users to sign up for email newsletters

### Changes

- [#591](https://gitlab.com/meltano/meltano/issues/591) Revert #484: remove `meltano ui` being run outside a Meltano project.

## 0.20.0 - (2019-04-15)

---

### New

- Add documentation on custom transformations and models. Link to Tutorial: https://www.meltano.com/tutorials/create-custom-transforms-and-models.html

## 0.19.1 - (2019-04-10)

---

### New

- [#539](https://gitlab.com/meltano/meltano/issues/539) Add Tutorial for "Using Jupyter Notebooks" with Meltano
- [#534](https://gitlab.com/meltano/meltano/issues/534) Add UI entity selection for a given extractor
- [#520](https://gitlab.com/meltano/meltano/issues/520) Add v1 UI for extractor connector settings
- [#486](https://gitlab.com/meltano/meltano/issues/486) Add the `model-gitlab` plugin to Meltano. It includes .m5o files for analyzing data fetched using the Gitlab API. Repository used: https://gitlab.com/meltano/model-gitlab
- [#500](https://gitlab.com/meltano/meltano/issues/500) Add the `model-stripe` plugin to Meltano. It includes .m5o files for analyzing data fetched using the Stripe API. Repository used: https://gitlab.com/meltano/model-stripe
- [#440](https://gitlab.com/meltano/meltano/issues/440) Add the `model-zuora` plugin to Meltano. It includes .m5o files for analyzing data fetched using the Zuora API. Repository used: https://gitlab.com/meltano/model-zuora
- [#541](https://gitlab.com/meltano/meltano/issues/541) Add a 404 page for missing routes on the web app

### Fixes

- [#576](https://gitlab.com/meltano/meltano/issues/576) Fix switching between designs now works
- [#555](https://gitlab.com/meltano/meltano/issues/555) Fix `meltano discover` improperly displaying plugins
- [#530](https://gitlab.com/meltano/meltano/issues/530) Fix query generation for star schemas
- [#575](https://gitlab.com/meltano/meltano/issues/575) Move Airflow configuration to .meltano/run/airflow
- [#571](https://gitlab.com/meltano/meltano/issues/571) Fix various routing and API endpoint issues related to recent `projects` addition

## 0.19.0 - (2019-04-08)

---

### New

- [#513](https://gitlab.com/meltano/meltano/issues/513) Added initial e2e tests for the UI
- [#431](https://gitlab.com/meltano/meltano/issues/431) Add the `tap-zendesk` transform to Meltano. It is using the dbt package defined in https://gitlab.com/meltano/dbt-tap-zendesk
- [484](https://gitlab.com/meltano/meltano/issues/484) Updated `meltano ui` to automatically launch the UI, and projects from the UI (previously only an option in the CLI)
- [#327](https://gitlab.com/meltano/meltano/issues/327) Add `meltano add --custom` switch to enable integration of custom plugins
- [#540](https://gitlab.com/meltano/meltano/issues/540) Add CHANGELOG link in intro section of the docs
- [#431](https://gitlab.com/meltano/meltano/issues/431) Add the `model-zendesk` plugin to Meltano. It includes .m5o files for analyzing data fetched using the Zendesk API. Repository used: https://gitlab.com/meltano/model-zendesk
- [!544](https://gitlab.com/meltano/meltano/merge_requests/544) Add support for extracting data from CSV files by adding [tap-csv](https://gitlab.com/meltano/tap-csv) to Meltano
- [#514](https://gitlab.com/meltano/meltano/issues/514) Add 'airflow' orchestrators plugin to enable scheduling
- Add the `tap-zuora` transform to Meltano. It is using the dbt package defined in https://gitlab.com/meltano/dbt-tap-zuora

### Changes

- [#455](https://gitlab.com/meltano/meltano/issues/455) Add documentation about `target-snowflake`

### Fixes

- [#507](https://gitlab.com/meltano/meltano/issues/507) Ensure design name and table name don't need to match so multiple designs can leverage a single base table
- [#551](https://gitlab.com/meltano/meltano/issues/551) Fix HDA queries generated when an attribute is used both as a column and as an aggregate.
- [#559](https://gitlab.com/meltano/meltano/issues/559) Add support for running custom transforms for taps without default dbt transforms.

## 0.18.0 - (2019-04-02)

---

### New

- [#432](https://gitlab.com/meltano/meltano/issues/432) Add the `tap-zuora` transform to Meltano. It is using the dbt package defined in https://gitlab.com/meltano/dbt-tap-zuora

### Changes

- Remove Snowflake references from advanced tutorial.
- [#2 dbt-tap-zuora](https://gitlab.com/meltano/dbt-tap-zuora/issues/2) Remove custom SFDC related attributes from Zuora Account and Subscription Models
- Update [Contributing - Code Style](https://meltano.com/docs/contributing.html#code-style) documentation to including **pycache** troubleshooting

### Fixes

- [#529](https://gitlab.com/meltano/meltano/issues/529) Resolve "SFDC Tutorial - ELT Fails due to invalid schema.yml" by [#4 dbt-tap-salesforce](https://gitlab.com/meltano/dbt-tap-salesforce/issues/4) removing the schema.yml files from the dbt models for tap-salesforce.
- [#502](https://gitlab.com/meltano/meltano/issues/502) Fix the situation where an m5o has no joins, the design still will work.

## 0.17.0 - (2019-03-25)

---

### New

- [#485](https://gitlab.com/meltano/meltano/issues/485) Added various UI unit tests to the Analyze page
- [#370](https://gitlab.com/meltano/meltano/issues/370) Enabled authorization using role-based access control for Designs and Reports

### Changes

- [#283](https://gitlab.com/meltano/meltano/issues/283) Silence pip's output when there is not error
- [#468](https://gitlab.com/meltano/meltano/issues/468) Added reminder in docs regarding the need for `source venv/bin/activate` in various situations and added minor copy updates

### Fixes

- [#433](https://gitlab.com/meltano/meltano/issues/433) Add the `sandbox` configuration to `tap-zuora`.
- [#501](https://gitlab.com/meltano/meltano/issues/501) Fix `meltano ui` crashing when the OS ran out of file watcher.
- [#510](https://gitlab.com/meltano/meltano/issues/510) Fix an issue when finding the current Meltano project in a multi-threaded environment.
- [#494](https://gitlab.com/meltano/meltano/issues/494) Improved documentation around tutorials and Meltano requirements
- [#492](https://gitlab.com/meltano/meltano/issues/492) A few small contextual additions to help streamline the release process
- [#503](https://gitlab.com/meltano/meltano/issues/503) Fix a frontend sorting issue so the backend can properly generate an up-to-date query

## 0.16.0 - (2019-03-18)

---

### New

- Add support for extracting data from Gitlab through the updated tap-gitlab (https://gitlab.com/meltano/tap-gitlab)
- Add the `tap-gitlab` transform to Meltano. It is using the dbt package defined in https://gitlab.com/meltano/dbt-tap-gitlab
- Add "Copy to Clipboard" functionality to code block snippets in the documentation
- Add the `tap-stripe` transform to Meltano. It is using the dbt package defined in https://gitlab.com/meltano/dbt-tap-stripe
- Add new command `meltano add model [name_of_model]`
- Add models to the available plugins

### Changes

- Various documentation [installation and tutorial improvements](https://gitlab.com/meltano/meltano/issues/467#note_149858308)
- Added troubleshooting button to help users add context to a pre-filled bug issue

### Fixes

- Fix the API database being mislocated
- Replaced the stale Meltano UI example image in the Carbon Emissions tutorial
- 473: Fix the docker image (meltano/meltano) from failing to expose the API

## 0.15.1 - (2019-03-12)

---

### Fixes

- locks down dependencies for issues with sqlalchemy snowflake connector

## 0.15.0 - (2019-03-11)

---

### New

- Add Salesforce Tutorial to the docs
- Add documentation for the permissions command
- Add tracking for the `meltano ui` command

### Fixes

- Updated analytics to properly recognize SPA route changes as pageview changes

## 0.14.0 - (2019-03-04)

---

### New

- Update stages table style in docs
- Add custom transforms and models tutorial to the docs

### Changes

- Add api/v1 to every route
- Update DbtService to always include the my_meltano_project model when transform runs

### Fixes

- Resolved duplicate display issue of Dashboards and Reports on the Files page
- Removed legacy `carbon.dashboard.m5o` (regression from merge)
- Updated dashboards and reports to use UI-friendly name vs slugified name
- Fix minor clipped display issue of right panel on `/settings/database`
- Fix minor display spacing in left panel of Settings
- Fix dashboard page to properly display a previously active dashboard's updated reports
- Fix pre-selected selections for join aggregates when loading a report
- Fix charts to display multiple aggregates (v1)
- Fix 404 errors when refreshing the frontend
- Fix a regression where the Topics would not be shown in the Files page

## 0.13.0 - (2019-02-25)

---

### New

- Add the `tap-salesforce` transform to Meltano. It is using the dbt package defined in https://gitlab.com/meltano/dbt-tap-salesforce
- Add m5o model and tables for tap-salesforce
- Updated the deep-link icon (for Dashboards/Reports on the Files page)

### Changes

- Polished the RBAC view, making it clearer the feature is experimental.
- Rename "Models" to "Topics"
- Use the current connection's schema when generating queries at run time for Postgres Connections.
- Add support for multiple Aggregates over the same attribute when generating HDA queries.

## 0.12.0 - (2019-02-21)

---

### New

- UI cleanup across routes (Analyze focus) and baseline polish to mitigate "that looks off comments"
- Update installation and contributing docs
- Meltano implement role-based access control - [!368](https://gitlab.com/meltano/meltano/merge_requests/368)
- Add version CLI commands for checking current Meltano version
- Add deep linking to dashboards
- Add deep linking to reports

### Fixes

- Fixed a problem when environment variables where used as default values for the CLI - [!390](https://gitlab.com/meltano/meltano/merge_requests/390)
- Fixed dashboards initial load issue due to legacy (and empty) `carbon.dashboard.m5o` file
- New standardized approach for `.m5o` id generation (will need to remove any dashboard.m5o and report.m5o)

## 0.11.0 - (2019-02-19)

---

### New

- Update installation and contributing docs
- Add support for generating Hyper Dimensional Aggregates (HDA)
- Add internal Meltano classes for representing and managing Designs, Table, Column, Aggregate, Definitions, and Query definitions

### Changes

- Move core functionality out of `api/controllers` to `/core/m5o` (for m5o and m5oc management) and `/core/sql` (for anything related to sql generation)

### Fixes

- Fixed a problem when environment variables where used as default values for the CLI - [!390](https://gitlab.com/meltano/meltano/merge_requests/390)

## 0.10.0 - (2019-02-12)

---

### New

- Add gunicorn support for Meltano UI as a WSGI application - [!377](https://gitlab.com/meltano/meltano/merge_requests/377)
- Meltano will now generate the minimal joins when building SQL queries - [!382](https://gitlab.com/meltano/meltano/merge_requests/382)

### Changes

- Add analytics to authentication page
- Meltano will now use SQLite for the job log. See https://meltano.com/docs/architecture.html#job-logging for more details.
- Removed manual `source .env` step in favor of it running automatically

### Fixes

- Meltano will correctly source the `.env`
- fixed charts to render as previously they were blank
- Fixed Analyze button groupd CSS to align as a single row

### Breaks

- Meltano will now use SQLite for the job log. See https://meltano.com/docs/architecture.html#job-logging for more details.
- URL routing updates ('/model' to '/files', removed currently unused '/extract', '/load', '/transform' and '/project/new')

## 0.9.0 - (2019-02-05)

---

### New

- add ability to save reports
- add ability to update an active report during analysis
- add ability to load reports
- add dashboards page and related add/remove report functionality

### Changes

- Generate default `Meltano UI` connection for the `meltano.db` SQLite DB when a new project is created with `meltano init`
- updated main navigation to Files, Analysis, and Dashboards
- Update the `meltano permissions grant` command to fetch the existing permissions from the Snowflake server and only return sql commands for permissions not already assigned
- Add `--diff` option to the `meltano permissions grant` command to get a full diff with the permissions already assigned and new ones that must be assigned

### Fixes

- Entry model definition correctly defines `region_id`.
- Updated the Fundamentals documentation section regarding reports
- Fixed Files page for empty state of Dashboards and Reports
- Fixed Analyze page's left column to accurately preselect columns and aggregates after loading a report

## 0.8.0 - (2019-01-29)

---

### New

- Add tracking of anonymous `meltano cli` usage stats to Meltano's Google Analytics Account
- Add `project_config.yml` to all meltano projects to store concent for anonymous usage tracking and the project's UUID

### Changes

- Add `--no_usage_stats` option to `meltano init <project_name>` to allow users to opt-out from anonymous usage stats tracking
- Bundled Meltano models are now SQLite compatible.

## 0.7.0 - (2019-01-22)

---

### New

- Added basic authentication support for meltano ui.
- Meltano will now automatically source the .env
- Updated docs with `.m5o` authoring requirements and examples
- add support for timeframes in tables
- add basic analytics to understand usage
- add disabled UI for the lack of timeframes support in sqlite
- update Results vs. SQL UI focus based on a results response or query update respectively

### Changes

- Meltano will now discover components based on `https://meltano.com/discovery.yml`
- sample designs are now packaged with meltano

### Fixes

- Updated mobile menu to work as expected
- Updated tutorial docs with improved CLI commands and fixed the host setting to `localhost`

## 0.6.1 - (2019-01-15)

---

## 0.6.0 - (2019-01-15)

---

### New

- add new command `meltano add transform [name_of_dbt_transformation]`
- add transforms to the available plugins

### Changes

- Auto install missing plugins when `meltano elt` runs
- Terminology updates for simpler understanding

### Fixes

- Edit links on the bottom of doc pages are working now

### Breaks

- Updated docs tutorial bullet regarding inaccurate "Validate" button

## 0.5.0 - (2019-01-09)

---

### New

- ensure `meltano init <project-name>` runs on windows
- settings ui now provides sqlite-specific controls for sqlite dialect
- add `target-sqlite` to available loaders for meltano projects
- add new command `meltano add transformer [name_of_plugin]`
- add transformers (dbt) to the available plugins

### Changes

- extractors and loaders are arguments in the elt command instead of options
- `meltano www` is now `meltano ui`
- remove dbt installation from `meltano init`
- move everything dbt related under `transform/`
- update `meltano elt` to not run transforms by default
- update `meltano elt` to auto generate the job_id (job_id has been converted to an optional argument)

### Fixes

- left joins now work correctly in analyze.
- fixed broken sql toggles in analyze view
- fixed sql output based on sql toggles in analyze view

## 0.4.0 - (2019-01-03)

---

### New

- add Using Superset with Meltano documentation

## 0.3.3 - (2018-12-21)

---

## 0.3.2 - (2018-12-21)

---

## 0.3.1 - (2018-12-21)

---

### Changes

- add default models for 'tap-carbon-intensity'.
- Meltano Analyze is now part of the package.
- removes database dependency from Meltano Analyze and uses .ma files
- update the error message when using Meltano from outside a project - [!238](https://gitlab.com/meltano/meltano/merge_requests/238)

## 0.3.0 - (2018-12-18)

---

### New

- updated Settings view so each database connection can be independently disconnected
- add `meltano select` to manage what is extracted by a tap.

### Changes

- documentation site will utilize a new static site generation tool called VuePress

- meltano.com will be deployed from the meltano repo

### Fixes

- model dropdown now updates when updating database (no longer requires page refresh)
- prevent model duplication that previously occurred after subsequent "Update Database" clicks

## 0.2.2 - (2018-12-11)

---

### Changes

- documentation site will utilize a new static site generation tool called VuePress
- first iteration of joins (working on a small scale)

## 0.2.1 - (2018-12-06)

---

### Fixes

- resolve version conflict for `idna==2.7`
- fix the `discover` command in the docker images
- fix the `add` command in the docker images
- fix module not found for meltano.core.permissions.utils

## 0.2.0 - (2018-12-04)

---

### New

- add `meltano permissions grant` command for generating permission queries for Postgres and Snowflake - [!90](https://gitlab.com/meltano/meltano/merge_requests/90)
- add 'tap-stripe' to the discovery

### Changes

- demo with [carbon intensity](https://gitlab.com/meltano/tap-carbon-intensity), no API keys needed
- .ma file extension WIP as alternative to lkml

### Fixes

- fix order in Meltano Analyze

## 0.1.4 - (2018-11-27)

### Fixes

- add default values for the 'www' command - [!185](https://gitlab.com/meltano/meltano/merge_requests/185)
- add CHANGELOG.md
- fix a problem with autodiscovery on taps - [!180](https://gitlab.com/meltano/meltano/merge_requests/180)

### Changes

- move the 'api' extra package into the default package
- add 'tap-fastly' to the discovery

---

## 0.1.3

### Changes

- remove `setuptools>=40` dependency
- `meltano` CLI is now in the `meltano` package

## 0.1.2

### Fixes

- target output state is now saved asynchronously

## 0.1.1

### Changes

- initial release
