#!/bin/bash

set -euxo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
pushd "$SCRIPT_DIR/../" > /dev/null

pushd src/webapp > /dev/null
yarn
yarn build
popd

mkdir -p src/meltano/api/templates
cp src/webapp/dist/index.html src/meltano/api/templates/webapp.html
cp src/webapp/dist/index-embed.html src/meltano/api/templates/embed.html
cp -r src/webapp/dist/static/. src/meltano/api/static
