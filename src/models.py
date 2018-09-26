"""This module stores the models for the telegram bot"""
from typing import Optional
import telegram as tg





class User(object):
    """
    A representation of a telegram user
    """
    id: int
    __karma: int
    first_name: str
    last_name: Optional[str]
    username: Optional[str]

    def __init__(
            self,
            user_id: int,
            username: str,
            first_name: str,
            last_name: str) -> None:
        self.__karma = 0
        self.id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name

    def get_karma(self):
        """Returns karma for user"""
        return self.__karma

    def get_username(self):
        """Returns username for user"""
        return self.username

    def get_user_id(self):
        """Returns user_id for user"""
        return self.id

    def get_first_name(self):
        """Returns first name for user"""
        return self.first_name

    def get_last_name(self):
        """Returns last name for user"""
        return self.last_name

    def __str__(self):
        """Returns string represntation of userr"""
        if self.username is not None:
            message = "Username: " + self.username + \
                " karma: " + str(self.get_karma())
            # clean this logic up
            message = message + " first: " + \
                str(self.get_first_name()) + " last: " + str(self.get_last_name())
            return message
        else:
            return "First Name: " + self.first_name + \
                " karma: " + str(self.get_karma())


class User_in_Chat(object):
    """Model for user_in_chat row"""
    user_id: int
    chat_id: str
    karma: int

    def __init__(self, user_id: int, chat_id: str, karma: int) -> None:
        self.user_id = user_id
        self.chat_id = chat_id
        self.karma = karma


class Telegram_Chat(object):
    """Model for telegram_chat row"""
    chat_id: str
    chat_name: str

    def __init__(self, chat_id: str, chat_name: str) -> None:
        self.chat_id = chat_id
        self.chat_name = chat_name


class Telegram_Message(object):
    """Model for telegram_message row"""
    message_id: int
    chat_id: str
    author_user_id: int
    message_text: str

    def __init__(
            self,
            message_id: int,
            chat_id: str,
            author_user_id: int,
            message_text: str) -> None:
        self.message_id = message_id
        self.message_text = message_text
        self.chat_id = chat_id
        self.author_user_id = author_user_id


class User_reacted_to_message(object):
    """Model for user_reacted_to_message row"""
    id: int
    user_in_chat_id: int
    message_id: int
    react_score: int
    react_message_id: str

    def __init__(
            self,
            user_id,
            user_in_chat_id,
            message_id,
            react_score,
            react_message_id):
        self.id = user_id
        self.user_in_chat_id = user_in_chat_id
        self.message_id = message_id
        self.react_score = react_score
        self.react_message_id = react_message_id


#TODO: move these helpers functions elsewhere
def user_from_tg_user(user: tg.User) -> User:
    """Creates a User object from a Telegram User object """
    return User(user.id, user.username, user.first_name, user.last_name)


def message_from_tg_message(message: tg.Message):
    """Creates a Telegram_message object from a Telegram message passed into the bot"""
    return Telegram_Message(
        message.message_id,
        message.chat.id,
        message.from_user.id,
        message.text)
