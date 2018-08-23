/* script written in idempotent manner */


-- delete the tables if they already exist
DROP TABLE IF EXISTS telegram_user CASCADE; -- CASCADE means delete rows if they exist
DROP TABLE IF EXISTS telegram_chat CASCADE;
DROP TABLE IF EXISTS user_in_chat CASCADE;

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
    author_user_id INTEGER REFERENCES telegram_user(user_id),
    message_text TEXT
    
);

CREATE TABLE IF NOT EXISTS user_reacted_to_message (
    id SERIAL PRIMARY KEY,
    --user_id INTEGER REFERENCES user_in_chat(user_id),
    user_in_chat_id INTEGER REFERENCES user_in_chat(id),
    message_id INTEGER REFERENCES telegram_message(message_id),
    react_score INTEGER --"1" if +1, "-1" if -1
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

INSERT INTO telegram_message VALUES (17,23423, 9019282, 'hello this is a message from walt');

INSERT INTO  user_reacted_to_message (user_in_chat_id,message_id, react_score) VALUES (0,17 ,1);
INSERT INTO  user_reacted_to_message (user_in_chat_id,message_id, react_score) VALUES (1,17,-1);



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





-- stuff below this is to TODO


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


change_karma_from_user_to_user(6012310,3042023,23423,-1);

val := change_karma_from_user_to_user(6012310,3042023,23423,1);
raise notice 'Value: %', val;
