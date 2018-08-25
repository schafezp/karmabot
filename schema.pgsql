/* script written in idempotent manner */


-- delete the tables if they already exist
DROP TABLE IF EXISTS telegram_user CASCADE; -- CASCADE means delete rows if they exist
DROP TABLE IF EXISTS telegram_chat CASCADE;
DROP TABLE IF EXISTS user_in_chat CASCADE;
DROP TABLE IF EXISTS telegram_message CASCADE;
DROP TABLE IF EXISTS user_reacted_to_message CASCADE;


-- create tables

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
    id SERIAL PRIMARY KEY, -- TODO: should user_id, chat_id be the primary keys instead?
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

-- example data can be dumped in to the db when testing
INSERT INTO telegram_user VALUES (6012310, '@facade','zach','schafer');
INSERT INTO telegram_user VALUES (3042023, '@weldon','luke','weldon');
INSERT INTO telegram_user VALUES (9019282, '@notthemessiah','walt','panfil');

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

INSERT INTO telegram_message VALUES (17,23423, 3, 'hello this is a message from walt');
INSERT INTO telegram_message VALUES (23,23423, 3, 'hello this is a different message from walt');
INSERT INTO telegram_message VALUES (25,23423, 1, 'zach: wolves are cool');


INSERT INTO  user_reacted_to_message (user_in_chat_id,message_id, react_score, react_text)
 VALUES (1,17 ,1,'cool');
INSERT INTO  user_reacted_to_message (user_in_chat_id,message_id, react_score, react_text)
 VALUES (2,17,-1, 'eww');
INSERT INTO  user_reacted_to_message (user_in_chat_id,message_id, react_score, react_text)
 VALUES (1,23 ,1,'righton');
INSERT INTO  user_reacted_to_message (user_in_chat_id,message_id, react_score, react_text)
 VALUES (2,23,1,'neat');

 INSERT INTO  user_reacted_to_message (user_in_chat_id,message_id, react_score, react_text)
 VALUES (2,25,1, 'i agree with zach');



DROP FUNCTION IF EXISTS show_users_in_chat;
-- only shows users who have karma
CREATE FUNCTION show_users_in_chat (chat_id_arg INTEGER)
RETURNS TABLE ( -- define the return schema
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    chat_name TEXT,
    karma INTEGER
) AS $$
    BEGIN
    RETURN QUERY -- this means return results of running a query
    SELECT telegram_username, fn, ln, tc.chat_name, karma_points
      from
    (SELECT tu.username as telegram_username, tu.first_name as fn, tu.last_name as ln
    , uic.chat_id as cid, uic.karma as karma_points
    FROM user_in_chat uic 
    LEFT JOIN telegram_user tu on uic.user_id=tu.user_id
    WHERE uic.chat_id=chat_id_arg) AS foo
    LEFT JOIN telegram_chat tc on tc.chat_id=cid
    ORDER BY karma_points DESC;
 END;
$$
LANGUAGE 'plpgsql';


-- This stored procedure creates the following table
select * from show_users_in_chat(23423);

/* database=# select * from show_users_in_chat(23423);
    username    | first_name | last_name | chat_id |     chat_name     | karma
----------------+------------+-----------+---------+-------------------+-------
 @weldon        | luke       | weldon    |   23423 | friend group chat |    10
 @notthemessiah | walt       | panfil    |   23423 | friend group chat |     7
 @facade        | zach       | schafer   |   23423 | friend group chat |     5 */



DROP FUNCTION IF EXISTS show_responses_to_message;
CREATE FUNCTION show_responses_to_message (message_id_arg INTEGER) 
RETURNS TABLE (
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    react_score INTEGER,
    react_text TEXT
) AS $$
    BEGIN RETURN QUERY
        select tu.username, tu.first_name, tu.last_name, foo.react_score, foo.react_text FROM
            (select uic.user_id as uic_user_id, urtm.react_score, urtm.react_text, chat_id, urtm.message_id as message_id  from user_reacted_to_message urtm 
            LEFT JOIN user_in_chat uic on uic.id=urtm.user_in_chat_id
            where message_id=message_id_arg) as foo
        LEFT JOIN telegram_user tu ON tu.user_id = uic_user_id;
    END;
$$
Language 'plpgsql';

select * from show_responses_to_message(17);


-- stuff below this is to TODO

--message_id is the id of the message the user is replying to
--TODO: shouldnt be able to reply to a message you already replied to
--TODO: don't pass in author_id instead parse it from message id
DROP FUNCTION IF EXISTS user_reply_to_message;
CREATE FUNCTION user_reply_to_message
(user_id INTEGER, chat_id INTEGER, message_id INTEGER, author_id INTEGER,
 score INTEGER, reply TEXT, username TEXT, OUT user_in_chat_id INTEGER)
