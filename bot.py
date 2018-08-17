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

def echo(bot, update):
    print(dir(bot))
    print(dir(update))
    print(bot.getMe())
    bot.send_message(chat_id=update.message.chat_id, text=update.message.text)

def caps(bot, update, args):
     text_caps = ' '.join(args).upper()
     bot.send_message(chat_id=update.message.chat_id, text=text_caps)

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
    echo_handler = MessageHandler(Filters.text, echo)
    dispatcher.add_handler(echo_handler)

    caps_handler = CommandHandler('caps', caps, pass_args=True)
    dispatcher.add_handler(caps_handler)

    plus_karma_handler = CommandHandler('+1', pluskarma, pass_args=True)
    dispatcher.add_handler(plus_karma_handler)

    plus_karma_handler = CommandHandler('plus1', pluskarma, pass_args=True)
    dispatcher.add_handler(plus_karma_handler)

    minus_karma_handler = CommandHandler('-1', minuskarma, pass_args=True)
    dispatcher.add_handler(minus_karma_handler)

    minus_karma_handler = CommandHandler('minus1', minuskarma, pass_args=True)
    dispatcher.add_handler(minus_karma_handler)

    dispatcher.add_error_handler(error)



    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()