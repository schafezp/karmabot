"""
All handlers go here. Putting them in one place will make it easier to mock the services.
"""
from models import User, Telegram_Message


def user_plus_or_minus_one(author_user: User, reply_to_user: User, chat_id: str, original_message: Telegram_Message, reply_message: Telegram_Message):
    """When user plus or minus one"""

    pass
    