#!/bin/bash

if [[ -n "$MELTANO_PROJECT_INIT" ]]; then
    [[ -f "$MELTANO_PROJECT_INIT/meltano.yml" ]] || { meltano init "$MELTANO_PROJECT_INIT" --no_usage_stats; }
    cd "$MELTANO_PROJECT_INIT" || exit 1
    exec meltano "$@"
else
    exec meltano "$@"
fi
