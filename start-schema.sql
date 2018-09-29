
CREATE TABLE IF NOT EXISTS telegram_user ( -- use IF NOT EXISTS to not error if they table does exist
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT
);
CREATE INDEX IF NOT EXISTS index_telegram_user_on_username
  on telegram_user(username);

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
CREATE UNIQUE INDEX IF NOT EXISTS index_user_in_chat_on_chat_id_usr_id
  on user_in_chat(chat_id, user_id);

CREATE TABLE IF NOT EXISTS telegram_message (
    message_id INTEGER PRIMARY KEY,
    chat_id TEXT REFERENCES telegram_chat(chat_id),
    author_user_id INTEGER REFERENCES telegram_user(user_id),
    message_text TEXT,
    message_time TIMESTAMP default current_timestamp
);
CREATE INDEX IF NOT EXISTS index_telegram_message_on_author_id
  on telegram_message(author_user_id);
CREATE INDEX IF NOT EXISTS index_telegram_message_on_chat_id
  on telegram_message(chat_id);


CREATE TABLE IF NOT EXISTS user_reacted_to_message (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES telegram_user(user_id),
    message_id INTEGER REFERENCES telegram_message(message_id),
    react_score INTEGER, --"1" if +1, "-1" if -1,
    react_message_id INTEGER
);
CREATE INDEX IF NOT EXISTS index_user_reacted_to_message_on_user_id_message_id_react_message_id
  on user_reacted_to_message(message_id, react_message_id, user_id);

-- use trigger to check banned used before allowing user_in_chat to be modified
-- soon maybe sum should be used for all karma
/* CREATE TABLE banned_users (
) */

create table IF NOT EXISTS command_used (
    id SERIAL PRIMARY KEY,
    command TEXT, --actual command used
    arguments TEXT,
    chat_id TEXT REFERENCES Telegram_chat(chat_id), -- chat used in
    user_id int REFERENCES Telegram_user(user_id), --user who used the command
    used_time TIMESTAMP default current_timestamp, --time they used the command
    program_version TEXT
);

CREATE TABLE IF NOT EXISTS witty_responses(
    response TEXT PRIMARY KEY
);