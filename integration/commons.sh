#!/usr/bin/env bash

inject_logging_yaml(){
  TARGET_DIR=$1
  if [ ! -d "$TARGET_DIR" ]; then
    echo "Target directory $TARGET_DIR does not exist"
    exit 1
  fi
  cp logging.yml "$TARGET_DIR"/logging.yml
}

compile_script(){
  SOURCE_FILE=$1
  OUTPUT_SCRIPT=$2
  if [ ! -f "$SOURCE_FILE" ]; then
    echo "Source file $SOURCE_FILE does not exist"
    exit 1
  fi
  mdsh -c  "$SOURCE_FILE" > "$OUTPUT_SCRIPT"
}

check_meltano_yaml(){
  SOURCE_FILE=$1
  TARGET_FILE=$2
  if [ ! -f "$SOURCE_FILE" ]; then
    echo "Source file $SOURCE_FILE does not exist"
    exit 1
  fi
  if [ ! -f "$TARGET_FILE" ]; then
    echo "Target file $TARGET_FILE does not exist"
    exit 1
  fi
  diff -q "$SOURCE_FILE" "$TARGET_FILE"
}
