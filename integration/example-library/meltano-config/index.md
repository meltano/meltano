# Manage Plugin Configuration

Using the CLI to configure the plugin.

## Setup

To begin, download or copy the [meltano.yml](/integration/example-library/meltano-config/meltano.yml) to an empty directory.

## Add a custom plugin

```shell
echo 'plugins:
  utilities:
  - name: example
    namespace: example
    settings:
    - name: a_string
    - name: an_integer
      kind: integer
    - name: an_object
      kind: object
    - name: an_array
      kind: array' >> meltano.yml
```

## Set plugin settings

```shell
meltano config example set a_string -- -86.75
meltano config example set an_integer '42'
meltano config example set an_object '{"foo": "bar"}'
meltano config example set an_array '["foo", "bar"]'
```

## Check plugin settings

```shell
meltano config example
```

You should see the following output:

```json
{
  "a_string": "-86.75",
  "an_integer": 42,
  "an_object": {
    "foo": "bar"
  },
  "an_object.foo": "bar",
  "an_array": [
    "foo",
    "bar"
  ]
}
```
