import re
import logging

import telegram as tg
from telegram.ext import CallbackContext
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from .annotations import types
from .telegramservice import KarmabotDatabaseService, UserNotFound
from .formatters import format_show_karma_for_users_in_chat
from .models import Telegram_Chat, Telegram_Message, user_from_tg_user, User
from .responses import START_BOT_RESPONSE, FAILED_CLEAR_CHAT_DUE_TO_GROUPCHAT, SUCCESSFUL_CLEAR_CHAT
from .commands_strings import SHOW_KARMA_COMMAND, USER_INFO_COMMAND, CHAT_INFO_COMMAND, HISTORY_GRAPH_COMMAND, SHOW_KARMA_KEYBOARD_COMMAND

VERSION = '1.04'  # TODO: make this automatic

def start(bot, update):
    """Message sent by bot upon first 1 on 1 interaction with the bot"""
    bot.send_message(
        chat_id=update.message.chat_id,
        text=START_BOT_RESPONSE)


def error(bot, update, _error):
    """Log Errors caused by Updates."""
    logging.warning('Update "%s" caused error "%s"', update, _error)


@types
def show_version(bot, update, args):
    """Handler to show the current version"""
    message = f"Version: {VERSION}\nBot powered by Python."
    # harder to hack the bot if source code is obfuscated :p
    #message = message + "\nChangelog found at: " + changelog_url
    bot.send_message(chat_id=update.message.chat_id, text=message)


def gen_show_karma(dbservice: KarmabotDatabaseService):
    """Handler show the karma in the chat"""

    """ use_command(
        'showkarma', user_from_tg_user(
            update.message.from_user), str(
                update.message.chat_id)) """
    @types
    def show_karma(update: tg.Update, context: CallbackContext):
        # returns username, first_name, karma
        bot: tg.Bot = context.bot

        logging.debug(f"Chat id: {str(update.message.chat_id)}")
        user = user_from_tg_user(update.message.from_user)
        chat_id = str(update.message.chat_id)
        dbservice.use_command(SHOW_KARMA_COMMAND, user, chat_id)
        users_and_karma = dbservice.get_karma_for_users_in_chat(chat_id)
        message = format_show_karma_for_users_in_chat(users_and_karma)
        bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=tg.ParseMode.HTML)
    return show_karma

def gen_reply(dbservice: KarmabotDatabaseService):

    def reply(update: tg.Update, context: CallbackContext):
        """Handler that's run when one user replies to another userself.
        This handler checks if an upvote or downvote are given"""
        bot: tg.Bot = context.bot
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

        if re.match("^([+pP][1-9][0-9]*|[Pp]{2}).*", reply_text):
            # if user tried to +1 self themselves
            # chat id is user_id when the user is talking 1 on 1 with the bot
            if(replying_user.id == update.message.reply_to_message.from_user.id and chat_id != str(reply_user.id)):
                default_respose = "USER_FIRST_NAME you cannot +1 yourself"
                response = dbservice.get_random_witty_response()
                if response is None:
                    response = default_respose

                message = response.replace("USER_FIRST_NAME", replying_user.first_name)
                bot.send_message(chat_id=chat_id, text=message)
            else:  # user +1 someone else
                dbservice.user_reply_to_message(
                    replying_user,
                    reply_user,
                    chat,
                    original_message,
                    reply_message,
                    1)
                logging.debug("user replying other user")
                logging.debug(replying_user)
                logging.debug(reply_user)
        # user -1 someone else
        elif re.match("^([\-mM][1-9][0-9]*|[Dd]{2}).*", reply_text):
            dbservice.user_reply_to_message(
                replying_user,
                reply_user,
                chat,
                original_message,
                reply_message,
                -1)
            logging.debug("user replying other user")
            logging.debug(replying_user)
            logging.debug(reply_user)
    return reply


def gen_show_user_stats(db_service: KarmabotDatabaseService):
    @types
    def show_user_stats(update: tg.Update, context: CallbackContext, args):

        """Handler to return statistics on user"""
        # TODO: remove this boiler plate code somehow
        # without this if this is the first command run alone with the bot it will
        # fail due to psycopg2.IntegrityError: insert or update on table
        # "command_used" violates foreign key constraint
        # "command_used_chat_id_fkey"
        args = context.args
        bot = context.bot
        chat = Telegram_Chat(str(update.message.chat_id),
                             update.message.chat.title)
        db_service.save_or_create_chat(chat)

        user = user_from_tg_user(update.message.from_user)
        chat_id = str(update.message.chat_id)
        db_service.use_command(USER_INFO_COMMAND, user, chat_id)

        if len(args) != 1:
            bot.send_message(
                chat_id=update.message.chat_id,
                text="use command like: /userinfo username")
            return
        username = args[0]
        if username[0] == "@":
            username = username[1:]

        # use_command(
        #     'userinfo', user_from_tg_user(
        #         update.message.from_user), str(
        #         update.message.chat_id), arguments=username)

        message = None
        try:
            result = db_service.get_user_stats(username, chat_id)
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
        except UserNotFound as _:
            message = f"No user with username: {username}"

        bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=tg.ParseMode.HTML)

    return show_user_stats

