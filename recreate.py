
def recreate_db():
    droptables = ["DROP TABLE IF EXISTS telegram_user CASCADE;",
"DROP TABLE IF EXISTS telegram_chat CASCADE;",
"DROP TABLE IF EXISTS user_in_chat CASCADE;",
"DROP TABLE IF EXISTS telegram_message CASCADE;",
"DROP TABLE IF EXISTS user_reacted_to_message CASCADE; "]

    """ for cmd in droptables:
        cursor.execute(cmd)
    conn.commit() """

    tables = ["""CREATE TABLE IF NOT EXISTS telegram_user ( 
    user_id INTEGER PRIMARY KEY, username TEXT, wfirst_name TEXT,
    last_name TEXT); """, """CREATE TABLE IF NOT EXISTS telegram_chat (
    chat_id INTEGER PRIMARY KEY,
    chat_name TEXT );""",
    """CREATE TABLE IF NOT EXISTS user_in_chat (
    id SERIAL PRIMARY KEY, -- TODO: should user_id, chat_id be the primary keys instead?
    user_id INTEGER REFERENCES telegram_user(user_id),
    chat_id INTEGER REFERENCES telegram_chat(chat_id),
    karma integer);""", """CREATE TABLE IF NOT EXISTS telegram_message (
    message_id INTEGER PRIMARY KEY,
    chat_id INTEGER REFERENCES telegram_chat(chat_id),
    author_user_in_chat_id INTEGER REFERENCES user_in_chat(id),
    message_text TEXT); """,
"""CREATE TABLE IF NOT EXISTS user_reacted_to_message (
    id SERIAL PRIMARY KEY,
    user_in_chat_id INTEGER REFERENCES user_in_chat(id),
    message_id INTEGER REFERENCES telegram_message(message_id), react_score INTEGER,
    react_text TEXT); """
    ]
    """ for table in tables:
        cursor.execute(table)
        conn.commit() """

    #alternative way to load schema commands
    """ schema = open("start-schema.pgsql","r").read()
    print(cursor.execute(schema))

    conn.commit() """