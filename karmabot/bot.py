"""Main entry point for telegram bot."""
import logging
import os
import sys

from telegram.ext import Filters, CommandHandler, MessageHandler, Updater, CallbackQueryHandler

from .customutils import attempt_connect, check_env_vars_all_loaded

from .commands_strings import START_COMMAND, CLEAR_CHAT_COMMAND, SHOW_KARMA_COMMAND, USER_INFO_COMMAND,\
    CHAT_INFO_COMMAND, HISTORY_GRAPH_COMMAND, SHOW_KARMA_KEYBOARD_COMMAND

from .handlers import start, show_version, gen_show_karma, gen_reply, gen_show_user_stats, gen_show_chat_info, \
    gen_show_history_graph, gen_clear_chat_with_bot, gen_show_karma_personally, gen_show_karma_personally_button_pressed
from .telegramservice import PostgresKarmabotDatabaseService, PostgresDBConfig

LOG_LEVEL_ENV_VAR = os.environ.get('LOG_LEVEL')
LOG_LEVEL = None
if LOG_LEVEL_ENV_VAR == "debug":
    LOG_LEVEL = logging.DEBUG
elif LOG_LEVEL_ENV_VAR == "info":
    LOG_LEVEL = logging.INFO
else:
    LOG_LEVEL = logging.ERROR

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=LOG_LEVEL)
LOGGER = logging.getLogger(__name__)

CHANGELOG_URL = 'https://github.com/schafezp/karmabot'


def error(bot, update, _error):
    """Log Errors caused by Updates."""
    logging.warning('Update "%s" caused error "%s"', update, _error)


def main():
    """Start the bot """
    required_env_vars = ['BOT_TOKEN',
                         'LOG_LEVEL',
                         'POSTGRES_USER',
                         'POSTGRES_PASS',
                         'POSTGRES_DB',]
    (is_loaded, var) = check_env_vars_all_loaded(required_env_vars)
    if not is_loaded:
        logging.info(f"Env vars not set that are required: {str(var)}")
        sys.exit(1)

    HOST = os.environ.get("POSTGRES_HOSTNAME")
    DATABASE = os.environ.get("POSTGRES_DB")
    USER = os.environ.get("POSTGRES_USER")
    PASSWORD = os.environ.get("POSTGRES_PASS")
    db_config = PostgresDBConfig(HOST, DATABASE, USER, PASSWORD)
    db_service = PostgresKarmabotDatabaseService(db_config)
    # Setup bot token from environment variables
    bot_token = os.environ.get('BOT_TOKEN')

    updater = Updater(token=bot_token)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler(START_COMMAND, start)
    dispatcher.add_handler(start_handler)

    #TODO: determine better way to get db_service in scope than to inject into each funcntion
    reply_handler = MessageHandler(Filters.reply, gen_reply(db_service))
    dispatcher.add_handler(reply_handler)

    showkarma_handler = CommandHandler(SHOW_KARMA_COMMAND, gen_show_karma(db_service), pass_args=True)
    dispatcher.add_handler(showkarma_handler)

    show_user_handler = CommandHandler(
        USER_INFO_COMMAND, gen_show_user_stats(db_service), pass_args=True)
    dispatcher.add_handler(show_user_handler)

    chat_info_handler = CommandHandler(
        CHAT_INFO_COMMAND, gen_show_chat_info(db_service), pass_args=True)
    dispatcher.add_handler(chat_info_handler)

    showversion_handler = CommandHandler(
        'version', show_version, pass_args=True)
    dispatcher.add_handler(showversion_handler)

    show_karma_personally_handler = CommandHandler(
        SHOW_KARMA_KEYBOARD_COMMAND, gen_show_karma_personally(db_service))
    dispatcher.add_handler(show_karma_personally_handler)
    dispatcher.add_handler(CallbackQueryHandler(gen_show_karma_personally_button_pressed(db_service)))

    show_history_graph_handler = CommandHandler(
        HISTORY_GRAPH_COMMAND, gen_show_history_graph(db_service))
    dispatcher.add_handler(show_history_graph_handler)

    #used for integration testing
    #should only work to clear a chat with a bot
    #chat_id == user_id
    clear_chat_with_bot_handler = CommandHandler(
        CLEAR_CHAT_COMMAND, gen_clear_chat_with_bot(db_service))
    dispatcher.add_handler(clear_chat_with_bot_handler)

    dispatcher.add_error_handler(error)

    updater.start_polling()

    conn = attempt_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pg_catalog.pg_tables;")
    many = cursor.fetchall()
    public_tables = list(
        map(lambda x: x[1], filter(lambda x: x[0] == 'public', many)))
    logging.info(f"public_tables: {str(public_tables)}")
    cursor.close()
    conn.close()

    updater.idle()




if __name__ == '__main__':
    main()
