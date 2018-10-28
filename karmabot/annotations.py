import telegram as tg
from functools import wraps

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