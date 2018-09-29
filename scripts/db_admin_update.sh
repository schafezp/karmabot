#!/bin/sh

#Changes Witty Responses according to witty_respones.csv
#Note: Does /NOT/ update Postgres database.

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 ENV_VARS_FILENAME" >&2
    exit 1
fi
env_vars_filename=$1

export $(grep -v '^#' ${env_vars_filename} | xargs)
python src/setup_db_rows.py
unset $(grep -v '^#' ${env_vars_filename} | xargs)