DROP TABLE IF EXISTS telegram_user CASCADE; -- CASCADE means delete rows if they exist
DROP TABLE IF EXISTS telegram_chat CASCADE;
DROP TABLE IF EXISTS user_in_chat CASCADE;
DROP TABLE IF EXISTS telegram_message CASCADE;
DROP TABLE IF EXISTS user_reacted_to_message CASCADE;

CREATE TABLE IF NOT EXISTS telegram_user ( -- use IF NOT EXISTS to not error if they table does exist
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
    user_id INTEGER REFERENCES telegram_user(user_id),
    chat_id INTEGER REFERENCES telegram_chat(chat_id),
    karma integer,
    PRIMARY KEY (user_id,chat_id)
);

CREATE TABLE IF NOT EXISTS telegram_message (
    message_id INTEGER PRIMARY KEY,
    chat_id INTEGER REFERENCES telegram_chat(chat_id),
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


INSERT INTO telegram_user VALUES (6012310, '@thing','zach','schafer');
INSERT INTO telegram_user VALUES (3042023, '@man','luke','weldon');
INSERT INTO telegram_user VALUES (9019282, '@dude','walt','panfil');

INSERT INTO telegram_chat VALUES (23423, 'friend group chat');
INSERT INTO telegram_chat VALUES (91235, 'school work group chat');

INSERT INTO user_in_chat (user_id, chat_id, karma)
VALUES (6012310, 23423, 5);
INSERT INTO user_in_chat (user_id, chat_id, karma)
VALUES (9019282, 23423, 7);
INSERT INTO user_in_chat (user_id, chat_id, karma) 
VALUES (3042023, 23423, 10);
INSERT INTO user_in_chat (user_id, chat_id, karma) 
VALUES (6012310, 91235, 2);

INSERT INTO telegram_message VALUES (17,23423, 9019282, 'hello this is a message from walt');
INSERT INTO telegram_message VALUES (19,23423, 6012310, 'i am zach responding to walt ');
INSERT INTO telegram_message VALUES (21,23423, 9019282, 'i am luke responding to walt ');

INSERT INTO  user_reacted_to_message (user_id,message_id, react_score, react_message_id)
 VALUES (6012310,17 ,1,19);
INSERT INTO  user_reacted_to_message (user_id,message_id, react_score, react_message_id)
 VALUES (9019282,17 ,1,21);

/* INSERT INTO  user_reacted_to_message (user_in_chat_id,message_id, react_score, react_message_id)
 VALUES (1,17 ,1,'cool');
INSERT INTO  user_reacted_to_message (user_in_chat_id,message_id, react_score, react_text)
 VALUES (2,17,-1, 'eww');
INSERT INTO  user_reacted_to_message (user_in_chat_id,message_id, react_score, react_text)
 VALUES (1,23 ,1,'righton');
INSERT INTO  user_reacted_to_message (user_in_chat_id,message_id, react_score, react_text)
 VALUES (2,23,1,'neat'); */


/* to show karma in chat */

select username, karma from user_in_chat uic
LEFT JOIN telegram_user tu ON uic.user_id=tu.user_id
where uic.chat_id=23423;