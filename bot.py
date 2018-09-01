import logging
import os
import sys
import pickle
import random
import psycopg2 # postgresql python 
import re

from telegram.ext import Filters, CommandHandler, MessageHandler, Updater
import telegram as tg
from typing import Dict, NewType, Tuple, List

from user import User, User_in_chat, Telegram_chat, Telegram_message,user_from_tg_user
from dbhelper import *

log_level = os.environ.get('LOG_LEVEL')
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

from functools import wraps
LIST_OF_ADMINS = [65278791]
def restricted(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in LIST_OF_ADMINS:
            print("Unauthorized access denied for {}.".format(user_id))
            return
        return func(bot, update, *args, **kwargs)
    return wrapped


conn = None
import time

#TODO: move this function
#Returns false if any of the required environment variables are not set
def check_env_vars_all_loaded() -> Tuple[bool,str]:
    env_vars = ['BOT_TOKEN','LOG_LEVEL','POSTGRES_USER','POSTGRES_PASS','POSTGRES_DB', ]
    logger.info("Environment Variables:")
    for var in env_vars:
        val = os.environ.get(var) 
        if val is None or val == '':
            logger.info('Variable: {} Value: {}'.format(var," VALUE MISSING. EXITING"))
            return (False,var)
        else:
            logger.info('Variable: {} Value: {}'.format(var,val))
            
    return (True,var)



#TODO:move this logic elsewhere and handle singleton connection in different way
while conn is None:
    try:
        host = os.environ.get("POSTGRES_HOSTNAME")
        database = os.environ.get("POSTGRES_DB")
        user = os.environ.get("POSTGRES_USER")
        password = os.environ.get("POSTGRES_PASS")
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
    except psycopg2.OperationalError as oe:
        print(oe)
        time.sleep(1)

cursor = conn.cursor()


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

    logger.debug("original_message_text: " + str(original_message_tg.text))
    logger.debug("original_message_user: " + str(reply_user.username))
    logger.debug("reply_message_text: " + str(reply_message_tg.text))
    logger.debug("replying_user: " + str(replying_user.username))
    
    original_message = Telegram_message(update.message.reply_to_message.message_id, chat.chat_id, reply_uic.user_id, update.message.reply_to_message.text)
    reply_message = Telegram_message(update.message.message_id, chat.chat_id, replying_uic.user_id, update.message.text)
    reply_text = reply_message.message_text
    chat_id = update.message.chat_id
    if re.match("^([\+pP][1-9][0-9]*|[Pp]{2}).*", reply_text):
        #if user tried to +1 self themselves
        if(replying_user.id == update.message.reply_to_message.from_user.id):
            witty_responses = [" how could you +1 yourself?", " what do you think you're doing?", " is your post really worth +1ing yourself?", " you won't get any goodie points for that", " try +1ing someone else instead of yourself!", " who are you to +1 yourself?", " beware the Jabberwocky", " have a 🍪!", " you must give praise. May he 🍔melt🍔! "]
            response = random.choice(witty_responses)
            message = "" + replying_user.first_name + response
            bot.send_message(chat_id=chat_id, text=message)
        else:
            user_reply_to_message(replying_user,reply_user, chat, original_message, reply_message, 1,conn)
            logger.debug("user replying other user")
            logger.debug(replying_user)
            logger.debug(reply_user)
    elif re.match("^([\+pP][1-9][0-9]*|[Dd]{2}).*", reply_text) :
        user_reply_to_message(replying_user, reply_user, chat, original_message, reply_message, -1,conn)
        logger.debug(replying_user)

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")


def show_version(bot,update,args):
    message = "Version: " + version + "\n" + "Bot powered by Python."
    #harder to hack the bot if source code is obfuscated :p
    #message = message + "\nChangelog found at: " + changelog_url
    bot.send_message(chat_id=update.message.chat_id, text=message)
def show_user_stats(bot,update,args):
    #TODO: remove this boiler plate code somehow
    #without this if this is the first command run alone with the bot it will fail due to psycopg2.IntegrityError: insert or update on table "command_used" violates foreign key constraint "command_used_chat_id_fkey"
    chat = Telegram_chat(str(update.message.chat_id), update.message.chat.title)
    save_or_create_chat(chat,conn)
    
    user_id = update.message.from_user.id
    chat_id = str(update.message.chat_id)
    if len(args) != 1:
        bot.send_message(chat_id=update.message.chat_id, text="use command like: /userinfo username")
        return
    username = args[0]
    if username[0] == "@":
        username = username[1:]
        
    use_command('userinfo',user_from_tg_user(update.message.from_user), str(update.message.chat_id), arguments=username)

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
            how_many_reacted_to_user_stats = """
            
            """
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
            if karma is None: karma = 0
            message = """Username: {:s} Karma: {:d}
Karma given out stats:
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
    
#TODO: replace this with an annotation maybe?
def use_command(command: str,user: User, chat_id: str, arguments=""):
    create_chat_if_not_exists(chat_id,conn)
    save_or_create_user(user,conn)
    insertcmd = """INSERT INTO command_used (command,arguments,user_id,chat_id) VALUES (%s,%s,%s,%s)"""
    with conn:
        with conn.cursor() as crs:
            crs.execute(insertcmd,[command,arguments,user.id,chat_id])


def show_karma(bot,update,args):
    use_command('showkarma',user_from_tg_user(update.message.from_user), str(update.message.chat_id))
    logger.debug("Chat id: " + str(update.message.chat_id))

    #returns username, first_name, karma
    rows : List[Tuple[str,str,int]] = get_karma_for_users_in_chat(str(update.message.chat_id),conn)
    rows.sort(key=lambda user: user[2], reverse=True)
    #use firstname if username not set
    def cleanrow(user):
        if user[0] is None:
            return (user[1],user[2])
        else:
            return (user[0],user[2])
    message_rows = []
    idx = 0
    for user in map(cleanrow,rows):
        row = f"{user[0]}: {user[1]}"
        if idx == 0:
            row = '🥇' + row 
        elif idx == 1:
            row = '🥈' + row 
        elif idx == 2:
            row = '🥉' + row 
        idx = idx + 1
        message_rows.append(row)
    message = "\n".join(message_rows)

    if message != '':
        message = "Username: Karma\n" + message # TODO: figure out a better way to add this heading
    else:
        message = "Oops I didn't find any karma"

    bot.send_message(chat_id=update.message.chat_id, text=message) 

def show_chat_info(bot,update,args):
    use_command('chatinfo',user_from_tg_user(update.message.from_user.id), str(update.message.chat_id))
    chat_id = str(update.message.chat_id)
    title = update.message.chat.title
    selectcmd = """select count(tm.message_id) from user_reacted_to_message urtm 
left join telegram_message tm ON tm.message_id = urtm.message_id
where tm.chat_id=%s"""
    select_user_with_karma_count = """ 
    select count(*) from telegram_chat tc 
    left join user_in_chat uic on uic.chat_id = tc.chat_id
    where tc.chat_id=%s
    """
    with conn:
        with conn.cursor() as crs:
            crs.execute(selectcmd,[chat_id])
            result = crs.fetchone()
            
            message = ""
            reply_count = None
            if result is not None:
                reply_count = result[0]
            else:
                reply_count = 0

            crs.execute(select_user_with_karma_count,[chat_id])
            result = crs.fetchone()
            user_with_karma_count = None
            if result is not None: 
                user_with_karma_count = result[0]
            else:
                user_with_karma_count = 0

            message = "Chat: {:s}.\n Number of Users with Karma: {:d}\n Total Reply Count: {:d}".format(title,user_with_karma_count, reply_count)
            bot.send_message(chat_id=update.message.chat_id, text=message)

@restricted
def am_I_admin(bot,update,args):
    message = "yes you are an admin"
    bot.send_message(chat_id=update.message.chat_id, text=message)

def show_karma_personally(bot,update,args):
    #TODO:check if this is a 1 on 1 message

    #might be best to use a different handler:
    #offer choice to user of which chat they want to see the karma totals of

    #user clicks on button to choose chat (similar to BotFather) then bot responds with karma for that chat

    print()


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


""" this command runs last and lets the user know their command was not understood """
def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")


def main():
    """Start the bot """
    (is_loaded, var) = check_env_vars_all_loaded()
    if not is_loaded:
        logger.info("Env vars not set that are required: " + str(var))
        sys.exit(1)

    # Setup bot token from environment variables
    bot_token = os.environ.get('BOT_TOKEN') 

    updater = Updater(token=bot_token)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    reply_handler = MessageHandler(Filters.reply, reply)
    dispatcher.add_handler(reply_handler)

    showkarma_handler = CommandHandler('showkarma', show_karma, pass_args=True)
    dispatcher.add_handler(showkarma_handler)
    
    show_user_handler = CommandHandler('userinfo', show_user_stats, pass_args=True)
    dispatcher.add_handler(show_user_handler)

    chat_info_handler = CommandHandler('chatinfo', show_chat_info, pass_args=True)
    dispatcher.add_handler(chat_info_handler)

    am_I_admin_handler = CommandHandler('amiadmin', am_I_admin, pass_args=True)
    dispatcher.add_handler(am_I_admin_handler)


    #TODO: finish this
    showusermessages_handler = CommandHandler('showusermessages', show_karma, pass_args=True)
    """ dispatcher.add_handler(showusermessages_handler) """

    showversion_handler = CommandHandler('version', show_version, pass_args=True)
    dispatcher.add_handler(showversion_handler)

    dispatcher.add_error_handler(error)

    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    updater.start_polling()

    cursor.execute("SELECT * FROM pg_catalog.pg_tables;")
    many = cursor.fetchall()
    public_tables = list(map(lambda x: x[1], filter(lambda x: x[0] == 'public', many)))
    logger.info("public_tables: "+ str(public_tables))
    updater.idle()

    cursor.close()
    conn.close()    
    

if __name__ == '__main__':
    main()
