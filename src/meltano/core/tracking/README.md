# Required Reading

See https://www.iglooanalytics.com/blog/understanding-snowplow-analytics-custom-contexts.html for more information.

# `iguctl` usage

To validate/lint a schema use [`iguctl`](https://github.com/snowplow-incubator/igluctl) rather than the Snowcat Cloud UI e.g.:

```bash
 $ $PATH_TO/igluctl lint ./src/meltano/core/tracking
OK: com.meltano/cli_context/jsonschema/1-0-0
OK: com.meltano/environment_context/jsonschema/1-0-0
OK: com.meltano/plugins_context/jsonschema/1-0-0
OK: com.meltano/project_context/jsonschema/1-0-0
TOTAL: 4 valid schemas
TOTAL: 0 schemas didn't pass validation
```

Note that `igluctl` is a Java program, and so will require local runtime to be installed.

# Snowcat Cloud access

When a new version of the schema is introduced, it must also be updated in our schema registry,
SnowcatCloud.

Login to https://app.snowcatcloud.com/ using your Meltano email address. Request permissions from
an account admin if necessary. As of the time of writing this, the admins are:

- aj@meltano.com
- pat@meltano.com
- will@meltano.com
- edgar@meltano.com
- taylor@meltano.com
- florian@meltano.com

Once SnowcatCloud provides an API to update the schemas, we should add a CI job to update them
automatically when a release pipeline is run with changes in this directory.

# Snowcloud Micro - for local development and testing

To test/validate schemas [snowcloud-micro](https://github.com/snowplow-incubator/snowplow-micro) can be used:


```
# from this directory
docker run \
  --mount type=bind,source=$(pwd),destination=/config \
  -p 9090:9090 \
  snowplow/snowplow-micro:1.2.1 \
  --collector-config /config/micro.conf \
  --iglu /config/iglu.json
```

Once up and running you can interact with this REST api:

```
# list a known schema
http localhost:9090/micro/iglu/com.meltano/environment_context/jsonschema/1-0-0

# list a summary
http localhost:9090/micro/all

# good events
http localhost:9090/micro/good

# bad events
http localhost:9090/micro/bad

# reset counters
http localhost:9090/micro/reset
```

To redirect events to a local snowplow micro instance:

```
MELTANO_SEND_ANONYMOUS_USAGE_STATS=True MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS='["http://localhost:9090"]' meltano invoke something
```

# Testing with Snowplow Micro under Pytest

Snowplow Micro will be run under Pytest automatically if `docker-compose` is available. We use `pytest-docker` to bring up the services defined in `tests/fixtures/docker/docker-compose.yml`.

Tests can use the `snowplow` fixture to access Snowplow Micro through its REST interface. The `snowplow` fixture yields a `SnowplowMicro` instance which is reset before and after every test. It has methods `all`, `good`, `bad`, which all return the JSON that their REST endpoints return, and `reset`, which resets Snowplow Micro and returns `None`.

Tests using this fixture will automatically have `send_anonymous_usage_stats` enabled, and have their collection endpoint set to the local Snowplow Micro service.

If `pytest-docker` was unable to start Snowplow Micro, tests that use the `Snowplow` fixture will be skipped. To avoid having a test skipped one can use the `snowplow_optional` fixture instead, which is the same as the `snowplow` fixture, but yields `None` if `pytest-docker` was not able to start Snowplow Micro. If you use the `snowplow_optional` fixture, you should handle the case where it yields `None`.

If Snowplow Micro is available, all tests that use `CliRunner.invoke` are automatically checked to ensure that no "bad" events (according to Snowplow Micro) were fired. More complex checks must be done manually.
