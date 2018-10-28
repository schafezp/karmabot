"""This is for loading user defined content into the database
Currently allows users to modify the response given when a user attempts to +1 themselves"""
import csv
import sys
from .customutils import attempt_connect, check_env_vars_all_loaded

def main():
    """Load custom user info into the database"""
    required_env_vars = ["POSTGRES_HOSTNAME", "POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASS"]
    (did_load, var_failed) = check_env_vars_all_loaded(required_env_vars)
    if not did_load:
        print(f"Failed to load {var_failed}")
        sys.exit(1)
    conn = attempt_connect()

    #insert witty responses
    witty_responses_filename = "attempted_self_plus_one_response.csv"
    self_plus_one_table_name = "attempted_self_plus_one_response"
    with conn:
        with conn.cursor() as crs:
            #use truncate to empty table. Allows user to use custom
            delete_existing_reponses_cmd = f"TRUNCATE TABLE {self_plus_one_table_name}"
            print("Delete existing self plus one responses")
            print(f"Start loading responses from {witty_responses_filename}")
            crs.execute(delete_existing_reponses_cmd, [])
            conn.commit()
            with open(witty_responses_filename, "r") as csv_file:
                reader = csv.DictReader(csv_file, delimiter="\t")
                for row in reader:
                    insert_cmd = f"""INSERT INTO {self_plus_one_table_name} VALUES (%s) ON CONFLICT DO NOTHING"""
                    crs.execute(insert_cmd, [row['response']])
    print("Finish loading responses")


if __name__ == '__main__':
    main()
