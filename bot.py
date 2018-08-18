from telegram.ext import Updater
import telegram as tg
from user import User
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

version = '1.00'

production_token = '613654042:AAHnLhu4TFC-xJ4IylkXdczX9ihnIgtqnI8'
test_token = '650879477:AAFO_o2_nt2gmwA-h0TeIo4bSqI-WLxp6VM'
is_production = False
updater = None
if is_production:
    updater = Updater(token=production_token)
else:
    updater = Updater(token=test_token)

dispatcher = updater.dispatcher
#Karma Dictionary
import pickle

karma_dictionary = dict()
karma_dictionary_filename = None
if is_production:
    karma_dictionary_filename = "karma_dictionary.p"
else:
    karma_dictionary_filename = "karma_dictionary_test.p"


try:
    with open(karma_dictionary_filename, "rb") as backupfile:
        karma_dictionary = pickle.load(backupfile)
except FileNotFoundError as fnfe:
    print("Karma dictionary not found. Creating one")
    karma_dictionary = dict()
    with open(karma_dictionary_filename, "wb") as backupfile:
        pickle.dump(karma_dictionary, backupfile)

def get_user_by_reply_user(reply_user: tg.User):
    if reply_user.id not in karma_dictionary:
        user = User(reply_user)
        print(reply_user.id)
        print(karma_dictionary)
        print(type(karma_dictionary))

        karma_dictionary[reply_user.id] = user
        return user
    else:
        user: User = karma_dictionary[reply_user.id]
        return user

def save_user(user: User):
    karma_dictionary[user.id] = user
    with open(karma_dictionary_filename, "wb") as backupfile:
        pickle.dump(karma_dictionary, backupfile)

def reset_karma():
    print("Resetting Karma for all users: DANGEROUS")
    karma_dictionary = dict()
    with open(karma_dictionary_filename, "wb") as backupfile:
        pickle.dump(karma_dictionary, backupfile)

def reply(bot: tg.Bot, update: tg.Update):
    reply_user = update.message.reply_to_message.from_user
    

    # might consume this info later down the line for metrics
    """ reply_to_message = update.message.reply_to_message
    message_id = reply_to_message.message_id
    original_message_text = reply_to_message.text
     """
    reply_text = update.message.text

    #TODO: check if +1 is first 2chars
    if reply_text == "/plus1" or reply_text == "+1" :
        user = get_user_by_reply_user(reply_user)
        user.give_karma()
        print(user)
        save_user(user)
    elif reply_text == "/minus1" or reply_text == "-1":
        user = get_user_by_reply_user(reply_user)
        user.remove_karma()
        print(user)
        save_user(user)

    #bot.send_message(chat_id=update.message.chat_id, text=update.message.text)

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")

def echo(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=update.message.text)


def caps(bot, update, args):
     text_caps = ' '.join(args).upper()
     bot.send_message(chat_id=update.message.chat_id, text=text_caps)
def showversion(bot,update,args):
    message = "Version: " + version + "\n" + "Bot powered by Python."
    bot.send_message(chat_id=update.message.chat_id, text=message)



def showkarma(bot,update,args):
    message = ""
    #(username, karma)
    users = []
    for id, user in karma_dictionary.items():
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