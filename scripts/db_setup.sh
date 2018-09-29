#!/bin/sh

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 ENV_VARS_FILENAME" >&2
    exit 1
fi
env_vars_filename=$1

#https://stackoverflow.com/questions/19331497/set-environment-variables-from-file
#set env vars from file
export $(grep -v '^#' ${env_vars_filename} | xargs)
python src/setup_db_rows.py
unset $(grep -v '^#' ${env_vars_filename} | xargs)