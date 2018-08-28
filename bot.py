import logging
import os
import pickle
import random
import psycopg2 # postgresql python 

from telegram.ext import Filters, CommandHandler, MessageHandler, Updater
import telegram as tg
from typing import Dict, NewType, Tuple

from user import User, User_in_chat, Telegram_chat, Telegram_message,user_from_tg_user
from dbhelper import *

log_level = os.environ.get('LOGLEVEL')
level = None
if log_level == "debug":
    level=logging.DEBUG
elif log_level == "info":
    level=logging.INFO
else:
    level=logging.INFO

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=level)
logger = logging.getLogger(__name__)

version = '1.04' # TODO: make this automatic
changelog_url = 'https://schafezp.com/schafezp/txkarmabot/blob/master/CHANGELOG.md'

# TODO: obfuscate these
production_token = '613654042:AAHnLhu4TFC-xJ4IylkXdczX9ihnIgtqnI8'
test_token = '650879477:AAFO_o2_nt2gmwA-h0TeIo4bSqI-WLxp6VM'

is_production = os.environ.get('PROD') == "true"
logger.debug("Production? %s" % is_production)

updater = None
if is_production:
    updater = Updater(token=production_token)
else:
    updater = Updater(token=test_token)

dispatcher = updater.dispatcher






conn = None
import time
while conn is None:
    try:
        conn = psycopg2.connect(host="postgres", database="karmabot", user="test_user", password="test_pass")
    except psycopg2.OperationalError as oe:
        print(oe)
        time.sleep(1)

cursor = conn.cursor()





""" def get_user_by_reply_user(reply_user: tg.User, chat_id: int):
    logger.debug("Chat id: " + str(chat_id))
    chat_id
    karma_dictionary = None

    if chat_id not in chat_to_karma_dictionary:
        karma_dictionary = dict()
        chat_to_karma_dictionary[chat_id] = karma_dictionary
    else:
        karma_dictionary = chat_to_karma_dictionary[chat_id]
    if reply_user.id not in karma_dictionary:
        user = User(reply_user)
        karma_dictionary[reply_user.id] = user
        return user
    else:
        user: User = karma_dictionary[reply_user.id]
        return user
 """

""" def save_user(user: User, chat_id: int):
    logger.debug(chat_id)
    logger.debug("Chat to karma: ")
    logger.debug(chat_to_karma_dictionary)
    karma_dictionary = chat_to_karma_dictionary[chat_id]
    karma_dictionary[user.id] = user
    with open(chat_to_karma_filename, "wb") as backupfile:
        pickle.dump(chat_to_karma_dictionary, backupfile)


def reset_karma(chat_id: int):
    logger.info("Resetting Karma for all users: DANGEROUS")
    chat_to_karma_dictionary = dict()
    with open(chat_to_karma_filename, "wb") as backupfile:
        pickle.dump(chat_to_karma_dictionary, backupfile) """


