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
    witty_responses_filename = "witty_responses.csv"
    with conn:
        with conn.cursor() as crs:
            #use truncate to empty table. Allows user to use custom 
            delete_existing_reponses_cmd = "TRUNCATE TABLE witty_responses" 
            print("Delete existing witty responses")
            print(f"Start loading witty responses from {witty_responses_filename}")
            crs.execute(delete_existing_reponses_cmd, [])
            conn.commit()
            with open(witty_responses_filename, "r") as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    insert_cmd = """INSERT INTO witty_responses VALUES (%s) ON CONFLICT DO NOTHING"""
                    crs.execute(insert_cmd, [row['response']])
    print("Finish loading witty responses")


if __name__ == '__main__':
    main()
