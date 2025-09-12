# Meltano Invoker Manifest

This example tests that PluginInvoker correctly uses manifest for environment variable resolution.

First, let's set up a project with environment variables:

```shell
meltano add extractor tap-gitlab
```

Configure some environment variables:

```shell
meltano config tap-gitlab set projects "meltano/meltano"
```

Test without manifest (should auto-compile):

```shell
rm -rf .meltano/manifests
meltano invoke tap-gitlab --help
```

Verify manifest was created:

```shell
ls .meltano/manifests/meltano-manifest.json
```

Now test with environment:

```shell
meltano --environment=dev compile
meltano --environment=dev invoke tap-gitlab --help
```
