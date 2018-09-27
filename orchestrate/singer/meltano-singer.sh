#!/bin/bash

TAP="tap-$1"
TARGET="target-$2"
RUN_DIR=$SINGER_RUN_DIR # from Dockerfile

TAP_OVERRIDE_DIR="$CI_PROJECT_DIR/extract/$TAP"
TARGET_OVERRIDE_DIR="$CI_PROJECT_DIR/load/$TARGET"
STATE_FILE="$RUN_DIR/state.json"

TAP_PATH="/venvs/$TAP/bin/$TAP"
TARGET_PATH="/venvs/$TARGET/bin/$TARGET"

usage() {
    echo "meltano-singer.sh <tap> <target>"
}

prepare() {
    ln -sf /etc/singer/tap/$TAP.properties.json $RUN_DIR/tap.properties.json
    envsubst < /etc/singer/tap/$TAP.config.json > $RUN_DIR/tap.config.json
    envsubst < /etc/singer/target/$TARGET.config.json > $RUN_DIR/target.config.json
}

run() {
    TAP_ARGS=""
    TAP_ARGS+=" -c $RUN_DIR/tap.config.json"
    TAP_ARGS+=" --catalog $RUN_DIR/tap.properties.json"
    [[ -s "$STATE_FILE" ]] && { TAP_ARGS+=" --state=$STATE_FILE"; }

    INVOKE_TAP="$TAP_PATH $TAP_ARGS"

    TARGET_ARGS=""
    TARGET_ARGS+=" -c $RUN_DIR/target.config.json"
    INVOKE_TARGET="$TARGET_PATH $TARGET_ARGS"

    exec $INVOKE_TAP | $INVOKE_TARGET > $RUN_DIR/next_state.json

    if [[ PIPESTATUS[0] && PIPESTATUS[1] ]]; then
        bookmark
    else
        echo "The pipeline failed:"
        echo "\ttap exited with $PIPESTATUS[0]"
        echo "\ttarget exited with $PIPESTATUS[1]"
    fi
}

bookmark() {
    NEXT_STATE_FILE=$RUN_DIR/next_state.json

    if [[ ! -s $NEXT_STATE_FILE ]]; then
        return
    fi

    if [[ -s $STATE_FILE ]]; then
        echo "Updating the bookmark file, changes are:"
        diff $NEXT_STATE_FILE $STATE_FILE
    fi

    mv $NEXT_STATE_FILE $STATE_FILE
}

if [[ $# != 2 || $1 = "--help" ]]; then
    usage
    exit 0
fi

if [[ ! -x "$TAP_PATH" ]]; then
    echo "$TAP not found, aborting."
    exit 1
fi

if [[ ! -x "$TARGET_PATH" ]]; then
    echo "$TARGET not found, aborting."
    exit 1
fi

prepare
run
