import logging
import os
import pickle
import random
import psycopg2 # postgresql python 

from telegram.ext import Filters, CommandHandler, MessageHandler, Updater
import telegram as tg
from typing import Dict, NewType

from user import User

log_level = os.environ.get('LOGLEVEL')
level = None
if log_level == "debug":
    level=logging.DEBUG
elif log_level == "info":
    level=logging.INFO
else:
    levle=logging.INFO

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=level)
logger = logging.getLogger(__name__)

version = '1.03' # TODO: make this automatic
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
        pickle.dump(chat_to_karma_dictionary, backupfile)


def get_user_by_reply_user(reply_user: tg.User, chat_id: int):
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


def save_user(user: User, chat_id: int):
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
        pickle.dump(chat_to_karma_dictionary, backupfile)


def reply(bot: tg.Bot, update: tg.Update):
    logger.debug("reply")
    reply_user = update.message.reply_to_message.from_user

    logger.debug(update.message.reply_to_message)

    # might consume this info later down the line for metrics
    """
    reply_to_message = update.message.reply_to_message
    message_id = reply_to_message.message_id
    original_message_text = reply_to_message.text
    """
    reply_text = update.message.text
    chat_id = update.message.chat_id

    #TODO: check if +1 is first 2chars
    if len(reply_text) >= 2 and reply_text[:2] == "+1":
        #if user tried to +1 self themselves
        if(reply_user.id == update.message.from_user.id):
            witty_responses = [" how could you +1 yourself?", " what do you think you're doing?", " is your post really worth +1ing yourself?", " you won't get any goodie points for that", " try +1ing someone else instead of yourself!", " who are you to +1 yourself?", " beware the Jabberwocky", " have a 🍪!", " you must give praise. May he 🍔melt🍔! "]
            response = random.choice(witty_responses)
            message = "" + reply_user.first_name + response
            bot.send_message(chat_id=chat_id, text=message)
        else:
            user = get_user_by_reply_user(reply_user, chat_id)
            user.give_karma()
            logger.debug("user")
            logger.debug(user)
            save_user(user, chat_id)
    elif len(reply_text) >= 2 and reply_text[:2] == "-1":
        user = get_user_by_reply_user(reply_user, chat_id)
        user.remove_karma()
        logger.debug(user)
        save_user(user, chat_id)


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")


def show_version(bot,update,args):
    message = "Version: " + version + "\n" + "Bot powered by Python."
    message = message + "\nChangelog found at: " + changelog_url
    bot.send_message(chat_id=update.message.chat_id, text=message)


def show_karma(bot,update,args):
    logger.debug("Chat id: " + str(update.message.chat_id))
    # Use the lower one if you find it more pythonic
    #users = chat_to_karma_dictionary[update.message.chat_id].items() if not KeyError else []
    users = list(chat_to_karma_dictionary.get(update.message.chat_id, dict()).values())

    users.sort(key=lambda user: user.get_karma(), reverse=True)
    logger.debug("users length: "+ str(len(users)))
    message = "\n".join(["%s: %d" % (user.get_username(), user.get_karma()) for user in users])

    if message != '':
        message = "Username: Karma\n" + message # TODO: figure out a better way to add this heading
    else:
        message = "Oops I didn't find any karma"

    bot.send_message(chat_id=update.message.chat_id, text=message)


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

    showversion_handler = CommandHandler('version', show_version, pass_args=True)
    dispatcher.add_handler(showversion_handler)

    dispatcher.add_error_handler(error)

    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    #updater.start_polling()
    conn = None
    while conn is None:
        try:
            conn = psycopg2.connect(host="postgres", database="karmabot", user="test_user", password="test_pass")
        except psycopg2.OperationalError as oe:
            print(oe)
    
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM pg_catalog.pg_tables;")
    many = cursor.fetchmany()
    print("many: "+ str(many))
    public_tables = list(filter(lambda x: x[0] == 'public', many))

    with cursor as crs:
        conn.set_session(autocommit=True)
        schema = open("start-schema.pgsql","r").read()
        print("schema: " + schema)
        print(cursor.execute(schema))
        conn.commit()

    """ print(public_tables)
    if len(public_tables) != 0:
        print('Tables exist in database')
    else:
        schema = open("start-schema.pgsql","r").read()
        print("schema: " + schema)
        print(cursor.execute(schema))
        conn.commit() """

    #updater.idle()


if __name__ == '__main__':
    main()
