import re
import logging

import telegram as tg
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from .annotations import types
from .telegramservice import KarmabotDatabaseService, UserNotFound
from .formatters import format_show_karma_for_users_in_chat
from .models import Telegram_Chat, Telegram_Message, user_from_tg_user
from .responses import START_BOT_RESPONSE

VERSION = '1.04'  # TODO: make this automatic

def start(bot, update):
    """Message sent by bot upon first 1 on 1 interaction with the bot"""
    bot.send_message(
        chat_id=update.message.chat_id,
        text=START_BOT_RESPONSE)


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
    def show_karma(bot, update, args):
        # returns username, first_name, karma
        logging.debug(f"Chat id: {str(update.message.chat_id)}")
        chat_id = str(update.message.chat_id)
        users_and_karma = dbservice.get_karma_for_users_in_chat(chat_id)
        message = format_show_karma_for_users_in_chat(users_and_karma)
        bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=tg.ParseMode.HTML)
    return show_karma

def gen_reply(dbservice: KarmabotDatabaseService):

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
    def show_user_stats(bot, update, args):
        """Handler to return statistics on user"""
        # TODO: remove this boiler plate code somehow
        # without this if this is the first command run alone with the bot it will
        # fail due to psycopg2.IntegrityError: insert or update on table
        # "command_used" violates foreign key constraint
        # "command_used_chat_id_fkey"
        chat = Telegram_Chat(str(update.message.chat_id),
                             update.message.chat.title)
        db_service.save_or_create_chat(chat)

        chat_id = str(update.message.chat_id)
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
    def show_chat_info(bot, update, args):
        """Handler to show information about current chat """
        # use_command(
        #     'chatinfo', user_from_tg_user(
        #         update.message.from_user), str(
        #             update.message.chat_id))
        chat_id = str(update.message.chat_id)
        title = update.message.chat.title
        if title is None:
            title = "No Title"
        result = db_service.get_chat_info(chat_id)
        message = "<b>Chat Name:</b> {:s}\n Number of Users with Karma: {:d}\n Total Reply Count: {:d}".format(
            title, result['user_with_karma_count'], result['reply_count'])
        bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=tg.ParseMode.HTML)
    return show_chat_info

def gen_show_history_graph(db_service: KarmabotDatabaseService):

    def show_history_graph(bot: tg.Bot, update: tg.Update):
        """Handler to show a graph of upvotes/downvotes per day"""
        chat_id = str(update.message.chat_id)
        chat_name = str(update.message.chat.title)
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
