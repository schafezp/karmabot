from py2neo import Graph
from karmabot.models.neo4j_models import User, Chat
from typing import List, Tuple, Dict


def get_model_user_from_graph_user(user: Dict) -> User:
    """ Converts neo4j database user into application logic user"""
    return User(user["id"], user["username"], user["karma"])


def get_model_chat_from_graph_chat(chat: Dict) -> Chat:
    """ Converts neo4j database user into application logic user"""
    return Chat(chat["id"], chat["name"])


def get_all_users(g: Graph) -> List[User]:
    data = g.run("MATCH (n:User) return collect(n) as users").data()
    if len(data) == 0:
        return []

    users = [get_model_user_from_graph_user(user) for user in data[0]["users"]]
    return users


def get_users_in_chat(g: Graph, chat_id: str) -> Tuple[List[User], Chat]:
    command = "MATCH (n:User)-[:USER_IN_CHAT]-> (chat:Chat) where chat.id={chat_id} return collect(n) as users, chat"
    data = g.run(command, {"chat_id": chat_id}).data()
    #TODO: does this handle if multiple chats exist with same chat id? should be handled by constraint
    if len(data) == 0:
        return []

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
    if len(data) == 0:
        return 0, 0
    if len(data) == 1:
        row = data[0]
        if row["vote_type"] == 1:
            return row["vote_count"], 0
        else:
            return 0, row["vote_count"]
    if len(data) == 2:
        # query uses order by asc so [0] is positive
        return data[0]["vote_count"], data[1]["vote_count"]

    return 0,0

