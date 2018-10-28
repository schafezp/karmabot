"""Manages class for telegram service.
"""
from typing import List, Tuple, Optional
from dataclasses import dataclass
import psycopg2
from .models import User, Telegram_Chat, Telegram_Message, User_in_Chat
import logging

class InvalidDBConfig(Exception):
    pass

@dataclass
class PostgresDBConfig:
    """Information to connect to postgres"""
    host: str
    database: str
    user: str
    password: str


class KarmabotDatabaseService:
    """Base class for karmabot service"""
    def get_karma_for_users_in_chat(self, chat_id: str) -> List[Tuple[str, str, int]]:
        """Gets karma for user in chat"""
        raise NotImplementedError

    #TODO: don't return optional
    def get_random_witty_response(self) -> Optional[str]:
        raise NotImplementedError

    def save_or_create_user(self, user: User) -> User:
        raise NotImplementedError

    def save_or_create_chat(self, chat: Telegram_Chat) -> Telegram_Chat:
        raise NotImplementedError

    def user_reply_to_message(self,
            reply_from_user_unsaved: User,
            reply_to_user_unsaved: User,
            chat: Telegram_Chat,
            original_message: Telegram_Message,
            reply_message: Telegram_Message,
            karma: int):
        raise NotImplementedError

class PostgresKarmabotDatabaseService(KarmabotDatabaseService):
    """Does connections to postgres"""
    #TODO: trigger use_commmand on function invocations (perhaps add annotation?)
    def __init__(self, db_config: PostgresDBConfig) -> None:
        try:
            self.conn = psycopg2.connect(
                host=db_config.host,
                database=db_config.database,
                user=db_config.user,
                password=db_config.password)
        except psycopg2.OperationalError as oe:
            raise oe

    def get_karma_for_users_in_chat(self,
        chat_id: str) -> List[Tuple[str, str, int]]:
        """Returns username, firstname, karma for all telegram users in a given chat"""
        cmd = """select username, first_name, karma from telegram_user tu
            LEFT JOIN user_in_chat uic ON uic.user_id=tu.user_id
            where uic.chat_id=%s;"""
        with self.conn:
            with self.conn.cursor() as crs:
                # TODO: handle | psycopg2.ProgrammingError: relation "user_in_chat"
                # does not exist
                crs.execute(cmd, [chat_id])
                return crs.fetchall()

    def get_random_witty_response(self)-> Optional[str]:
        """Returns a random witty response. Uses USER_FIRST_NAME as replace string for actual user first name"""
        cmd = """SELECT response FROM attempted_self_plus_one_response ORDER BY RANDOM() LIMIT 1"""

        with self.conn:
            with self.conn.cursor() as crs:
                crs.execute(cmd, [])
                result = crs.fetchone()
                if result is not None:
                    return result[0]
                else:
                    return None

    def save_or_create_user(self, user: User) -> User:
        """Creates a user in database if not exists, otherwise update values and return the new database copy of the User"""
        with self.conn:
            with self.conn.cursor() as crs:  # I would love type hints here but psycopg2.cursor isn't a defined class
                selectcmd = "SELECT user_id, username, first_name, last_name from telegram_user tu where tu.user_id=%s"
                # TODO: upsert to update values otherwise username, firstname, lastname wont ever change
                # print("user with id: " + str(user_id) + "  not found: creating user")
                insertcmd = """INSERT into telegram_user
                (user_id, username, first_name, last_name) VALUES (%s,%s,%s,%s)
                ON CONFLICT (user_id) DO UPDATE
                SET username = EXCLUDED.username,
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name
                """
                crs.execute(insertcmd,
                            [user.get_user_id(),
                             user.get_username(),
                             user.get_first_name(),
                             user.get_last_name()])
                self.conn.commit()
                crs.execute(selectcmd, [user.get_user_id()])
                (user_id, username, first_name, last_name) = crs.fetchone()
                return User(user_id, username, first_name, last_name)

    def save_or_create_chat(self, chat: Telegram_Chat):
        """Creates chat if not exists otherwise updates chat_name"""
        with self.conn:
            with self.conn.cursor() as crs:  # I would love type hints here but psycopg2.cursor isn't a defined class
                insertcmd = """INSERT into telegram_chat
                (chat_id, chat_name) VALUES (%s,%s)
                ON CONFLICT (chat_id) DO UPDATE
                SET chat_name = EXCLUDED.chat_name"""
                crs.execute(insertcmd, [chat.chat_id, chat.chat_name])
                self.conn.commit()

    def does_chat_exist(self, chat_id: str) -> bool:
        """Returns true if chat exists"""
        with self.conn:
            with self.conn.cursor() as crs:  # I would love type hints here but psycopg2.cursor isn't a defined class
                selectcmd = "SELECT chat_id, chat_name FROM telegram_chat tc where tc.chat_id=%s"
                crs.execute(selectcmd, [chat_id])
                return crs.fetchone() is not None

    def save_or_create_user_in_chat(self,
            user: User,
            chat_id: str,
            change_karma=0) -> User_in_Chat:
        """Creates user in chat if not exists otherwise updates user_in_chat karma"""
        with self.conn:
            with self.conn.cursor() as crs:  # I would love type hints here but psycopg2.cursor isn't a defined class
                # TODO: instead of select first, do insert and then trap exception
                # if primary key exists
                # selectcmd = "SELECT user_id, chat_id, karma FROM user_in_chat uic where uic.user_id=%s AND uic.chat_id=%s"

                insertcmd_karma = """INSERT into user_in_chat
                    (user_id, chat_id, karma) VALUES (%s,%s,%s)
                    ON CONFLICT (user_id,chat_id) DO UPDATE SET karma = user_in_chat.karma + %s
                    RETURNING karma
                    """

                # TODO: used named parameters instead of %s to not have to repeat
                # these params
                crs.execute(
                    insertcmd_karma, [
                        user.get_user_id(), chat_id, change_karma, change_karma])

                row = crs.fetchone()
                self.conn.commit()
                karma = row[0]
                return User_in_Chat(user.id, chat_id, karma)

    def user_reply_to_message(self,
            reply_from_user_unsaved: User,
            reply_to_user_unsaved: User,
            chat: Telegram_Chat,
            original_message: Telegram_Message,
            reply_message: Telegram_Message,
            karma: int):
        """Processes a user replying to another users message with a given karma.
        Saves both users, both messages, updates user in chat and creates a user_reacted_to_message row"""
        user: User = self.save_or_create_user(reply_from_user_unsaved)
        reply_to_user: User = self.save_or_create_user(reply_to_user_unsaved)
        if not self.does_chat_exist(chat.chat_id):
            self.save_or_create_chat(chat)

        uic: User_in_Chat = self.save_or_create_user_in_chat(user, chat.chat_id)
        self.save_or_create_user_in_chat(reply_to_user, chat.chat_id)

        insert_message = """INSERT INTO telegram_message
        (message_id,chat_id, author_user_id, message_text)
        VALUES (%s,%s,%s,%s)
        ON CONFLICT (message_id) DO UPDATE
        SET message_text = EXCLUDED.message_text;
        """
        inserturtm = """INSERT INTO user_reacted_to_message
        (user_id,message_id,react_score,react_message_id)
        VALUES (%s,%s,%s,%s)"""

        # TODO: manage this with a constraint rather than having to select
        selecturtmunique = """SELECT react_score from user_reacted_to_message urtm where urtm.user_id=%s and urtm.message_id=%s"""
        # none if user hasn't reacted yet
        user_previous_react = None
        with self.conn:
            with self.conn.cursor() as crs:
                args_select_urtm = [uic.user_id, original_message.message_id]
                crs.execute(selecturtmunique, args_select_urtm)
                result = crs.fetchone()
                if result is not None:
                    user_previous_react = result[0]

        # TODO: add gaurd for karma == 1 or == -1 up higher
        if user_previous_react is None or user_previous_react != karma:
            if karma in (1, -1):
                self.save_or_create_user_in_chat(
                    reply_to_user, chat.chat_id, change_karma=karma)
            else:
                #TODO: move logging into handler
                logging.info(
                    f"invalid karma: {karma} passed to user_reply_to_message")
            with self.conn:
                with self.conn.cursor() as crs:
                    args_reply_message = [
                        reply_message.message_id,
                        chat.chat_id,
                        uic.user_id,
                        reply_message.message_text]
                    args_original_message = [
                        original_message.message_id,
                        chat.chat_id,
                        original_message.author_user_id,
                        original_message.message_text]
                    crs.execute(insert_message, args_reply_message)
                    crs.execute(insert_message, args_original_message)
                    argsurtm = [
                        uic.user_id,
                        original_message.message_id,
                        karma,
                        reply_message.message_id]
                    crs.execute(inserturtm, argsurtm)

class Neo4jKarmabotDatabaseService(KarmabotDatabaseService):
    """Does connections to neo4j"""
    pass

