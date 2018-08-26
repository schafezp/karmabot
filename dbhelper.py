from user import User, User_in_chat, Telegram_chat, Telegram_message

def get_user_by_user_id(user_id: int, conn) -> User:
    with conn:
        with conn.cursor() as crs: #I would love type hints here but psycopg2.cursor isn't a defined class
            selectcmd = "SELECT user_id, username, first_name, last_name from telegram_user tu where tu.user_id=%s"
            crs.execute(selectcmd, [user_id])
            res = crs.fetchone()
            return User(res[0],res[1],res[2],res[3])

def save_or_create_user(user : User,conn) -> User:
    with conn:
        with conn.cursor() as crs: #I would love type hints here but psycopg2.cursor isn't a defined class
            selectcmd = "SELECT user_id, username, first_name, last_name from telegram_user tu where tu.user_id=%s"
            #TODO: upsert to update values otherwise username, firstname, lastname wont ever change
            #print("user with id: " + str(user_id) + "  not found: creating user")
            insertcmd = """INSERT into telegram_user 
            (user_id, username, first_name, last_name) VALUES (%s,%s,%s,%s)
            ON CONFLICT (user_id) DO UPDATE 
            SET username = EXCLUDED.username, 
            first_name = EXCLUDED.first_name,
            last_name = EXCLUDED.last_name
            """
            crs.execute(insertcmd,[user.get_user_id(),user.get_username(),user.get_first_name(),user.get_last_name()])
            conn.commit()
            crs.execute(selectcmd,[user.get_user_id()])
            (user_id, username, first_name, last_name) = crs.fetchone()
            return User(user_id,username,first_name,last_name)
def does_chat_exist(chat_id: int, conn):
    with conn:
        with conn.cursor() as crs: #I would love type hints here but psycopg2.cursor isn't a defined class
            selectcmd = "SELECT chat_id, chat_name FROM telegram_chat tc where tc.chat_id=%s"
            crs.execute(selectcmd,[chat_id])
            return crs.fetchone() is not None
def save_or_create_chat(chat: Telegram_chat, conn):
    with conn:
        with conn.cursor() as crs: #I would love type hints here but psycopg2.cursor isn't a defined class
            """ selectcmd = "SELECT chat_id, chat_name FROM telegram_chat tc where tc.chat_id=%s"
            crs.execute(selectcmd, [chat_id, chat_name])
            result = crs.fetchone() """
            insertcmd = """INSERT into telegram_chat 
            (chat_id, chat_name) VALUES (%s,%s)
            ON CONFLICT (chat_id) DO UPDATE 
            SET chat_name = EXCLUDED.chat_name
            """
            crs.execute(insertcmd, [chat.chat_id, chat.chat_name])
            conn.commit()


#if user did not have a karma before, karma will be set to change_karma
def save_or_create_user_in_chat(user: User, chat_id: int, conn, change_karma=0) -> User_in_chat:
    with conn:
        with conn.cursor() as crs: #I would love type hints here but psycopg2.cursor isn't a defined class
            #TODO: instead of select first, do insert and then trap exception if primary key exists
            selectcmd = "SELECT user_id, chat_id, karma FROM user_in_chat uic where uic.user_id=%s AND uic.chat_id=%s"
            crs.execute(selectcmd,[user.get_user_id(), chat_id,])

            result = crs.fetchone()

            insertcmd_karma = """INSERT into user_in_chat 
                (user_id, chat_id, karma) VALUES (%s,%s,%s)
                ON CONFLICT (user_id,chat_id) DO UPDATE SET karma = user_in_chat.karma + %s
                RETURNING karma 
                """
            
            #TODO: used named parameters instead of %s to not have to repeat these params
            crs.execute(insertcmd_karma,
            [user.get_user_id(),chat_id, change_karma,change_karma])
            
            row = crs.fetchone()
            print(row)
            conn.commit()
            karma = row[0]
            return User_in_chat(user.id,chat_id,karma)



