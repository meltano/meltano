#!/usr/bin/env bash
meltano add extractor tap-mock
meltano config tap-mock set api_key "config_value"
rm -rf .meltano/manifests
meltano invoke tap-mock --help
ls .meltano/manifests/meltano-manifest.json
meltano --environment=dev compile
meltano --environment=dev invoke tap-mock --help
