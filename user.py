import telegram as tg

class User(object):
    """
    A representation of a telegram user
    """
    def __init__(self, user: tg.User ):
        self.__karma = 0
        self.id = user.id
        self.first_name = user.first_name
        self.last_name = user.last_name
        self.username = user.username
    def get_karma(self):
        return self.__karma
    def give_karma(self):
        self.__karma = self.__karma + 1
    def remove_karma(self):
        self.__karma = self.__karma - 1
    def __str__(self):
            return "Username: " + self.username + " karma: " + str(self.get_karma())
