"""Manages class for telegram service.
"""
from typing import List, Tuple
import psycopg2
from customutils import attempt_connect
from dataclasses import dataclass
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


class PostgresKarmabotDatabaseService(KarmabotDatabaseService):
    """Does connections to postgres"""
    #TODO: trigger use_commmand on function invocations (perhaps add annotation?)
    def __init__(self, dbConfig: PostgresDBConfig):
        try:
            self.conn = psycopg2.connect(
                host=dbConfig.host,
                database=dbConfig.database,
                user=dbConfig.user,
                password=dbConfig.password)
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
        

class Neo4jKarmabotDatabaseService(KarmabotDatabaseService):
    """Does connections to neo4j"""
    pass

