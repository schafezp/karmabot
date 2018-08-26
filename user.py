import telegram as tg
from typing import Optional

def user_from_tg_user(user : tg.User):
    return User(user.id, user.first_name, user.last_name, user.username)
def message_from_tg_message(message :tg.Message):
    return Telegram_message(message.message_id, message.chat.id, message.from_user.id, message.text)

class User(object):
    """
    A representation of a telegram user
    """
    id :int
    first_name: str
    last_name: Optional[str]
    username : Optional[str]


    def __init__(self, id:int, username: str, first_name:str, last_name:str):
        self.__karma = 0
        self.id = id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name

    #TODO: write function to create User from there params
    """ def __init__(self, user: tg.User ):
        self.__karma = 0
        self.id : int = user.id
        self.first_name :  str = user.first_name
        self.last_name : Optional[str] = user.last_name
        self.username : Optional[str] = user.username """


    def get_karma(self):
        return self.__karma
    def get_username(self):
        return self.username
    def give_karma(self):
        self.__karma = self.__karma + 1
    def remove_karma(self):
        self.__karma = self.__karma - 1
    def get_user_id(self):
        return self.id
    def get_first_name(self):
        return self.first_name
    def get_last_name(self):
        return self.last_name
    def __str__(self):
        if self.username is not None:
            message = "Username: " + self.username + " karma: " + str(self.get_karma())
            #clean this logic up
            message = message + " first: " + self.get_first_name() + " last: " + self.get_last_name()
            return message
        else:
            return "First Name: " + self.first_name + " karma: " + str(self.get_karma())


class User_in_chat(object):
    id :int
    user_id: int
    chat_id: int
    karma: int

    def __init__(self, id : int, user_id : int, chat_id: int, karma: int):
        self.id = id
        self.user_id = user_id
        self.chat_id = chat_id
        self.karma = karma

class Telegram_chat(object):
    chat_id: int
    chat_name: str
    def __init__(self,chat_id: int, chat_name: str):
        self.chat_id = chat_id
        self.chat_name = chat_name
class Telegram_message(object):
    message_id: int
    chat_id: int
    author_user_in_chat_id: int
    message_text: str
    def __init__(self, message_id: int, chat_id: int, author_user_in_chat_id: int, message_text: str):
        self.message_id = message_id
        self.message_text = message_text
        self.chat_id = chat_id
        self.author_user_in_chat_id = author_user_in_chat_id


class User_reacted_to_message(object):
    id: int
    user_in_chat_id: int
    message_id: int
    react_score: int
    react_message_id: str
    def __init__(self,id,user_in_chat_id, message_id, react_score, react_message_id):
        self.id = id
        self.user_in_chat_id = user_in_chat_id
        self.message_id = message_id
        self.react_score = react_score
        self.react_message_id = react_message_id




