"""Manages class for telegram service.
"""
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
import psycopg2
from .models.postgres_models import User, Telegram_Chat, Telegram_Message, User_in_Chat
import logging


class InvalidDBConfig(Exception):
    pass


class UserNotFound(Exception):
    """Returned when no valid user is found"""

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

    # TODO: make sure all my methods have docstrings
    def get_karma_for_users_in_chat(self, chat_id: str) -> List[Tuple[str, str, int]]:
        """Gets karma for user in chat"""
        raise NotImplementedError

    # TODO: determine if this should be on public api
    # def get_user_by_username(self, username: str) -> User:
    #     raise NotImplementedError
    # TODO: don't return optional
    def get_random_witty_response(self) -> Optional[str]:
        raise NotImplementedError

    def save_or_create_user(self, user: User) -> User:
        raise NotImplementedError

    def save_or_create_chat(self, chat: Telegram_Chat) -> Telegram_Chat:
        raise NotImplementedError

    def user_reply_to_message(
        self,
        reply_from_user_unsaved: User,
        reply_to_user_unsaved: User,
        chat: Telegram_Chat,
        original_message: Telegram_Message,
        reply_message: Telegram_Message,
        karma: int,
    ):
        raise NotImplementedError

    def get_user_stats(self, username: str, chat_id: str) -> Dict:
        raise NotImplementedError

    def get_chat_info(self, chat_id: str) -> Dict:
        raise NotImplementedError

    def get_chat_name(self, chat_id: str) -> Optional[str]:
        raise NotImplementedError

    # TODO: give option for using day/week as well as start/end date

    def get_responses_per_day(self, chat_id: str) -> Optional[Tuple[str, str]]:
        """Returns responses per day per chat"""
        raise NotImplementedError

    # TODO: throw exception if chat is not with bot
    def clear_chat_with_bot(self, chat_id, user_id):
        """Clears all history from a chat but only if chat_id matches user_id
            If chat_id matches user_id then the chat is a 1 on 1 with a bot."""
        raise NotImplementedError

    def get_chats_user_is_in(self, user_id: int) -> Optional[List[Tuple[str, str]]]:
        raise NotImplementedError

    def use_command(self, command: str, user: User, chat_id: str):
        raise NotImplementedError


