#!/bin/sh

env_vars_default='test_env_vars.sh'
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 ENV_VARS_FILENAME" >&2
    exit 1
fi
env_vars_filename=$1

#https://stackoverflow.com/questions/19331497/set-environment-variables-from-file
#set env vars from file
export $(grep -v '^#' ${env_vars_filename} | xargs)

docker-compose build && docker-compose up -d --no-deps && docker-compose logs bot
#unset variables at end to not pollute local space
unset $(grep -v '^#' ${env_vars_filename} | xargs)