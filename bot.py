from telegram.ext import Updater
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


token = '613654042:AAHnLhu4TFC-xJ4IylkXdczX9ihnIgtqnI8'
updater = Updater(token=token)
dispatcher = updater.dispatcher

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")
from telegram.ext import CommandHandler
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


def echo(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=update.message.text)
from telegram.ext import MessageHandler, Filters
echo_handler = MessageHandler(Filters.text, echo)
dispatcher.add_handler(echo_handler)


def caps(bot, update, args):
     text_caps = ' '.join(args).upper()
     bot.send_message(chat_id=update.message.chat_id, text=text_caps)

caps_handler = CommandHandler('caps', caps, pass_args=True)
dispatcher.add_handler(caps_handler)

def pluskarma(bot, update, args):
     bot.send_message(chat_id=update.message.chat_id, text="you threw +1 karma into the void")

plus_karma_handler = CommandHandler('+1', pluskarma, pass_args=True)
dispatcher.add_handler(plus_karma_handler)

def minuskarma(bot, update, args):
    bot.send_message(chat_id=update.message.chat_id, text="you threw -1 karma into the void")

minus_karma_handler = CommandHandler('-1', minuskarma, pass_args=True)
dispatcher.add_handler(minus_karma_handler)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


dispatcher.add_error_handler(error)

def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")

unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

updater.start_polling()
updater.idle()


