#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
docker run -p 4000:4000 -v "${SCRIPT_DIR}/../docs:/site" bretfisher/jekyll-serve