class PostgresKarmabotDatabaseService(KarmabotDatabaseService):
    """Does connections to postgres"""

    # TODO: trigger use_commmand on function invocations (perhaps add annotation?)
    def __init__(self, db_config: PostgresDBConfig) -> None:
        try:
            self.conn = psycopg2.connect(
                host=db_config.host,
                database=db_config.database,
                user=db_config.user,
                password=db_config.password,
            )
        except psycopg2.OperationalError as oe:
            raise oe

    def get_karma_for_users_in_chat(self, chat_id: str) -> List[Tuple[str, str, int]]:
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

    def get_user_by_username(self, username: str) -> User:
        """Returns User given that user's username"""
        with self.conn:
            with self.conn.cursor() as crs:  # I would love type hints here but psycopg2.cursor isn't a defined class
                selectcmd = "SELECT user_id, username, first_name, last_name from telegram_user tu where tu.username=%s"
                crs.execute(selectcmd, [username])
                res = crs.fetchone()
                return User(res[0], res[1], res[2], res[3])

    def get_random_witty_response(self) -> Optional[str]:
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
                crs.execute(
                    insertcmd,
                    [
                        user.get_user_id(),
                        user.get_username(),
                        user.get_first_name(),
                        user.get_last_name(),
                    ],
                )
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

    def save_or_create_user_in_chat(
        self, user: User, chat_id: str, change_karma=0
    ) -> User_in_Chat:
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
                    insertcmd_karma,
                    [user.get_user_id(), chat_id, change_karma, change_karma],
                )

                row = crs.fetchone()
                self.conn.commit()
                karma = row[0]
                return User_in_Chat(user.id, chat_id, karma)

    def user_reply_to_message(
        self,
        reply_from_user_unsaved: User,
        reply_to_user_unsaved: User,
        chat: Telegram_Chat,
        original_message: Telegram_Message,
        reply_message: Telegram_Message,
        karma: int,
    ):
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
                    reply_to_user, chat.chat_id, change_karma=karma
                )
            else:
                # TODO: move logging into handler
                logging.info(f"invalid karma: {karma} passed to user_reply_to_message")
            with self.conn:
                with self.conn.cursor() as crs:
                    args_reply_message = [
                        reply_message.message_id,
                        chat.chat_id,
                        uic.user_id,
                        reply_message.message_text,
                    ]
                    args_original_message = [
                        original_message.message_id,
                        chat.chat_id,
                        original_message.author_user_id,
                        original_message.message_text,
                    ]
                    crs.execute(insert_message, args_reply_message)
                    crs.execute(insert_message, args_original_message)
                    argsurtm = [
                        uic.user_id,
                        original_message.message_id,
                        karma,
                        reply_message.message_id,
                    ]
                    crs.execute(inserturtm, argsurtm)

    # TODO: determine if this should be in the public api (super)
    def did_user_react_to_messages(self, username: str) -> bool:
        """Returns true if a user has responded to some messages"""
        select_user_replies = """select username, message_id, react_score, react_message_id  from telegram_user tu
                left join user_reacted_to_message urtm on urtm.user_id=tu.user_id
                where tu.username = %s"""
        reacted_messages_result = None
        with self.conn:
            with self.conn.cursor() as crs:
                crs.execute(select_user_replies, [username])
                reacted_messages_result = crs.fetchone()
                return reacted_messages_result is not None

    def get_karma_for_user_in_chat(self, username: str, chat_id: str) -> Optional[int]:
        """Returns karma for a particular user in chat
        if that uic does not exist, return None"""
        cmd = """select karma from telegram_user tu
            LEFT JOIN user_in_chat uic ON uic.user_id=tu.user_id
            where tu.username=%s AND uic.chat_id=%s"""
        with self.conn:
            with self.conn.cursor() as crs:
                # TODO: handle | psycopg2.ProgrammingError: relation "user_in_chat"
                # does not exist
                crs.execute(cmd, [username, chat_id])
                result = crs.fetchone()
                if result is not None:
                    return result[0]
                return result

    # TODO: pass in user_id
    # TODO: implement this as a stored procedure instead since there is a number of round trips
    # TODO: return some structure and then parse it

    def get_user_stats(self, username: str, chat_id: str) -> Dict:
        """Returns Dictionary of statistics for a user given a username"""
        user = self.get_user_by_username(username)
        if user is None:
            raise UserNotFound()
        user_has_reacts = self.did_user_react_to_messages(username)
        karma = self.get_karma_for_user_in_chat(username, chat_id)
        if karma is None:
            karma = 0

        output_dict = None
        if not user_has_reacts:
            output_dict = {
                "username": username,
                "karma": karma,
                "upvotes_given": 0,
                "downvotes_given": 0,
                "total_votes_given": 0,
                "net_karma_given": 0,
            }
        else:
            # how many reacts given out by user
            how_many_user_reacted_to_stats = """select react_score, count(react_score)from
                (select username, message_id, react_score, react_message_id  from telegram_user tu
                left join user_reacted_to_message urtm on urtm.user_id=tu.user_id
                where tu.username = %s) as sub left join telegram_message tm on  tm.message_id= sub.message_id
                where tm.chat_id=%s group by react_score;"""
            # TODO: implement how many reacts recieved by user
            negative_karma_given = 0
            positive_karma_given = 0
            with self.conn:
                with self.conn.cursor() as crs:
                    crs.execute(how_many_user_reacted_to_stats, [username, chat_id])
                    rows = crs.fetchall()
                    # there are only two rows
                    for row in rows:
                        if row[0] == -1:
                            negative_karma_given = int(row[1])
                        if row[0] == 1:
                            positive_karma_given = int(row[1])

            # TODO: make this output type a class instead to bundle this info
            output_dict = {
                "username": username,
                "karma": karma,
                "upvotes_given": positive_karma_given,
                "downvotes_given": negative_karma_given,
                "total_votes_given": positive_karma_given + negative_karma_given,
                "net_karma_given": positive_karma_given - negative_karma_given,
            }
        return output_dict

    def get_chat_info(self, chat_id: str) -> Dict:
        """Returns Dictionary of statistics for a chat given a chat_id"""
        count_reacts_cmd = """select count(tm.message_id) from user_reacted_to_message urtm
    left join telegram_message tm ON tm.message_id = urtm.message_id
    where tm.chat_id=%s"""
        select_user_with_karma_count = """
        select count(*) from telegram_chat tc
        left join user_in_chat uic on uic.chat_id = tc.chat_id
        where tc.chat_id=%s
        """
        with self.conn:
            with self.conn.cursor() as crs:
                reply_count = None
                user_with_karma_count = None
                crs.execute(count_reacts_cmd, [chat_id])
                result = crs.fetchone()
                if result is not None:
                    reply_count = result[0]
                else:
                    reply_count = 0

                crs.execute(select_user_with_karma_count, [chat_id])
                result = crs.fetchone()
                if result is not None:
                    user_with_karma_count = result[0]
                else:
                    user_with_karma_count = 0
                return {
                    "reply_count": reply_count,
                    "user_with_karma_count": user_with_karma_count,
                }

    def get_responses_per_day(self, chat_id: str) -> Optional[Tuple[str, str]]:
        """Returns responses per day per chat"""
        cmd = """select date_trunc('day',tm.message_time ) "day", count(*) as result_nums
                    from user_reacted_to_message urtm 
                    LEFT JOIN telegram_message tm ON tm.message_id=urtm.message_id
                    WHERE tm.chat_id = %s AND tm.message_time is not null
                    group by 1
                    order by 1"""
        with self.conn:
            with self.conn.cursor() as crs:
                crs.execute(cmd, [chat_id])
                return crs.fetchall()

    def clear_chat_with_bot(self, chat_id, user_id):
        if chat_id != user_id:
            raise ValueError("Not a chat with a bot. Don't delete group chats")

        chat_id_str = str(chat_id)
        # delete user_in_chat
        del_user_in_chat_cmd = "DELETE FROM user_in_chat uic WHERE uic.chat_id = %s"

        # TODO: delete user_reacted_to_message find all message in chat, find all urtm with those messages then delete them
        del_user_reacted_to_message_cmd = """DELETE FROM user_reacted_to_message urtmd WHERE id IN
            (select urtm.id as user_reacted_to_message_id FROM (select tm.message_id from telegram_message tm where tm.chat_id = %s) as message_in_chat
            LEFT JOIN user_reacted_to_message urtm on urtm.message_id=message_in_chat.message_id);"""

        # delete all telegram_messages with matching chat id
        del_telegram_messages = """DELETE FROM user_reacted_to_message urtmd WHERE id IN
            (select urtm.id as user_reacted_to_message_id FROM (select tm.message_id from telegram_message tm where tm.chat_id = %s) as message_in_chat
            LEFT JOIN user_reacted_to_message urtm on urtm.message_id=message_in_chat.message_id);"""

        del_command_used = """DELETE FROM command_used cu where chat_id=%s"""
        with self.conn:
            with self.conn.cursor() as crs:
                crs.execute(del_user_in_chat_cmd, [chat_id_str])
                crs.execute(del_user_reacted_to_message_cmd, [chat_id_str])
                crs.execute(del_telegram_messages, [chat_id_str])
                crs.execute(del_command_used, [chat_id_str])

    # TODO: don't return optional

    def get_chats_user_is_in(self, user_id: int) -> Optional[List[Tuple[str, str]]]:
        """Returns a list of chat_ids and chat names """
        cmd = """SELECT tc.chat_id, tc.chat_name from user_in_chat uic
        LEFT JOIN telegram_chat tc on tc.chat_id = uic.chat_id
        where uic.user_id = %s
        """
        with self.conn:
            with self.conn.cursor() as crs:
                crs.execute(cmd, [user_id])
                return crs.fetchall()

    def get_chat_name(self, chat_id: str) -> Optional[str]:
        """Returns chat name"""
        cmd = """select chat_name from telegram_chat tc where tc.chat_id=%s"""
        with self.conn:
            with self.conn.cursor() as crs:
                crs.execute(cmd, [chat_id])
                result = crs.fetchone()
                if result is None:
                    return None
                else:
                    return result[0]  # unpack

    def create_chat_if_not_exists(self, chat_id: str):
        """Creates chat if not exists otherwise does nothing"""
        with self.conn:
            with self.conn.cursor() as crs:  # I would love type hints here but psycopg2.cursor isn't a defined class
                insertcmd = """INSERT into telegram_chat
                    (chat_id) VALUES (%s)
                    ON CONFLICT (chat_id) DO NOTHING"""
                crs.execute(insertcmd, [chat_id])
                self.conn.commit()

    def use_command(self, command: str, user: User, chat_id: str, arguments=""):
        """Handler to log when commands are used and with which arguments"""
        self.create_chat_if_not_exists(chat_id)
        self.save_or_create_user(user)

        insertcmd = """INSERT INTO command_used (command,arguments,user_id,chat_id) VALUES (%s,%s,%s,%s)"""
        with self.conn:
            with self.conn.cursor() as crs:
                crs.execute(insertcmd, [command, arguments, user.id, chat_id])


class Neo4jKarmabotDatabaseService(KarmabotDatabaseService):
    """Does connections to neo4j"""

    pass
