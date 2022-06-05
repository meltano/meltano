# required reading

See https://www.iglooanalytics.com/blog/understanding-snowplow-analytics-custom-contexts.html for more information.

# iguctl usage

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

Note that igluctl is Java and so will require local runtime to be installed. 

# Snowcat Cloud access

When a new version of the schema is introduced , it must also be updated in our schema registry,
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

Once up and running you can interact with this rest api:

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
MELTANO_DISABLE_TRACKING=False MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS='["http://localhost:9090"]' meltano invoke something
```
