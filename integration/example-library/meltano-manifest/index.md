# Meltano Manifest

This example demonstrates how a manifest can be generated manually using the `compile` command.


A manifest for a single environment can be compiled by specifying the environment as you would for any other Meltano command:

```shell
meltano --environment=prod compile
```


By default a manifest file for each environment is compiled:

```shell
meltano compile --indent 2
```


By default, secret values are redacted. These values can be kept unredacted with the `--unsafe` flag.

```shell
meltano --environment=jigsaw compile --indent 2 --unsafe
```