def gen_show_chat_info(db_service: KarmabotDatabaseService):
    @types
    def show_chat_info(update: tg.Update, context: CallbackContext):
        """Handler to show information about current chat """

        bot = context.bot
        user = user_from_tg_user(update.message.from_user)
        chat_id = str(update.message.chat_id)
        db_service.use_command(CHAT_INFO_COMMAND, user, chat_id)
        title = update.message.chat.title
        if title is None:
            title = "No Title"
        result = db_service.get_chat_info(chat_id)
        message = "<b>Chat Name:</b> {:s}\n Number of Users with Karma: {:d}\n Total Reply Count: {:d}".format(
            title, result['user_with_karma_count'], result['reply_count'])
        bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=tg.ParseMode.HTML)
    return show_chat_info

def gen_show_history_graph(db_service: KarmabotDatabaseService):

    def show_history_graph(update: tg.Update, context: CallbackContext):
        """Handler to show a graph of upvotes/downvotes per day"""
        bot = context.bot

        chat_id = str(update.message.chat_id)
        chat_name = str(update.message.chat.title)
        user = user_from_tg_user(update.message.from_user)
        db_service.use_command(HISTORY_GRAPH_COMMAND, user, chat_id)
        if chat_name is None:
            chat_name = "Chat With Bot"
        result = db_service.get_responses_per_day(chat_id)
        logging.info(f"result: {result}")

        if result is None or result == []:
            bot.send_message(chat_id=update.message.chat_id, text="No responses for this chat")
            return

        bot.send_chat_action(
            chat_id=update.message.chat_id,
            action=tg.ChatAction.UPLOAD_PHOTO)

        days, responses = zip(*result)

        figure_name = f'/output/graph_{chat_id}.png'
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(days, responses)
        ax.set_ylabel('Upvotes and Downvotes')
        ax.set_xlabel('Day')
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_title(f'{chat_name}: User votes per day')
        fig.autofmt_xdate()
        fig.savefig(figure_name)


        bot.send_photo(chat_id=update.message.chat_id, photo=open(figure_name, 'rb'))
    return show_history_graph


def gen_clear_chat_with_bot(db_service: KarmabotDatabaseService):
    def clear_chat_with_bot(update: tg.Update, context: CallbackContext):
        """Clears chat with bot"""
        bot = context.bot
        chat_id = update.message.chat_id
        user_id = update.message.from_user.id
        if user_id != chat_id:
            bot.send_message(chat_id=update.message.chat_id, text=FAILED_CLEAR_CHAT_DUE_TO_GROUPCHAT)
            return
        bot.send_message(chat_id=update.message.chat_id, text=SUCCESSFUL_CLEAR_CHAT)
        db_service.clear_chat_with_bot(chat_id, user_id)

    return clear_chat_with_bot


def gen_show_karma_personally(db_service: KarmabotDatabaseService):
    @types
    def show_karma_personally(update: tg.Update, context: CallbackContext):
        """Conversation handler to allow users to check karma values through custom keyboard"""
        user_id = update.effective_user.id
        user: User = user_from_tg_user(update.effective_user)
        chat_id: str = str(update.message.chat_id)
        result = db_service.get_chats_user_is_in(user_id)
        db_service.use_command(SHOW_KARMA_KEYBOARD_COMMAND, user, chat_id)

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

    return show_karma_personally

def gen_show_karma_personally_button_pressed(db_service: KarmabotDatabaseService):
    def show_karma_personally_button_pressed(update: tg.Update, context: CallbackContext):
        """Runs /showkarma on chat the user_selected"""
        bot = context.bot
        query = update.callback_query
        chat_id: str = str(query.data)
        karma_rows = db_service.get_karma_for_users_in_chat(chat_id)
        message = format_show_karma_for_users_in_chat(karma_rows)
        chat_name = db_service.get_chat_name(chat_id)

        if chat_name is not None:
            message = f"<b>Chat name: {chat_name}</b>\n{message}"

        bot.edit_message_text(text=message,
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              parse_mode=tg.ParseMode.HTML)
    return show_karma_personally_button_pressed
