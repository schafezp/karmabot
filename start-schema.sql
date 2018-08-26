CREATE TABLE IF NOT EXISTS telegram_user ( -- use IF NOT EXISTS to not error if they table does exist
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT
);

CREATE TABLE IF NOT EXISTS telegram_chat (
    chat_id TEXT PRIMARY KEY,
    chat_name TEXT 
);

CREATE TABLE IF NOT EXISTS user_in_chat (
    user_id INTEGER REFERENCES telegram_user(user_id),
    chat_id TEXT REFERENCES telegram_chat(chat_id),
    karma integer,
    PRIMARY KEY (user_id,chat_id)
);

CREATE TABLE IF NOT EXISTS telegram_message (
    message_id INTEGER PRIMARY KEY,
    chat_id TEXT REFERENCES telegram_chat(chat_id),
    author_user_id INTEGER REFERENCES telegram_user(user_id),
    message_text TEXT  
);

CREATE TABLE IF NOT EXISTS user_reacted_to_message (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES telegram_user(user_id),
    message_id INTEGER REFERENCES telegram_message(message_id),
    react_score INTEGER, --"1" if +1, "-1" if -1,
    react_message_id INTEGER
);