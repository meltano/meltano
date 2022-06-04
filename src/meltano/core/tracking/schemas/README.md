To validate/lint a schema use `iguctl` rather than the Snowcat Cloud UI e.g.:

```bash
 $ $PATH_TO/igluctl lint ./src/meltano/core/tracking
OK: com.meltano/cli_context/jsonschema/1-0-0
OK: com.meltano/environment_context/jsonschema/1-0-0
OK: com.meltano/plugins_context/jsonschema/1-0-0
OK: com.meltano/project_context/jsonschema/1-0-0
TOTAL: 4 valid schemas
TOTAL: 0 schemas didn't pass validation
```

See https://www.iglooanalytics.com/blog/understanding-snowplow-analytics-custom-contexts.html for more information.

When a new version of the schema is introduced , it must also be updated in our schema registry,
SnowcatCloud.

Login to https://app.snowcatcloud.com/ using your Meltano email address. Request permissions from
an account admin if necessary. As of the time of writing this, the admins are:

- pat@meltano.com
- will@meltano.com
- edgar@meltano.com
- taylor@meltano.com
- florian@meltano.com

Once SnowcatCloud provides an API to update the schemas, we should add a CI job to update them
automatically when a release pipeline is run with changes in this directory.
