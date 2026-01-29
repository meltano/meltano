#!/bin/bash

function init {
    rm -rdf ./profiles
    rm -rdf ./logs
    mkdir ./profiles
    mkdir ./logs
}

function cleanup {
    rm -rdf dist
    rm -rdf .venv
    rm -rdf ./project/.meltano/
    rm -rdf ./project/output/warehouse.duckdb
}

function prepare {
    uv venv -p 3.10
    echo "Installing $1 into a virtualenv..."
    VIRTUAL_ENV=.venv uv pip install "$1"
    .venv/bin/meltano --version
    .venv/bin/meltano --cwd ./project install
}

function run {
    meltano_run=".venv/bin/meltano --cwd ./project run --refresh-catalog tap-mysql target-duckdb"
    echo "Profiling command $meltano_run"
    NO_COLOR=1 sudo sh -c "umask 0002 && py-spy record -o ./profiles/profile-$1.svg -- $meltano_run 2> ./logs/logs-$1.txt"
}

init

# EXAMPLE: check a specific commit
# https://github.com/meltano/meltano/commit/43bba8c9859a9f679d61716e98a3d5b753815f9d
# cleanup
# prepare 'meltano @ git+https://github.com/meltano/meltano.git@43bba8c9859a9f679d61716e98a3d5b753815f9d'
# run 43bba8c9859a9f679d61716e98a3d5b753815f9d

# v3.6.0
cleanup
prepare 'meltano==3.6.0'
run v3.6

# v3.7.9
cleanup
prepare 'meltano==3.7.9'
run v3.7

# v4.0.8
cleanup
prepare 'meltano==4.0.8'
run v4.0.8

# HEAD
cleanup
prepare 'meltano @ ../'
run latest
