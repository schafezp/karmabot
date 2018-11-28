"""Manages class for telegram service.
"""
from typing import List, Tuple, Optional, Dict
from karmabot.models.postgres_models import User, Telegram_Chat, Telegram_Message, User_in_Chat

class InvalidDBConfig(Exception):
    pass

class UserNotFound(Exception):
    """Returned when no valid user is found"""
    pass

class KarmabotDatabaseService:
    """Base class for karmabot service"""
    #TODO: make sure all my methods have docstrings
    def get_karma_for_users_in_chat(self, chat_id: str) -> List[Tuple[str, str, int]]:
        """Gets karma for user in chat"""
        raise NotImplementedError

    #TODO: determine if this should be on public api
    # def get_user_by_username(self, username: str) -> User:
    #     raise NotImplementedError
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

    #TODO: throw exception if chat is not with bot
    def clear_chat_with_bot(self, chat_id, user_id):
        """Clears all history from a chat but only if chat_id matches user_id
            If chat_id matches user_id then the chat is a 1 on 1 with a bot."""
        raise NotImplementedError

    def get_chats_user_is_in(self, user_id: int) -> Optional[List[Tuple[str, str]]]:
        raise NotImplementedError

    def use_command(self, command: str, user: User, chat_id: str):
        raise NotImplementedError




class Neo4jKarmabotDatabaseService(KarmabotDatabaseService):
    """Does connections to neo4j"""
    pass

