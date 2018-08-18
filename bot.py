from telegram.ext import Updater
import telegram as tg
from user import User
import logging

import random

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

version = '1.03'
changelog_url = 'https://schafezp.com/schafezp/txkarmabot/blob/master/CHANGELOG.md'

production_token = '613654042:AAHnLhu4TFC-xJ4IylkXdczX9ihnIgtqnI8'
test_token = '650879477:AAFO_o2_nt2gmwA-h0TeIo4bSqI-WLxp6VM'
is_production = False

import os

try:
    prodvar = os.environ['PROD']
    if prodvar == "true":
        print("PROD var found with value true! ")
        print("running in production mode")
        is_production = True
    else:
        print("PROD var equal to: " + prodvar)
        print("Running test mode")
except KeyError as ke:
    print("PROD var not found")
    print("Running test mode")
    is_production = False

updater = None
if is_production:
    updater = Updater(token=production_token)
else:
    updater = Updater(token=test_token)

dispatcher = updater.dispatcher
#Karma Dictionary
import pickle


#dict of chat_id: int -> Karma_dictionary (which is user_id: int -> user: User)
chat_to_karma_dictionary = dict()
chat_to_karma_filename = None
if is_production:
    chat_to_karma_filename = "chat_to_karma_dictionary.p"
else:
    chat_to_karma_filename = "chat_to_karma_dictionary_test.p"

try:
    with open(chat_to_karma_filename, "rb") as backupfile:
        chat_to_karma_dictionary = pickle.load(backupfile)
except FileNotFoundError as fnfe:
    print("Chat to Karma dictionary not found. Creating one")
    with open(chat_to_karma_filename, "wb") as backupfile:
        pickle.dump(chat_to_karma_dictionary, backupfile)

def get_user_by_reply_user(reply_user: tg.User, chat_id: int):
    print("Chat id: " + str(chat_id))
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
    print(chat_id)
    karma_dictionary = chat_to_karma_dictionary[chat_id]
    karma_dictionary[user.id] = user
    with open(chat_to_karma_filename, "wb") as backupfile:
        pickle.dump(chat_to_karma_dictionary, backupfile)

def reset_karma(chat_id: int):
    print("Resetting Karma for all users: DANGEROUS")
    chat_to_karma_dictionary = dict()
    with open(chat_to_karma_filename, "wb") as backupfile:
        pickle.dump(chat_to_karma_dictionary, backupfile)

def reply(bot: tg.Bot, update: tg.Update):
    reply_user = update.message.reply_to_message.from_user

    print(update.message.reply_to_message)

    # might consume this info later down the line for metrics
    """ reply_to_message = update.message.reply_to_message
    message_id = reply_to_message.message_id
    original_message_text = reply_to_message.text
     """
    reply_text = update.message.text
    chat_id = update.message.chat_id

    #TODO: check if +1 is first 2chars
    if len(reply_text) >= 2 and reply_text[:2] == "+1":
        #if user tried to +1 self themselves 
        if(reply_user.id == update.message.from_user.id):
            responses = [" how could you +1 yourself?", " what do you think you're doing?", " is your post really worth +1ing yourself?", " you won't get any goodie points for that", " try +1ing someone else instead of yourself!", " who are you to +1 yourself?", " beware the Jabberwocky", " have a 🍪!"]
            response = random.choice(responses)
            message = "" + reply_user.first_name + response
            bot.send_message(chat_id=chat_id, text=message)        
        else:
            user = get_user_by_reply_user(reply_user, chat_id)
            user.give_karma()
            print(user)
            save_user(user, chat_id)
    elif len(reply_text) >= 2 and reply_text[:2] == "-1":
        user = get_user_by_reply_user(reply_user, chat_id)
        user.remove_karma()
        print(user)
        save_user(user, chat_id)

    

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")

def echo(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=update.message.text)


def caps(bot, update, args):
     text_caps = ' '.join(args).upper()
     bot.send_message(chat_id=update.message.chat_id, text=text_caps)
def showversion(bot,update,args):
    message = "Version: " + version + "\n" + "Bot powered by Python."
    message = message + "\nChangelog found at: " + changelog_url
    bot.send_message(chat_id=update.message.chat_id, text=message)



def showkarma(bot,update,args):
    message = ""
    #(username, karma)
    print("bot dir")
    #print(dir(bot))
    print(bot.get_me())
    bot_id = bot.get_me().id
    users = []

    karma_dictionary = None
    try:
        print("Chat id: " + str(update.message.chat_id))
        karma_dictionary = chat_to_karma_dictionary[update.message.chat_id]
    except KeyError as _:
        message = "Oops I did not find any karma"
        bot.send_message(chat_id=update.message.chat_id, text=message)
        return
    except IndexError as ie:
        print(ie)
    
    for id, user in karma_dictionary.items():
        if id != bot_id:
            users.append(user)   

    users.sort(key=lambda user: user.get_karma(), reverse=True)
    for user in users:
        message = message + str(user) + "\n"

    if message == "":
        message = "Oops I did not find any karma"
    bot.send_message(chat_id=update.message.chat_id, text=message)

def pluskarma(bot, update, args):
    bot.send_message(chat_id=update.message.chat_id, text="you threw +1 karma into the void")

def minuskarma(bot, update, args):
    bot.send_message(chat_id=update.message.chat_id, text="you threw -1 karma into the void")

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

""" this command runs last and lets the user know their command was not understood """
def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")


def main():
    """Start the bot """

    from telegram.ext import CommandHandler
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    from telegram.ext import MessageHandler, Filters
    """ echo_handler = MessageHandler(Filters.text, echo)
    dispatcher.add_handler(echo_handler) """

    reply_handler = MessageHandler(Filters.reply, reply)
    dispatcher.add_handler(reply_handler)

    caps_handler = CommandHandler('caps', caps, pass_args=True)
    dispatcher.add_handler(caps_handler)

    showkarma_handler = CommandHandler('showkarma', showkarma, pass_args=True)
    dispatcher.add_handler(showkarma_handler)

    showversion_handler = CommandHandler('version', showversion, pass_args=True)
    dispatcher.add_handler(showversion_handler)

    """ plus_karma_handler = CommandHandler('+1', pluskarma, pass_args=True)
    dispatcher.add_handler(plus_karma_handler)

    plus_karma_handler = CommandHandler('plus1', pluskarma, pass_args=True)
    dispatcher.add_handler(plus_karma_handler)

    minus_karma_handler = CommandHandler('-1', minuskarma, pass_args=True)
    dispatcher.add_handler(minus_karma_handler)

    minus_karma_handler = CommandHandler('minus1', minuskarma, pass_args=True)
    dispatcher.add_handler(minus_karma_handler) """

    dispatcher.add_error_handler(error)

    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()