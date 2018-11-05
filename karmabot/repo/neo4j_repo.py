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


