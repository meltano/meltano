# CHANGELOG

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/) and [Keep a Changelog](http://keepachangelog.com/).

## v3.9.2 (2026-02-03)

### 🐛 Fixes

- Default smart-open logs to the warning level and above (#9617)
- Filter out Alembic logs of level INFO and below (#9734)
- Bump `fasteners` to 0.20 (#9637)

### ⚙️ Under the Hood

- Filter out `urllib3` logs below the error level (#9599)
- Remove missing import handling for state backends now that they are loaded dynamically (#9479)
- Get package version from distribution metadata (#9438)

### ⚡ Performance Improvements

- Revert to sync APIs for writing the tap catalog file following discovery (#9724)

### 📦 Packaging changes

- Pin core `click` and `sqlalchemy` dependencies to their minor versions (#9449)
- Remove upper constraint on Python version
- Removed license classifier made redundant by PEP 639 (#9711)
- Require google-cloud-storage 3+
- Require uv 0.8.14+
- Allow uv 0.9 (#9550)
- Allow pip 26.0 (#9799)
- Allow `packaging` 26.0 (#9762)
- Allow ruamel-yaml 0.19.x (#9756)
- Allow check-jsonschema 0.36.x
- Allow Rich 14.3.x (#9780)
- Remove upper constraint on aiodocker
- Bump upper constraint on boto3

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

## v2.x

See [changelogs/2.x.md](changelogs/v2.md).

## v1.x

See [changelogs/1.x.md](changelogs/v1.md).

## v0.x

See [changelogs/0.x.md](changelogs/v0.md).
