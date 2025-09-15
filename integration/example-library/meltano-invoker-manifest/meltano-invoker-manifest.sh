#!/usr/bin/env bash
meltano add extractor tap-gitlab
meltano config set tap-gitlab projects meltano/meltano
rm -rf .meltano/manifests
meltano invoke tap-gitlab --help
ls .meltano/manifests/meltano-manifest.*.json
meltano --environment=dev compile
meltano --environment=dev invoke tap-gitlab --help