RETURNS INTEGER as $$
    BEGIN
    --DECLARE user_in_chat_id INTEGER;
    --todo convert user_id into user_in_chat

    --if there is not already a user_in_chat then create one
    IF  NOT EXISTS ( SELECT 1 from telegram_user tu where tu.id = user_id) THEN
        raise notice 'Create User: %', username;
        INSERT INTO telegram_user (user_id,username) VALUES (user_id,username);

    END IF;
    --if there is not a user_in_chat then create one
    IF  EXISTS ( SELECT 1 from user_in_chat uic where uic.user_id = user_id) THEN
        -- have to find user_in_chat.id
        SELECT * from user_in_chat uic
        where uic.user_id=user_id
        returning uic.id into user_in_chat_id;
        /* INSERT INTO user_reacted_to_message
        (user_in_chat_id, message_id, score, reply) VALUES (user_in_chat_id, message_id, score, reply); */
        
    ELSE    
    
    raise notice 'Create User in chat_id: %', chat_id;
        INSERT INTO user_in_chat (user_id,username) VALUES (user_id,username)
        RETURNING ID
        INTO user_in_chat_id;

    END IF;

    --TODO
    /* INSERT INTO user_reacted_to_message (user_in_chat_id, message_id, score, reply)
         VALUES (user_in_chat_id, message_id, score, reply);
    END; */
    
$$
Language 'plpgsql';

DROP FUNCTION IF EXISTS change_karma_from_user_to_user;
-- stored procedure to modify the karma of a particular user in a particular chat

--returns new karma value
CREATE FUNCTION change_karma_from_user_to_user (from_user_id INTEGER, to_user_id INTEGER, chat_id INTEGER, change_value INTEGER)
RETURNS INTEGER AS $$
BEGIN
    --TODO: check if this updated something and error if not
    UPDATE user_in_chat uic
    SET karma = karma + change_value
    WHERE user_id=to_user_id;

    IF abs(change_value) == change_value THEN --give positive karma
        UPDATE user_in_chat uic
        SET upvotes = upvotes + 1
        WHERE user_id=to_user_id;
    ELSE


    END IF

    UPDATE user_in_chat
    SET 
    RETURN 1;
END
$$
LANGUAGE PLPGSQL;


DROP FUNCTION IF EXISTS get_user_in_chat_from_user_id;
CREATE FUNCTION get_user_in_chat_from_user_id(user_id_arg INTEGER, chat_id_arg INTEGER)
RETURNS SETOF user_in_chat AS $$
    BEGIN 
    RETURN QUERY
    select * from user_in_chat uic where uic.user_id = user_id_arg AND uic.chat_id=chat_id_arg;
    END
$$
LANGUAGE plpgsql;

--select * from get_user_in_chat_from_user_id(6012310, 23423);

/* Gets all karma upvotes or downvotes with the message sent alongside*/
DROP FUNCTION get_message_responses_for_user_in_chat;
CREATE OR REPLACE FUNCTION get_message_responses_for_user_in_chat(user_id_arg INTEGER, chat_id_arg INTEGER) 
RETURNS TABLE(
    user_id INTEGER,
    message_id INTEGER,
    message_text TEXT,
    react_score INTEGER,
    react_text TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT sub2.user_id, sub2.message_id, sub2.response_text as message_text, urtm.react_score, urtm.react_text FROM
    (select sub.user_id, tm.message_id, tm.message_text as response_text,  uic_id from
    (select id as uic_id, get_user_in_chat_from_user_id.user_id, chat_id, karma from get_user_in_chat_from_user_id(user_id_arg,chat_id_arg)) as sub
    LEFT JOIN telegram_message tm ON uic_id=tm.author_user_in_chat_id) as sub2
    LEFT JOIN user_reacted_to_message urtm on urtm.message_id = sub2.message_id;
END
$$ LANGUAGE plpgsql;

select * from get_message_responses_for_user_in_chat(6012310, 23423);


/* TODO: update get_message_responses_for_user_in_chat to also return username, lastname, firstname*/
select  sub.user_id, tm.message_id, tm.message_text as response_text,  uic_id from (
select uic_id, sub.user_id, sub.karma, tu.username, tu.first_name, tu.last_name from (
    select id as uic_id, get_user_in_chat_from_user_id.user_id, chat_id, karma
    from get_user_in_chat_from_user_id(6012310, 23423)
) as sub
LEFT JOIN telegram_user tu on tu.user_id=sub.user_id) as sub2
LEFT JOIN telegram_message tm ON uic_id=tm.author_user_in_chat_id ;


/* change_karma_from_user_to_user(6012310,3042023,23423,-1);

val := change_karma_from_user_to_user(6012310,3042023,23423,1);
raise notice 'Value: %', val; */
