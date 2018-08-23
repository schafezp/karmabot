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
    karma integer,
    upvotes integer,
    downvotes integer
);

-- example data can be dumped in to the db when testing
INSERT INTO telegram_user VALUES (6012310, '@facade','zach','schafer');
INSERT INTO telegram_user VALUES (3042023, '@weldon','luke','weldon');
INSERT INTO telegram_user VALUES (9019282, '@notthemessiah','walt','panfil');

INSERT INTO telegram_chat VALUES (23423, 'friend group chat');
INSERT INTO telegram_chat VALUES (91235, 'school work group chat');

INSERT INTO user_in_chat (user_id, chat_id, karma) VALUES (6012310, 23423, 5);
INSERT INTO user_in_chat (user_id, chat_id, karma) VALUES (9019282, 23423, 7);
INSERT INTO user_in_chat (user_id, chat_id, karma) VALUES (3042023, 23423, 10);
INSERT INTO user_in_chat (user_id, chat_id, karma) VALUES (6012310, 91235, 5);



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

-- stored procedure to modify the karma of a particular user in a particular chat
CREATE FUNCTION change_karma_from_user_to_user (from_user_id INTEGER, to_user_id INTEGER, chat_id INTEGER, change_value INTEGER)
RETURNS INTEGER
BEGIN
--- logic
    UPDATE user_in_chat uic
    SET karma = karma + change_value
    WHERE user_id=to_user_id;

END;
LANGUAGE PLPGSQL;


change_karma_from_user_to_user ( )