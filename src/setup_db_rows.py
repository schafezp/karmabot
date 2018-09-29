"""Inserts any rows neccesary to set up the database state.
Any tables are created in start-schema.sql but this is for setting up initial state"""
import csv
import sys
from utils import check_env_vars_all_loaded, attempt_connect

def main():
    """Load custom user info into the database"""
    required_env_vars = ["POSTGRES_HOSTNAME", "POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASS"]
    (did_load, var_failed) = check_env_vars_all_loaded(required_env_vars)
    if not did_load:
        print(f"Failed to load {var_failed}")
        sys.exit(1)
    conn = attempt_connect()

    #insert witty responses
    print("Start loading witty responses")
    with conn:
        with conn.cursor() as crs:
            with open("witty_responses.csv", "r") as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    cmd = """INSERT INTO witty_responses VALUES (%s) ON CONFLICT DO NOTHING"""
                    crs.execute(cmd, [row['response']])
    print("Finish loading witty responses")


if __name__ == '__main__':
    main()
