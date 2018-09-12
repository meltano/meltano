#!/usr/bin/env bash

set -e

echo '{"Makefile": {"name": "makefile", "symbol": "#"}}' > /tmp/languages.json
npm i -g docco http-server
docco -L /tmp/languages.json -o /tmp/docs /app/Makefile
cp /tmp/docs/app/Makefile.html /tmp/docs/index.html
http-server /tmp/docs -p 8081
