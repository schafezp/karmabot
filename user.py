import telegram as tg
from typing import Optional

class User(object):
    """
    A representation of a telegram user
    """
    def __init__(self, user: tg.User ):
        self.__karma = 0
        self.id : int = user.id
        self.first_name :  str = user.first_name
        self.last_name : Optional[str] = user.last_name
        self.username : Optional[str] = user.username
    def get_karma(self):
        return self.__karma
    def give_karma(self):
        self.__karma = self.__karma + 1
    def remove_karma(self):
        self.__karma = self.__karma - 1
    def __str__(self):
        if self.username is not None:
            return "Username: " + self.username + " karma: " + str(self.get_karma())
        else:
            return "First Name: " + self.first_name + " karma: " + str(self.get_karma())
