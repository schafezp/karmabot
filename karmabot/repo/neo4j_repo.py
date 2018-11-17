"""Module used to encapsulate database query logic"""
from py2neo import Graph
from karmabot.models.neo4j_models import User, Chat
from typing import List, Tuple, Dict, Optional

# ------------- Database helpers ---------------

def get_model_user_from_graph_user(user: Dict) -> User:
    """ Converts neo4j database user into application logic user"""
    return User(user["id"], user["username"], user["karma"])


def get_model_chat_from_graph_chat(chat: Dict) -> Chat:
    """ Converts neo4j database user into application logic user"""
    return Chat(chat["id"], chat["name"])

def convert_vote_types_from_dict_to_tuple(data: List, type_key, count_key) -> Tuple[int, int]:
    """Requires order by type_key asc otherwise not guaranteed correct
    Data is a list.
    If list has 0 things then 0 positive and 0 negative votes were given.
    If list has 1 things then type_key might be 1 for positive or -1 for negative vote.
    If list has 2 things then the first one should be positive due to vote by asc

    :return: (positive votes, negative votes)
    """
    if len(data) == 0:
        return 0, 0
    if len(data) == 1:
        row = data[0]
        if row[type_key] == 1:
            return row[count_key], 0
        else:
            return 0, row[count_key]
    if len(data) == 2:
        # query uses order by asc so [0] is positive
        return data[1][count_key], data[0][count_key]

    return 0, 0


# ------------- Database calls ---------------

def get_all_users(g: Graph) -> List[User]:
    data = g.run("MATCH (n:User) return collect(n) as users").data()
    if len(data) == 0:
        return []

    users = [get_model_user_from_graph_user(user) for user in data[0]["users"]]
    return users

def get_user(g: Graph, user_id: str)-> Optional[User]:
    data = g.run("MATCH (n:User) where n.id = {user_id} return n as user", {"user_id": user_id}).data()
    if data == []:
        return None
    #TODO: consider raising exception here
    if len(data) > 1:
        return None
    else:
        return get_model_user_from_graph_user(data[0]["user"])


def get_users_in_chat(g: Graph, chat_id: str) -> Optional[Tuple[List[User], Chat]]:
    """ Returns all the users in a given chat. If chat does not exist returns none
    TODO: throw exception if chat not found?
    :param g:
    :param chat_id:
    :return: Tuple of list of users and chat they are a member of. None if chat does not exist.
    """

    command = "MATCH (n:User)-[:USER_IN_CHAT]-> (chat:Chat) where chat.id={chat_id} return collect(n) as users, chat"
    data = g.run(command, {"chat_id": chat_id}).data()
    if len(data) == 0:
        return None

    users = [get_model_user_from_graph_user(user) for user in data[0]["users"]]
    chat = get_model_chat_from_graph_chat(data[0]["chat"])

    return users, chat


def get_karma_given_by_user_in_chat(g: Graph, user_id: str, chat_id: str) -> Tuple[int, int]:
    """Given a user and a chat, returns how much karma that user has given in that chat; seperated by positive and negative

    :param g: The graph
    :param user_id:
    :param chat_id:
    :return: (positive votes, negative votes)
    """
    command = """MATCH (user:User)-[:AUTHORED_MESSAGE]->(message:Message)-[r:REPLIED_TO]->(message_replied_to:Message)
    MATCH (message:Message)-[:WRITTEN_IN_CHAT]->(chat:Chat)
    where user.id= {user_id}
    and chat.id= {chat_id}
    return distinct(r.vote) as vote_type, count(r.vote) as vote_count
    order by vote_type asc;"""

    data = g.run(command, {"user_id": user_id, "chat_id": chat_id}).data()
    return convert_vote_types_from_dict_to_tuple(data, "vote_type", "vote_count")

def get_karma_received_by_user_in_chat(g: Graph, user_id: str, chat_id: str) -> Tuple[int,int]:
    command = """MATCH (user:User)-[:AUTHORED_MESSAGE]->(message_replied_to:Message)<-[r:REPLIED_TO]-(message:Message)
    MATCH (message:Message)-[:WRITTEN_IN_CHAT]->(chat:Chat)
    where user.id= {user_id}
    and chat.id= {chat_id}
    return distinct(r.vote) as vote_type, count(r.vote) as vote_count
    order by vote_type asc;"""
    data = g.run(command, {"user_id": user_id, "chat_id": chat_id}).data()
    return convert_vote_types_from_dict_to_tuple(data, "vote_type", "vote_count")

# Section for helpers

