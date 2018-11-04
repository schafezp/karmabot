import unittest
from py2neo import Graph, Node
from karmabot.repo.neo4j_repo import get_all_users

class Neo_Test(unittest.TestCase):
    def setUp(self):
        self.graph = Graph(host="neo4j", password="admin")
        self.graph.run("match (n) detach delete n")
        with open("neo4j_unittest_setup.cql") as cql_setup_files:
            cql_lines = cql_setup_files.readlines()
            line = " ".join([line.replace("\n", "") for line in cql_lines])
            self.graph.run(line)

    def test_get_users(self):
        data = self.graph.run("MATCH (n:User) return n").data()
        test_karma_values = [5,3,-1]
        users = get_all_users(self.graph)
        karma = [users.karma for user in users]
        self.assertTrue(test_karma_values == karma)

if __name__ == "__main__":
    unittest.main()