def reply(bot: tg.Bot, update: tg.Update):
    logger.debug("reply")
    reply_user = user_from_tg_user(update.message.reply_to_message.from_user) 
    replying_user = user_from_tg_user(update.message.from_user)
    save_or_create_user(reply_user, conn)
    save_or_create_user(replying_user, conn)
    chat = Telegram_chat(str(update.message.chat_id), update.message.chat.title)
    save_or_create_chat(chat,conn)

    reply_uic = save_or_create_user_in_chat(reply_user, chat.chat_id,conn)
    replying_uic = save_or_create_user_in_chat(replying_user, chat.chat_id,conn)

    original_message_tg = update.message.reply_to_message
    reply_message_tg = update.message

    print("original_message_text: " + original_message_tg.text)
    print("original_message_user: " + reply_user.username)
    print("reply_message_text: " + reply_message_tg.text)
    print("replying_user: " + replying_user.username)
    
    original_message = Telegram_message(update.message.reply_to_message.message_id, chat.chat_id, reply_uic.user_id, update.message.reply_to_message.text)
    reply_message = Telegram_message(update.message.message_id, chat.chat_id, replying_uic.user_id, update.message.text)
    reply_text = reply_message.message_text
    chat_id = update.message.chat_id

    logger.debug(update.message.reply_to_message)

    if len(reply_text) >= 2 and reply_text[:2] == "+1":
        #if user tried to +1 self themselves
        if(replying_user.id == update.message.reply_to_message.from_user.id):
            witty_responses = [" how could you +1 yourself?", " what do you think you're doing?", " is your post really worth +1ing yourself?", " you won't get any goodie points for that", " try +1ing someone else instead of yourself!", " who are you to +1 yourself?", " beware the Jabberwocky", " have a 🍪!", " you must give praise. May he 🍔melt🍔! "]
            response = random.choice(witty_responses)
            message = "" + replying_user.first_name + response
            bot.send_message(chat_id=chat_id, text=message)
        else:
            user_reply_to_message(replying_user,reply_user, chat, original_message, reply_message, 1,conn)
            """ user = save_or_create_user_in_chat(reply_user.id,chat_id, conn,change_karma=1) """
            logger.debug("user replying other user")
            logger.debug(replying_user)
            logger.debug(reply_user)
    elif len(reply_text) >= 2 and reply_text[:2] == "-1":
        #user = save_or_create_user_in_chat(user_from_tg_user(reply_user), chat_id, conn, change_karma=-1)
        user_reply_to_message(replying_user, reply_user, chat, original_message, reply_message, -1,conn)
        logger.debug(replying_user)

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")


def show_version(bot,update,args):
    message = "Version: " + version + "\n" + "Bot powered by Python."
    message = message + "\nChangelog found at: " + changelog_url
    bot.send_message(chat_id=update.message.chat_id, text=message)
def show_user_stats(bot,update,args):
    user_id = update.message.from_user.id
    chat_id = str(update.message.chat_id)
    if len(args) != 1:
        bot.send_message(chat_id=update.message.chat_id, text="send argument of username")
        return
    username = args[0]
    if username[0] == "@":
        username = username[1:]

    selectuser = "select * from telegram_user tu where tu.username=%s"
    result = None
    with conn:
        with conn.cursor() as crs:
            crs.execute(selectuser,[username])
            result = crs.fetchone()
    if result is not None:
        select_user_replies = """select username, message_id, react_score, react_message_id  from telegram_user tu 
            left join user_reacted_to_message urtm on urtm.user_id=tu.user_id
            where tu.username = %s"""
        reacted_messages_result = None
        with conn:
            with conn.cursor() as crs:
                crs.execute(select_user_replies,[username])
                reacted_messages_result = crs.fetchone()
        if reacted_messages_result is not None:
            #this cmd shows react given to other
            stats_cmd = """select sum(react_score), count(react_score) from 
                (select username, message_id, react_score, react_message_id  from telegram_user tu 
                left join user_reacted_to_message urtm on urtm.user_id=tu.user_id
                where tu.username = %s
                ) as sub
                left join telegram_message tm on  tm.message_id= sub.message_id
                where tm.chat_id=%s;"""
            how_many_of_react_stats = """select react_score, count(react_score)from 
            (select username, message_id, react_score, react_message_id  from telegram_user tu 
            left join user_reacted_to_message urtm on urtm.user_id=tu.user_id
            where tu.username = %s
            ) as sub left join telegram_message tm on  tm.message_id= sub.message_id
            where tm.chat_id=%s
            group by react_score;"""
            negative_karma_given = 0
            positive_karma_given = 0

            result = None
            
            with conn:
                with conn.cursor() as crs:
                    crs.execute(stats_cmd,[username,chat_id])
                    result = crs.fetchone()
                    print(result)
                    crs.execute(how_many_of_react_stats,[username,chat_id])
                    rows = crs.fetchall()
                    print("rows: " + str(rows))
                    for row in rows:
                        if row[0] == -1:
                            negative_karma_given = int(row[1])
                        if row[0] == 1:
                            positive_karma_given = int(row[1])
                    result = crs.fetchone()

            
            karma = get_karma_for_user_in_chat(username,chat_id,conn)
            print(negative_karma_given)
            print(type(negative_karma_given))
            print(type(positive_karma_given))
            print(type(positive_karma_given-negative_karma_given))
            message = """Username: {:s} Karma: {:d}
Karma given out of score:
    Upvotes, Downvotes, Total Votes, Net Karma
    {:d}, {:d}, {:d}, {:d}"""
            message = message.format(username, karma,
            positive_karma_given, negative_karma_given,
            positive_karma_given + negative_karma_given,
            positive_karma_given - negative_karma_given)
            bot.send_message(chat_id=update.message.chat_id, text=message)    
            
        else:
            bot.send_message(chat_id=update.message.chat_id, text="User: " + username + " did not respond to any messages")    
        
    else:
        bot.send_message(chat_id=update.message.chat_id, text="No user with that username")


