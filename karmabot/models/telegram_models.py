""" These are the models that will be used for abstraction by the service

"""
from typing import Optional
from dataclasses import dataclass


@dataclass
class User:
    user_id: int
    first_name: str
    last_name: Optional[str]
    username: Optional[str]


@dataclass
class Telegram_Chat:
    chat_id: str
    chat_name: str


@dataclass
class Telegram_Message:
    id: int
    chat_id: str
    author_user_id: int
    message_text: str


@dataclass
class User_Reacted_to_Message:
    """ In Postgres data model user_in_chat_id is used instead of user_id
    """

    id: int
    user_id: int
    chat_id: int
    react_score: int
    react_message_id: str


# Used to convert telegram_bot object to telegram_model
def user_from_tg_user(user) -> User:
    """Creates a User object from a Telegram User object """
    return User(user.id, user.username, user.first_name, user.last_name)


def message_from_tg_message(message):
    """Creates a Telegram_message object from a Telegram message passed into the bot"""
    return Telegram_Message(
        message.message_id, message.chat.id, message.from_user.id, message.text
    )
