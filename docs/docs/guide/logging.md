---
title: Logging and Monitoring
description: Learn how to configure logging and monitoring for Meltano.
layout: doc
sidebar_position: 19
---

## Logging

Logging in meltano can be controlled via a standard yaml formatted [python logging dict config file](https://docs.python.org/3/library/logging.config.html#configuration-dictionary-schema).

By default, meltano will look for this in a `logging.yaml` file in the project root. However, you can override this by
setting the [environment variable](/guide/configuration#configuring-settings) `MELTANO_CLI_LOG_CONFIG` or by using the
`meltano` CLI option `--log-config`. e.g. `meltano --log-config=my-prod-logging.yaml ...`.

A logging.yaml contains a few key sections that you should be aware of.

- `formatters` - This section contains the formatters that are used by the handlers. This controls the output format of the log messages (e.g. json).
- `handlers` - This section contains the handlers which are used by the loggers. This controls the output destination of the log messages (e.g. the console).
- `root` - The root section cover the root logger, which is effectively the default config for all loggers unless they are otherwise configured.
- `loggers` - This section allows you to explicitly control specific module/class/etc named loggers.

A few key points to note:

1. Different handlers can use different formats. Meltano ships with [3 formatters](https://github.com/meltano/meltano/blob/main/src/meltano/core/logging/formatters.py):
   - `meltano.core.logging.console_log_formatter` - A formatter that renders lines for the console, with optional colorization. When colorization is enabled, tracebacks are formatted with the `rich` python library.
   - `meltano.core.logging.json_log_formatter` - A formatter that renders lines in JSON format.
   - `meltano.core.logging.key_value` - A formatter that renders lines in key=value format.
2. Different loggers can use different handlers and log at different log levels.
3. We support all the [standard python logging handlers](https://docs.python.org/3/library/logging.handlers.html#) (e.g. rotating files, syslog, etc).

Here's an annotated example of a logging.yaml file:

```yaml
version: 1
disable_existing_loggers: false

formatters:
  default: # use a format similar to default generic python logging format
    format: "[%(asctime)s] [%(process)d|%(threadName)10s|%(name)s] [%(levelname)s] %(message)s"
  structured_colored:
    (): meltano.core.logging.console_log_formatter
    colors: True
  structured_plain_no_locals: # log format for structured plain text logs without colored output and without local variables
    (): meltano.core.logging.console_log_formatter
    colors: False # also disables `rich` traceback formatting
    show_locals: False # disables local variable logging in tracebacks (which be very verbose and leak sensitive data)
  structured_locals: # log format for structured plain text logs WITH local variables
    (): meltano.core.logging.console_log_formatter
    colors: True # also enables traceback formatting with `rich`
    show_locals: True # enables local variable logging in tracebacks (can be very verbose and leak sensitive data)
  key_value: # log format for traditional key=value style logs
    (): meltano.core.logging.key_value_formatter
    sort_keys: False
  json: # log format for json formatted logs
    (): meltano.core.logging.json_formatter
    callsite_parameters: true # adds `pathname`, `lineno`, and `func_name` to each log entry
    dict_tracebacks: false # removes the `exception` object that is added to each log entry

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

For Google Cloud Logging (stackdriver) the default json log format is sufficient. That means when capturing `meltano run`,
`meltano invoke` and `meltano elt` console output directly via something like CloudRun the built-in json format is
sufficient:

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

Use [jq](https://stedolan.github.io/jq/) to filter the output of JSON formatted Meltano logs to only show the lines you're interested in.

```bash
cat meltano.log | jq -c 'select(.string_id == "tap-gitlab" and .stdio == "stderr") | .event'
```