def show_user_messages(bot,update,args):
    user_id = update.message.from_user.id
    if len(args) != 1:
        bot.send_message(chat_id=update.message.chat_id, text="send argument of username")
        return
    username = args[0]
    chat_id = str(update.message.chat_id)
    selectcmd = """select * from 
            (select react_score, react_message_id, user_id as reply_user_id from
            ((select message_id,chat_id, message_text from 
                    (select user_id as custom_user_id from telegram_user tu where tu.username = %s) as sub
                        left join telegram_message tm on tm.author_user_id=sub.custom_user_id
                        where tm.chat_id=%s
                ) as messages_by_customer_user
            left join user_reacted_to_message urtm on urtm.message_id=messages_by_customer_user.message_id
            ) as sub2) as sub3
            left join telegram_user tu on tu.user_id = reply_user_id;
            """
    user_id = None
    with conn:
        with conn.cursor() as crs:
            crs.execute(selectcmd, [username, chat_id])
            """ crs.execute(selectcmd, [username])
            user_id = crs.fetchone()[0] """
    if user_id is None:
        bot.send_message(chat_id=update.message.chat_id, text="No user with that username")
        return
    res = get_message_responses_for_user_in_chat(user_id, update.message.chat_id,conn)
    bot.send_message(chat_id=update.message.chat_id, text=str(res))
    

def show_karma(bot,update,args):
    logger.debug("Chat id: " + str(update.message.chat_id))

    #returns username, karma
    rows : Tuple[str,int] = get_karma_for_users_in_chat(str(update.message.chat_id),conn)
    rows.sort(key=lambda user: user[1], reverse=True)

    message = "\n".join(["%s: %d" % (user[0], user[1]) for user in rows])

    if message != '':
        message = "Username: Karma\n" + message # TODO: figure out a better way to add this heading
    else:
        message = "Oops I didn't find any karma"

    bot.send_message(chat_id=update.message.chat_id, text=message) 

    #bot.send_message(chat_id=update.message.chat_id, text=str(karma))

    """ users = list(chat_to_karma_dictionary.get(update.message.chat_id, dict()).values())

    users.sort(key=lambda user: user.get_karma(), reverse=True)
    logger.debug("users length: "+ str(len(users)))
    """


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


""" this command runs last and lets the user know their command was not understood """
def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")


