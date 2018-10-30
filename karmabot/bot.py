"""Main entry point for telegram bot."""
import logging
import os
import sys
from typing import Tuple, List
from functools import wraps

from telegram.ext import Filters, CommandHandler, MessageHandler, Updater, CallbackQueryHandler
import telegram as tg

from .models import User
from . import postgres_funcs as pf
from .customutils import attempt_connect, check_env_vars_all_loaded

from .responses import SHOW_KARMA_NO_HISTORY_RESPONSE
from .commands_strings import START_COMMAND, CLEAR_CHAT_COMMAND, SHOW_KARMA_COMMAND, USER_INFO_COMMAND, CHAT_INFO_COMMAND, HISTORY_GRAPH_COMMAND, SHOW_KARMA_KEYBOARD_COMMAND

from .handlers import start, show_version, gen_show_karma, gen_reply, gen_show_user_stats, gen_show_chat_info, \
    gen_show_history_graph, gen_clear_chat_with_bot, gen_show_karma_personally
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
LIST_OF_ADMINS = []


def restricted(func):
    """Function wrap to deny access to a user based on user_id"""
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        """function to wrap"""
        user_id = update.effective_user.id
        if user_id not in LIST_OF_ADMINS:
            print("Unauthorized access denied for {}.".format(user_id))
        return func(bot, update, *args, **kwargs)
    return wrapped




#TODO: move this down into the main function
#this stops us from importing directly from this function: bad practice
#blocks here
conn = attempt_connect()

# TODO: replace this with an annotation maybe?


def use_command(command: str, user: User, chat_id: str, arguments=""):
    """Handler to log when commands are used and with which arguments"""
    pf.create_chat_if_not_exists(chat_id, conn)
    pf.save_or_create_user(user, conn)
    insertcmd = """INSERT INTO command_used (command,arguments,user_id,chat_id) VALUES (%s,%s,%s,%s)"""
    with conn:
        with conn.cursor() as crs:
            crs.execute(insertcmd, [command, arguments, user.id, chat_id])

def format_show_karma_for_users_in_chat(chat_id):
    """Returns a formatted html message showing the karma for users in a chat"""
    rows: List[Tuple[str, str, int]] = pf.get_karma_for_users_in_chat(
        chat_id, conn)
    if rows == []:
        return SHOW_KARMA_NO_HISTORY_RESPONSE

    rows.sort(key=lambda user: user[2], reverse=True)
    # use firstname if username not set

    def cleanrow(user):
        """selects desired user attributes to show"""
        if user[0] is None:
            return (user[1], user[2])
        else:
            return (user[0], user[2])
    message_rows = []
    idx = 0
    for user in map(cleanrow, rows):
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
    message = "<b>Username: Karma</b>\n" + message
    return message


@restricted
def am_i_admin(bot, update, args):
    """Handler to check if user is an admin"""
    message = "yes you are an admin"
    bot.send_message(chat_id=update.message.chat_id, text=message)





#TODO: rename
def show_karma_personally_button_pressed(bot, update):
    """Runs /showkarma on chat the user_selected"""
    query = update.callback_query
    chat_id: str = str(query.data)
    message = format_show_karma_for_users_in_chat(chat_id)
    chat_name = pf.get_chatname(chat_id, conn)
    if chat_name is not None:
        message = f"<b>Chat name: {chat_name}</b>\n{message}"

    bot.edit_message_text(text=message,
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          parse_mode=tg.ParseMode.HTML)


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

    am_i_admin_handler = CommandHandler('amiadmin', am_i_admin, pass_args=True)
    dispatcher.add_handler(am_i_admin_handler)

    showversion_handler = CommandHandler(
        'version', show_version, pass_args=True)
    dispatcher.add_handler(showversion_handler)

    show_karma_personally_handler = CommandHandler(
        SHOW_KARMA_KEYBOARD_COMMAND, gen_show_karma_personally(db_service))
    dispatcher.add_handler(show_karma_personally_handler)
    dispatcher.add_handler(CallbackQueryHandler(show_karma_personally_button_pressed))

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

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pg_catalog.pg_tables;")
    many = cursor.fetchall()
    public_tables = list(
        map(lambda x: x[1], filter(lambda x: x[0] == 'public', many)))
    logging.info(f"public_tables: {str(public_tables)}")

    updater.idle()

    cursor.close()
    conn.close()


if __name__ == '__main__':
    main()
