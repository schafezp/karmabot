"""Main entry point for telegram bot."""
import logging
import os
import sys
import re
from typing import Tuple, List, Any
from functools import wraps

from telegram.ext import Filters, CommandHandler, MessageHandler, Updater, CallbackQueryHandler
import telegram as tg

from models import User, Telegram_Chat, Telegram_Message, user_from_tg_user
import postgres_funcs as pf
from utils import attempt_connect, check_env_vars_all_loaded

LOG_LEVEL_ENV_VAR = os.environ.get('LOG_LEVEL')
LOG_LEVEL = None
if LOG_LEVEL_ENV_VAR == "debug":
    LOG_LEVEL = logging.DEBUG
elif LOG_LEVEL_ENV_VAR == "info":
    LOG_LEVEL = logging.INFO
else:
    LOG_LEVEL = logging.INFO

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=LOG_LEVEL)
LOGGER = logging.getLogger(__name__)


VERSION = '1.04'  # TODO: make this automatic
CHANGELOG_URL = 'https://schafezp.com/schafezp/txkarmabot/blob/master/CHANGELOG.md'


LIST_OF_ADMINS = [65278791]


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


def types(func):
    """Used by bot handlers that respond with text.
    ChatAction.Typing is called which makes the bot look like it's typing"""
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        """function to wrap"""
        bot.send_chat_action(
            chat_id=update.message.chat_id,
            action=tg.ChatAction.TYPING)
        return func(bot, update, *args, **kwargs)
    return wrapped



#TODO: move this down into the main function
#this stops us from importing directly from this function: bad practice
#blocks here
conn = attempt_connect()


def reply(bot: tg.Bot, update: tg.Update):
    """Handler that's run when one user replies to another userself.
    This handler checks if an upvote or downvote are given"""
    reply_user = user_from_tg_user(update.message.reply_to_message.from_user)
    replying_user = user_from_tg_user(update.message.from_user)
    chat_id = str(update.message.chat_id)
    chat = Telegram_Chat(chat_id, update.message.chat.title)
    original_message = Telegram_Message(
        update.message.reply_to_message.message_id,
        chat.chat_id,
        reply_user.id,
        update.message.reply_to_message.text)
    reply_message = Telegram_Message(
        update.message.message_id,
        chat.chat_id,
        replying_user.id,
        update.message.text)
    reply_text = reply_message.message_text

    if re.match("^([\+pP][1-9][0-9]*|[Pp]{2}).*", reply_text):
        # if user tried to +1 self themselves
        # chat id is user_id when the user is talking 1 on 1 with the bot
        if(replying_user.id == update.message.reply_to_message.from_user.id and chat_id != str(reply_user.id)):
            default_respose = "USER_FIRST_NAME you cannot +1 yourself"
            response = pf.get_random_witty_response(conn)
            if response is None:
                response = default_respose

            message = response.replace("USER_FIRST_NAME", replying_user.first_name)
            bot.send_message(chat_id=chat_id, text=message)
        else:  # user +1 someone else
            pf.user_reply_to_message(
                replying_user,
                reply_user,
                chat,
                original_message,
                reply_message,
                1,
                conn)
            logging.debug("user replying other user")
            logging.debug(replying_user)
            logging.debug(reply_user)
    # user -1 someone else
    elif re.match("^([\-mM][1-9][0-9]*|[Dd]{2}).*", reply_text):
        pf.user_reply_to_message(replying_user, reply_user,
                                 chat, original_message, reply_message, -1, conn)
        logging.debug("user replying other user")
        logging.debug(replying_user)
        logging.debug(reply_user)


def start(bot, update):
    """Message sent by bot upon first 1 on 1 interaction with the bot"""
    bot.send_message(
        chat_id=update.message.chat_id,
        text="I'm a bot, please talk to me!")


@types
def show_version(bot, update, args):
    """Handler to show the current version"""
    message = f"Version: {VERSION}\nBot powered by Python."
    # harder to hack the bot if source code is obfuscated :p
    #message = message + "\nChangelog found at: " + changelog_url
    bot.send_message(chat_id=update.message.chat_id, text=message)


