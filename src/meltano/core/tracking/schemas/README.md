When a JSON file in this directory is updated, it must also be updated in our schema registry,
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
