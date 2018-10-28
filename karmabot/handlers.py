from annotations import types
from telegramservice import KarmabotDatabaseService
from formatters import format_show_karma_for_users_in_chat
import logging
import telegram as tg

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