@types
def show_user_stats(bot, update, args):
    """Handler to return statistics on user"""
    # TODO: remove this boiler plate code somehow
    # without this if this is the first command run alone with the bot it will
    # fail due to psycopg2.IntegrityError: insert or update on table
    # "command_used" violates foreign key constraint
    # "command_used_chat_id_fkey"
    chat = Telegram_Chat(str(update.message.chat_id),
                         update.message.chat.title)
    pf.save_or_create_chat(chat, conn)

    chat_id = str(update.message.chat_id)
    if len(args) != 1:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="use command like: /userinfo username")
        return
    username = args[0]
    if username[0] == "@":
        username = username[1:]

    use_command(
        'userinfo', user_from_tg_user(
            update.message.from_user), str(
                update.message.chat_id), arguments=username)

    message = None
    try:
        result = pf.get_user_stats(username, chat_id, conn)
        message = """<b>Username:</b> {:s} Karma: {:d}
        Karma given out stats:
        Upvotes, Downvotes, Total Votes, Net Karma
        {:d}, {:d}, {:d}, {:d}"""
        message = message.format(
            result['username'],
            result['karma'],
            result['upvotes_given'],
            result['downvotes_given'],
            result['total_votes_given'],
            result['net_karma_given'])
    except pf.UserNotFound as _:
        message = f"No user with username: {username}"

    bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=tg.ParseMode.HTML)

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
    if rows is None:
        return "No karma for users in this chat"
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

@types
def show_karma(bot, update, args):
    """Handler show the karma in the chat"""
    use_command(
        'showkarma', user_from_tg_user(
            update.message.from_user), str(
                update.message.chat_id))
    logging.debug(f"Chat id: {str(update.message.chat_id)}")

    # returns username, first_name, karma
    chat_id = str(update.message.chat_id)
    message = format_show_karma_for_users_in_chat(chat_id)

    bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=tg.ParseMode.HTML)


@types
def show_chat_info(bot, update, args):
    """Handler to show information about current chat """
    use_command(
        'chatinfo', user_from_tg_user(
            update.message.from_user), str(
                update.message.chat_id))
    chat_id = str(update.message.chat_id)
    title = update.message.chat.title
    if title is None:
        title = "No Title"
    result = pf.get_chat_info(chat_id, conn)
    message = "<b>Chat Name:</b> {:s}\n Number of Users with Karma: {:d}\n Total Reply Count: {:d}".format(
        title, result['user_with_karma_count'], result['reply_count'])
    bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=tg.ParseMode.HTML)


@restricted
def am_i_admin(bot, update, args):
    """Handler to check if user is an admin"""
    message = "yes you are an admin"
    bot.send_message(chat_id=update.message.chat_id, text=message)


@types
def show_karma_personally(bot, update: tg.Update):
    """Conversation handler to allow users to check karma values through custom keyboard"""
    user_id = update.effective_user.id
    user: User = user_from_tg_user(update.effective_user)
    chat_id: str = str(update.message.chat_id)
    result = pf.get_chats_user_is_in(user_id, conn)
    use_command('checkchatkarmas', user, chat_id)

    keyboard = []
    if result is not None:
        for (chat_id, chat_name) in result:
            if chat_name is not None:
                logging.info(f"Chat name:{chat_name}")
                keyboard.append([tg.InlineKeyboardButton(chat_name, callback_data=chat_id)])
        reply_markup = tg.InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Please choose a chat:', reply_markup=reply_markup)
    else:
        update.message.reply_text("""No chats available.
        You can only see chats you have given or received karma in.""")


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

    show_user_handler = CommandHandler(
        'userinfo', show_user_stats, pass_args=True)
    dispatcher.add_handler(show_user_handler)

    chat_info_handler = CommandHandler(
        'chatinfo', show_chat_info, pass_args=True)
    dispatcher.add_handler(chat_info_handler)

    am_i_admin_handler = CommandHandler('amiadmin', am_i_admin, pass_args=True)
    dispatcher.add_handler(am_i_admin_handler)

    showversion_handler = CommandHandler(
        'version', show_version, pass_args=True)
    dispatcher.add_handler(showversion_handler)

    show_karma_personally_handler = CommandHandler(
        'checkchatkarmas', show_karma_personally)
    dispatcher.add_handler(show_karma_personally_handler)

    dispatcher.add_handler(CallbackQueryHandler(show_karma_personally_button_pressed))


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
