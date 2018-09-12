CREATE TABLE IF NOT EXISTS telegram_user (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT
);

CREATE TABLE IF NOT EXISTS telegram_chat (
    chat_id INTEGER PRIMARY KEY,
    chat_name TEXT
);

CREATE TABLE IF NOT EXISTS user_in_chat (
    id SERIAL PRIMARY KEY, -- TODO: should user_id, chat_id be the primary keys instead?  -- No
    user_id INTEGER REFERENCES telegram_user(user_id),
    chat_id INTEGER REFERENCES telegram_chat(chat_id),
    karma integer
);

CREATE TABLE IF NOT EXISTS telegram_message (
    message_id INTEGER PRIMARY KEY,
    chat_id INTEGER REFERENCES telegram_chat(chat_id),
    author_user_in_chat_id INTEGER REFERENCES user_in_chat(id),
    message_text TEXT

);

CREATE TABLE IF NOT EXISTS user_reacted_to_message (
    id SERIAL PRIMARY KEY,
    --TODO: should I use user_id or user_in_chat_id?
    --user_id INTEGER REFERENCES user_in_chat(user_id),
    user_in_chat_id INTEGER REFERENCES user_in_chat(id),
    message_id INTEGER REFERENCES telegram_message(message_id),
    react_score INTEGER, --"1" if +1, "-1" if -1,
    react_text TEXT
);
