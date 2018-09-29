import os
import logging
import time
from typing import Tuple
import psycopg2

def attempt_connect(time_sleep=1,do_log=True):
    """ returns connection to postgres
    attempts to reconnect every time_sleep seconds"""
    conn = None
    while conn is None:
        try:
            HOST = os.environ.get("POSTGRES_HOSTNAME")
            DATABASE = os.environ.get("POSTGRES_DB")
            USER = os.environ.get("POSTGRES_USER")
            PASSWORD = os.environ.get("POSTGRES_PASS")
            conn = psycopg2.connect(
                host=HOST,
                database=DATABASE,
                user=USER,
                password=PASSWORD)
            return conn
        except psycopg2.OperationalError as oe:
            if do_log:
                logging.info(oe)
            time.sleep(time_sleep)
    return conn



def check_env_vars_all_loaded(env_vars,
                              do_log=True
                             ) -> Tuple[bool, str]:
    """Checks required environment variables and returns false if required env vars are not set
    """

    if do_log:
        logging.info("Environment Variables:")
    for var in env_vars:
        val = os.environ.get(var)
        if val is None or val == '':
            if do_log:
                logging.info(f"Variable: {var} Value: VALUE MISSING. EXITING")
            return (False, var)
        else:
            if do_log:
                logging.info(f"Variable: {var} Value: {val}")

    #TODO: return sensical second option; consider Optional[str]
    return (True, "All Env vars loaded")