def main():
    """Start the bot """

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    reply_handler = MessageHandler(Filters.reply, reply)
    dispatcher.add_handler(reply_handler)

    showkarma_handler = CommandHandler('showkarma', show_karma, pass_args=True)
    dispatcher.add_handler(showkarma_handler)
    
    show_user_handler = CommandHandler('userinfo', show_user_stats, pass_args=True)
    dispatcher.add_handler(show_user_handler)

    #TODO: finsih this
    showusermessages_handler = CommandHandler('showusermessages', show_karma, pass_args=True)
    """ dispatcher.add_handler(showusermessages_handler) """

    showversion_handler = CommandHandler('version', show_version, pass_args=True)
    dispatcher.add_handler(showversion_handler)

    dispatcher.add_error_handler(error)

    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    updater.start_polling()

    """ from typing import Dict, NewType, Tuple
    ChatToKarmaDict = NewType('ChatToKarmaDict', Dict[int, Dict[int, User]])
    #dict of chat_id: int -> Karma_dictionary (which is user_id: int -> user: User)
    chat_to_karma_dictionary : ChatToKarmaDict = dict()
    chat_to_karma_filename = None
    if is_production:
        chat_to_karma_filename = "chat_to_karma_dictionary.p"
    else:
        chat_to_karma_filename = "chat_to_karma_dictionary_test.p"

    try:
        with open(chat_to_karma_filename, "rb") as backupfile:
            chat_to_karma_dictionary: ChatToKarmaDict = pickle.load(backupfile)
    except FileNotFoundError as fnfe:
        logger.info("Chat to Karma dictionary not found. Creating one")
        with open(chat_to_karma_filename, "wb") as backupfile:
            pickle.dump(chat_to_karma_dictionary, backupfile) """
    
    
    insert_chat = "INSERT INTO telegram_chat VALUES (%s,%s) ON CONFLICT (chat_id) DO UPDATE SET chat_name=EXCLUDED.chat_name"
    insert_user = "INSERT INTO telegram_user (user_id, username, first_name, last_name) VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING"
    #select first to see if a uic is set, in that case update those values
    select_uic = ""
    insert_uic = "INSERT INTO user_in_chat(user_id,chat_id, karma) VALUES (%s,%s,%s) ON CONFLICT (user_id,chat_id) DO UPDATE SET karma=EXCLUDED.karma"
    migrate = True
    import pandas as pd
    if migrate:
        df = pd.read_csv("db.csv",sep='\t')
        convert_cols = ['user_id','chat_id','karma']
        for col in convert_cols:
            df[col] = df[col].astype(int)
        print(df)
        for index, row in df.iterrows():
                #set 3 variables all on one line in python by seperating with ','
                user_id = row['user_id']
                chat_id = row['chat_id']
                username = row['username']
                first_name = row['first_name']
                last_name = row['last_name']
                karma = row['karma']

                #insert telegram_user
                cursor.execute(insert_user,[user_id, username, first_name, last_name])
                #insert telegram_chat
                try:
                    cursor.execute(insert_chat,[chat_id,'default_chat_name'])
                except psycopg2.DataError as de:
                    print("DE: " + de)
                
                #insert telegram_user_in_chat
                cursor.execute(insert_uic,[user_id, chat_id, karma])
        conn.commit()
        

    cursor.execute("SELECT * FROM pg_catalog.pg_tables;")
    many = cursor.fetchall()
    public_tables = list(filter(lambda x: x[0] == 'public', many))
    print("public_tables: "+ str(public_tables))

    """ cursor.execute("SELECT * FROM pg_catalog.pg_tables;")
    many = cursor.fetchall()
    public_tables = list(filter(lambda x: x[0] == 'public', many))
    print("public_tables: "+ str(public_tables))"""

    updater.idle()

    cursor.close()
    conn.close()    
    
    #TODO: create tests from this code
    """ user_id= 560101
    username="@username"
    first_name = "firstname"
    last_name = "lastname"
    user = User(user_id, username, first_name, last_name)
    user2 = User(43123, "@bob", "bob", "dude")
    save_or_create_user(user, conn)
    save_or_create_user(user2, conn) """
    
    """ print("run get or create user")
    print(save_or_create_user(user, conn))
    user.first_name = "another_first_name"
    print("User: " + str(user))
    updated_user: User = save_or_create_user(user,conn)
    assert updated_user.get_first_name() == "another_first_name" """

    """ chat_id=23432
    chat = Telegram_chat(chat_id, "chat name 1")
    save_or_create_chat(chat, conn)
    uic = save_or_create_user_in_chat(user,chat_id,conn)
    uic2 = save_or_create_user_in_chat(user2,chat_id, conn)
    message1 = Telegram_message(31,chat_id,uic.id, "here is a message from @username")
    message2 = Telegram_message(27,chat_id,uic2.id, "message from bob")
    user_reply_to_message(user,chat, message1,message2, 1,conn)
    print(get_karma_for_users_in_chat(chat.chat_id, conn))
    print(get_message_responses_for_user_in_chat(user.id, chat.chat_id, conn)) """


    """ with conn:
            with conn.cursor() as curs:
            # this block is now in a transaction: yay python with block magic

             """
    


if __name__ == '__main__':
    main()
