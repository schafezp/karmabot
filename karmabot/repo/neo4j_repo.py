from py2neo import Graph
from karmabot.models.neo4j_models import User


def get_all_users(g: Graph) -> User:
    data = g.run("MATCH (n:User) return n").data()
    users = []
    for row in data:
        d = row['n']
        users.append(User(d['userid'],d['username'], d['karma']))
    return users


