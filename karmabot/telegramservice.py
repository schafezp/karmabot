"""Manages class for telegram service.
"""
class KarmabotDatabaseService:
    """Base class for karmabot service"""
    def upvote(self, user, user_message, reply_to_message):
        raise NotImplementedError


class PostgresKarmabotDatabaseService(KarmabotDatabaseService):
    """Does connections to postgres"""
    pass

class Neo4jKarmabotDatabaseService(KarmabotDatabaseService):
    """Does connections to neo4j"""
    pass