#message tg.Message
def user_reply_to_message(user: User,reply_user: User, chat: Telegram_chat , original_message : Telegram_message, reply_message : Telegram_message, karma : int, conn):
    user: User = save_or_create_user(user,conn)
    user2: User = save_or_create_user(reply_user,conn)
    if not does_chat_exist(chat.chat_id,conn):
        save_or_create_chat(chat, conn)


    
    uic: User_in_chat = save_or_create_user_in_chat(user, chat.chat_id, conn)
    uic2: User_in_chat = save_or_create_user_in_chat(user2, chat.chat_id, conn)
    print("uic user_id: "+ str(uic.user_id))
    print("uic2 user_id: "+ str(uic2.user_id))
    #apply karma to message author
    if(karma == 1 or karma == -1):
        save_or_create_user_in_chat(user2,chat.chat_id, conn, change_karma=karma)
    else:
        print("invalid karma number")
    insert_message = """INSERT INTO telegram_message 
    (message_id,chat_id, author_user_id, message_text) 
    VALUES (%s,%s,%s,%s)
    ON CONFLICT (message_id) DO UPDATE
    SET message_text = EXCLUDED.message_text;
    """
    selecturtm = """SELECT * from user_reacted_to_message urtm where urtm.user_id=%s and urtm.message_id=%s and urtm.react_message_id=%s"""
    inserturtm = """INSERT INTO user_reacted_to_message 
    (user_id,message_id,react_score,react_message_id)
    VALUES (%s,%s,%s,%s)"""
    with conn:
        with conn.cursor() as crs:
            args_reply_message = [reply_message.message_id, chat.chat_id, uic.user_id, reply_message.message_text]
            args_original_message = [original_message.message_id, chat.chat_id, original_message.author_user_id, original_message.message_text]
            crs.execute(insert_message,args_reply_message)
            crs.execute(insert_message,args_original_message)
            # check if urtm doesn't exist #(primary key should do this part...)
            args_select_urtm = [uic.user_id, original_message.message_id, reply_message.message_id]
            crs.execute(selecturtm,args_select_urtm)
            if crs.fetchone() is None:
                argsurtm = [uic.user_id, original_message.message_id, karma, reply_message.message_id]
                crs.execute(inserturtm,argsurtm)
            
def get_karma_for_users_in_chat(chat_id: int,conn):
    cmd = """select username, karma from user_in_chat uic
        LEFT JOIN telegram_user tu ON uic.user_id=tu.user_id
        where uic.chat_id=%s;"""
    with conn:
        with conn.cursor() as crs:
            crs.execute(cmd,[chat_id])
            return crs.fetchall()


def get_message_responses_for_user_in_chat(user_id: int, chat_id: int,conn):
    cmd = """    SELECT sub3.user_id, sub3.message_id, sub3.response_text AS message_text, urtm.react_score, 
        urtm.react_message_id, sub3.username AS responder_username, sub3.first_name AS responder_first_name,
         sub3.last_name AS responder_last_name  FROM (
        SELECT  sub2.user_id, tm.message_id, tm.message_text AS response_text,  uic_id ,
            sub2.username, sub2.first_name, sub2.last_name FROM (
            SELECT uic_id, sub.user_id, sub.karma, tu.username, tu.first_name, tu.last_name FROM (
                SELECT id AS uic_id, a.user_id, chat_id, karma FROM (
                    select * from user_in_chat uic where uic.user_id = %s AND uic.chat_id=%s
                    ) as a
            ) AS sub
            LEFT JOIN telegram_user tu ON tu.user_id=sub.user_id) AS sub2
        LEFT JOIN telegram_message tm ON uic_id=tm.author_user_in_chat_id) AS sub3
    LEFT JOIN user_reacted_to_message urtm ON urtm.message_id = sub3.message_id;"""
    with conn:
        with conn.cursor() as crs:
            crs.execute(cmd,[user_id,chat_id])
            return crs.fetchall()