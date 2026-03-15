---
title: Logging and Monitoring
description: Learn how to configure logging and monitoring for Meltano.
layout: doc
sidebar_position: 19
---

## Logging

A quick way to change the log format of the command line output is [the `--log-format` global option](/reference/settings/#clilog_format). For example:

```bash
meltano --log-format=json run my-job
```

## Viewing Job Logs

Meltano stores logs for all job runs in the `.meltano/logs` directory. You can use the [`meltano logs`](/reference/command-line-interface#logs) command to easily view these logs without navigating the file system.

To list recent job runs:
```bash
meltano logs list
```

To view the log for a specific run:
```bash
meltano logs show <log_id>
```

The logs command provides options for viewing partial logs with `--tail`, outputting in JSON format with `--format json`, and more. See the [CLI reference](/reference/command-line-interface#logs) for full details.

## Configuring Logging

Logging in Meltano can also be controlled in more detail via a standard YAML-formatted Python logging dict config file ([configuration dictionary schema](https://docs.python.org/3/library/logging.config.html#configuration-dictionary-schema)).

By default, meltano will look for this in a `logging.yaml` file in the project root. Both `.yaml` and `.yml` file extensions are supported. However, you can override this by
setting the [environment variable](/guide/configuration#configuring-settings) `MELTANO_CLI_LOG_CONFIG` or by using the
`meltano` CLI option `--log-config`. e.g. `meltano --log-config=my-prod-logging.yaml ...`.

A logging.yaml contains a few key sections that you should be aware of.

- `formatters` - This section contains the formatters that are used by the handlers. This controls the output format of the log messages (e.g. json).
- `handlers` - This section contains the handlers which are used by the loggers. This controls the output destination of the log messages (e.g. the console).
- `root` - The root section cover the root logger, which is effectively the default config for all loggers unless they are otherwise configured.
- `loggers` - This section allows you to explicitly control specific module/class/etc named loggers.

A few key points to note:

1. Different handlers can use different formats. Meltano ships with [3 formatters](https://github.com/meltano/meltano/blob/main/src/meltano/core/logging/formatters.py):
   - `meltano.core.logging.console_log_formatter` - A formatter that renders lines for the console, with optional colorization. When colorization is enabled, tracebacks are formatted with the `rich` python library. Supports `colors` (bool), `show_locals` (bool), `max_frames` (int, default: 2), `all_keys` (bool), and `include_keys` (set[str]) parameters. By default, only essential keys are displayed for cleaner output.
   - `meltano.core.logging.json_log_formatter` - A formatter that renders lines in JSON format.
   - `meltano.core.logging.key_value` - A formatter that renders lines in key=value format.
   - `meltano.core.logging.plain_formatter` - A formatter that renders lines in a plain text format.
2. **Console output filtering**: By default, the console formatter displays only essential log keys for cleaner output. The default keys include:
   - Base keys: `timestamp`, `level`, `event`, `logger`, `logger_name`
   - Plugin subprocess keys: `string_id`
   - Plugin structured logging keys: `plugin_exception`, `metric_info`

   You can control this behavior using the `all_keys` and `include_keys` parameters in your logging configuration. When both `all_keys` and `include_keys` are specified,
   **`include_keys` takes precedence**. The behavior is:

   1. If `include_keys` is set (regardless of `all_keys`): Shows default keys + specified keys
   2. If only `all_keys: true` is set: Shows all keys
   3. If neither is set (default): Shows only default keys

3. Different loggers can use different handlers and log at different log levels.
4. We support all the [standard python logging handlers](https://docs.python.org/3/library/logging.handlers.html#) (e.g. rotating files, syslog, etc).
5. If a logging config file is found, it will take precedence over the `--log-format` and `--log-level` CLI options.

Here's an annotated example of a logging.yaml file:

```yaml
version: 1
disable_existing_loggers: false

formatters:
  default: # use a format similar to default generic python logging format
    format: "[%(asctime)s] [%(process)d|%(threadName)10s|%(name)s] [%(levelname)s] %(message)s"
  structured_colored:
    (): meltano.core.logging.console_log_formatter
    colors: true
  structured_colored_all_keys: # log format with colored output showing all log keys
    (): meltano.core.logging.console_log_formatter
    colors: true
    all_keys: true # displays all log keys instead of just the default set
  structured_plain_no_locals: # log format for structured plain text logs without colored output and without local variables
    (): meltano.core.logging.console_log_formatter
    colors: false # also disables `rich` traceback formatting
    show_locals: false # disables local variable logging in tracebacks (which be very verbose and leak sensitive data)
  structured_locals: # log format for structured plain text logs WITH local variables
    (): meltano.core.logging.console_log_formatter
    colors: true # also enables traceback formatting with `rich`
    show_locals: true # enables local variable logging in tracebacks (can be very verbose and leak sensitive data)
    max_frames: 5 # maximum number of frames to show in tracebacks (default: 2)
  key_value: # log format for traditional key=value style logs
    (): meltano.core.logging.key_value_formatter
    sort_keys: false
  json: # log format for json formatted logs
    (): meltano.core.logging.json_formatter
    callsite_parameters: true # adds `pathname`, `lineno`, `func_name` and `process` to each log entry
    dict_tracebacks: false # removes the `exception` object that is added to each log entry
    show_locals: true # enables local variable logging in tracebacks

handlers:
  console: # log to the console (stderr) using structured_colored formatter, logging everything at DEBUG level and up
    class: logging.StreamHandler
    level: DEBUG
    formatter: structured_colored
    stream: "ext://sys.stderr"
  meltano_log: # log everything INFO and above to a file in the project root called meltano.log in json format
    class: logging.FileHandler
    level: INFO
    filename: meltano.log
    formatter: json
  my_warn_file_handler: # log everything WARNING and above to automatically rotating log file in key_value format
    class: logging.handlers.RotatingFileHandler
    level: WARN
    formatter: key_value
    filename: /tmp/meltano_warn.log
    maxBytes: 10485760
    backupCount: 20
    encoding: utf8

root:
  level: DEBUG # the root logger must always specify a level
  propagate: yes # propagate to child loggers
  handlers: [console, meltano_log, my_warn_file_handler] # by default use these three handlers

loggers:
  somespecific.module.logger: # if you want debug logs for a specific named logger or module
    level: DEBUG
    handlers: [console]
    propogate: no
  urllib3: # for example hide all urllib3 debug logs
    level: WARNING
    handlers: [console, meltano_log]
    propogate: no
```

For a detailed explanation of the above of the file format, see the [python logging documentation](https://docs.python.org/3/library/logging.config.html#configuration-file-format).

## Local development config example

While working with Meltano locally it's sometimes nice to have more terse logging on the console, but still have DEBUG
level info written to a log file behind scenes incase you need to debug something. To accomplish that, you can use a
file like:

```yaml
version: 1
disable_existing_loggers: false

formatters:
  structured_colored:
    (): meltano.core.logging.console_log_formatter
    colors: True
  json:
    (): meltano.core.logging.json_formatter

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: structured_colored
    stream: "ext://sys.stderr"
  file:
    class: logging.FileHandler
    level: DEBUG
    filename: meltano.log
    formatter: json

root:
  level: DEBUG
  propagate: yes
  handlers: [console, file]
```

To have it be even more terse, you can use level `WARN` instead of `INFO`. In the case of something like a successful
`meltano run` invocation this would produce no output at all.

## A generic starting config for log management providers

Most logging management tools will readily accept structured logs delivered in JSON format. As such, when all else fails
configuring Meltano to log in JSON format is a good first step.

For example, to log to a file called `meltano.log` in JSON format, while also reporting WARNING lines and above on
the console you could use the following `logging.yaml` config:

```yaml
version: 1
disable_existing_loggers: false

formatters:
  structured_plain:
    (): meltano.core.logging.console_log_formatter
    colors: False
  json:
    (): meltano.core.logging.json_formatter

handlers:
  console:
    class: logging.StreamHandler
    level: WARNING
    formatter: structured_plain
    stream: "ext://sys.stderr"
  file:
    class: logging.FileHandler
    level: INFO
    filename: meltano.log
    formatter: json

root:
  level: DEBUG
  propagate: yes
  handlers: [console, file]
```

If instead you wanted the console output to log in JSON format because your logging solution is capturing output directly
you could use the following config:

```yaml
version: 1
disable_existing_loggers: false

formatters:
  json:
    (): meltano.core.logging.json_formatter

handlers:
  console:
    class: logging.StreamHandler
    formatter: json
    stream: "ext://sys.stderr"

root:
  level: INFO
  propagate: yes
  handlers: [console]
```

## Datadog logging config

You have a couple options for configuring logs for Datadog. The easiest approach may be to log to a file in JSON format
and collect it with the Datadog Agent.

To do so you'll want to use a `logging.yaml` config that writes directly to a file like in the previously examples:

```yaml
version: 1
disable_existing_loggers: false

formatters:
  structured_plain:
    (): meltano.core.logging.console_log_formatter
    colors: False
  json:
    (): meltano.core.logging.json_formatter

handlers:
  console:
    class: logging.StreamHandler
    level: WARNING
    formatter: structured_plain
    stream: "ext://sys.stderr"
  file:
    class: logging.FileHandler
    level: INFO
    filename: meltano.log
    formatter: json

root:
  level: DEBUG
  propagate: yes
  handlers: [console, file]
```

With a Datadog Agent `conf.yaml` similar to:

```yaml
init_config:

instances:

##Log section
logs:
  - type: file
    path: "<PATH_TO_MELTANO>.log"
    service: "meltano"
    source: python
    sourcecategory: sourcecode
```

See https://docs.datadoghq.com/logs/log_collection/python/?tab=jsonlogformatter for further details.

## Google Cloud logging config
That means when capturing `meltano run`,
`meltano invoke` and `meltano el` console output directly via something like CloudRun the built-in json format is
sufficient:

#For Google Cloud Logging (formerly Stackdriver), Meltano can output logs in JSON format,
but Google Cloud does not automatically recognize them as structured logs.

You may notice that Meltano logs show `"level": "info"` even when warnings or errors
occur. This is expected behavior. Logs coming from plugins and subprocesses are
normalized by Meltano, and their original Python log severity is not preserved.

Because of this, when Meltano logs are sent directly to Google Cloud Logging,
severity-based filtering and alerts may not work as expected unless the logs are
explicitly transformed.
##

### Severity mapping with the Google Cloud Ops Agent

To correctly parse Meltano logs and map severity levels in Google Cloud Logging,
the Google Cloud Ops Agent must be configured to parse the JSON payload and
explicitly map severity fields.



#### Example configuration

**`logging.yaml`**
```yaml
version: 1
disable_existing_loggers: false

formatters:
  json:
    (): meltano.core.logging.json_formatter

handlers:
  file:
    class: logging.FileHandler
    level: DEBUG
    filename: /tmp/meltano.log
    formatter: json

root:
  level: DEBUG
  handlers: [file]

```yaml

/etc/google-cloud-ops-agent/config.yaml

logging:
  receivers:
    meltano:
      type: files
      include_paths:
        - /tmp/meltano.log
  processors:
    json:
      type: parse_json
    map_severity:
      type: modify_fields
      fields:
        severity:
          move_from: jsonPayload.level
  service:
    pipelines:
      meltano:
        receivers: [meltano]
        processors: [json, map_severity]



```yaml
version: 1
disable_existing_loggers: false

formatters:
  json:
    (): meltano.core.logging.json_formatter

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: json
    stream: "ext://sys.stderr"

root:
  level: INFO
  propagate: yes
  handlers: [console]
```

## Log fields

While not a complete dictionary of all fields available in the log, the following are common fields that you may encounter,
and ones that are useful for filter or grouping:

- `level` - The log level.
- `timestamp` - The timestamp of the log entry.
- `event` - The actual log message.
- `name` or `source` - Where the log message originated e.g. `tap-gitlab` if the log message originated from a Tap.
- `stdio` - When the log message originated from a plugin, this field indicates whether the log message originated from stdout or stderr. Allowing you to filter out standard singer events for example.
- `cmd_type` - The type of command that the log message originated from.
- `state_id` - The associated state id.
- `success` - Whether something succeeded or failed.
- `error` - Where possible indicates the error type if one occurred.

## Tips and tricks

### Filter logs

Use [jq](https://stedolan.github.io/jq/) to filter the output of JSON formatted Meltano logs to only show the lines you're interested in.

```bash
cat meltano.log | jq -c 'select(.string_id == "tap-gitlab" and .stdio == "stderr") | .event'
```

### Exclude plugin stdout logs

When DEBUG level logging is enabled, a plugin's stdout logs can be very verbose. For extractors, these can include the raw [Singer](/reference/glossary/#singer) messages. To exclude them, you can set the `meltano.plugins` logger to the `INFO` level.

```yaml
version: 1
disable_existing_loggers: no

loggers:
  # Disable logging of tap and target stdout
  meltano.plugins.stdout:
    level: INFO
    propagate: no
  root:
    level: DEBUG
    handlers: [console]
```

## Structured Log Parsing

Meltano includes advanced log parsing capabilities that can automatically parse and re-emit structured logs from plugins, particularly those using the Singer SDK's structured logging format.

### Overview

When plugins output structured JSON logs, Meltano can:

1. **Parse** the structured logs to extract semantic information
2. **Transform** the logs using the parsed data for enhanced metadata
3. **Re-emit** the logs through Meltano's logging system with additional context

This provides better log aggregation, filtering, and analysis capabilities while maintaining backward compatibility with existing logging infrastructure.

### Supported Log Formats

#### Singer SDK Structured Logs

Meltano automatically detects and parses Singer SDK structured logs that include the following required fields:

- `level` - Log level (debug, info, warning, error, critical)
- `pid` - Process ID
- `logger_name` - Name of the logger that emitted the log
- `ts` - Timestamp (Unix timestamp)
- `thread_name` - Thread name
- `app_name` - Application name (e.g., "tap-github", "target-postgres")
- `stream_name` - Stream name (if applicable)
- `message` - Log message
- `extra` - Additional metadata

Example Singer SDK structured log:

```json
{
  "level": "info",
  "pid": 12345,
  "logger_name": "tap_github",
  "ts": 1705709074.883021,
  "thread_name": "MainThread",
  "app_name": "tap-github",
  "stream_name": "users",
  "message": "Processing stream users",
  "extra": {
    "record_count": 150,
    "api_endpoint": "https://api.github.com/users"
  }
}
```

#### Metric Logs

Structured logs with metric information are handled specially:

```json
{
  "level": "info",
  "pid": 12345,
  "logger_name": "tap_github",
  "ts": 1705709074.883021,
  "thread_name": "MainThread",
  "app_name": "tap-github",
  "stream_name": "users",
  "message": "METRIC",
  "metric_info": {
    "metric_name": "records_processed",
    "value": 150,
    "tags": {"stream": "users", "status": "success"}
  },
  "extra": {}
}
```

### Configuration

Log parsing is automatically enabled when Meltano detects that a plugin supports structured logging. You can control this behavior through plugin capabilities.

#### Plugin Capabilities

Plugins can declare structured logging support through capabilities:

```yaml
plugins:
  extractors:
  - name: tap-github
    variant: meltanolabs
    capabilities:
    - structured-logs
```

#### Manual Parser Selection

You can also manually specify which parser to use for specific plugins:

```yaml
plugins:
  extractors:
  - name: tap-github
    variant: meltanolabs
    settings:
      log_parser: singer-sdk  # Force use of Singer SDK parser
```

### Benefits

Structured log parsing enables enhanced metadata extraction, better filtering and search capabilities through tools like `jq`, and automatic performance monitoring through parsed metric logs. This provides improved observability while maintaining backward compatibility with existing logging infrastructure.

### Parser Implementation

Meltano uses a factory pattern for log parsers with the following components:

1. **SingerSDKLogParser** - Parses Singer SDK structured JSON logs
2. **PassthroughLogParser** - Fallback for unstructured logs
3. **LogParserFactory** - Manages parser selection and fallback logic

The parsing process:

1. Attempts to parse with the preferred parser (if specified)
2. Falls back to trying all registered parsers
3. Uses passthrough parser as final fallback
4. Maintains original log content if parsing fails

### Troubleshooting

#### Parser Selection Issues

If logs aren't being parsed correctly:

1. Check plugin capabilities: `meltano invoke <plugin> --print-capabilities`
2. Verify log format matches expected structure
3. Review parser selection logic in debug logs

#### Performance Considerations

Log parsing adds minimal overhead:

- Parsing performance: ~381K logs/second
- Memory usage: Minimal additional allocation
- Fallback behavior: Preserves original performance for unparseable logs

#### Debug Log Parsing

Enable debug logging to troubleshoot parsing issues:

```yaml
loggers:
  meltano.core.logging.parsers:
    level: DEBUG
```

This will show parsing attempts and failures for debugging purposes.
