import unittest
from py2neo import Graph, Node
from karmabot.repo.neo4j_repo import get_all_users, get_users_in_chat, get_karma_given_by_user_in_chat
import warnings


class Neo_Test(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter('ignore', category=ImportWarning)
        self.graph = Graph(host="localhost", password="admin")
        self.loadDb()

    def loadDb(self):
        self.graph.run("match (n) detach delete n")
        with open("neo4j_unittest_setup.cql") as cql_setup_files:
            cql_lines = cql_setup_files.readlines()
            line = " ".join([line.replace("\n", "") for line in cql_lines])
            self.graph.run(line)

    def test_get_users(self):
        test_karma_values = [-1, 3, 5]
        users = get_all_users(self.graph)
        karma = [user.karma for user in users]
        karma.sort()
        self.assertTrue(test_karma_values.sort() == karma.sort())

    def test_get_users_in_chat(self):
        chat_id = "1"
        chat_name = "A fun chat"
        users, chat = get_users_in_chat(self.graph, chat_id)
        self.assertTrue(chat.chat_id == chat_id)
        self.assertTrue(chat.chat_name == chat_name)

    def test_get_karma_given_by_user(self):
        user_id = "3"
        chat_id = "1"
        votes = get_karma_given_by_user_in_chat(self.graph, user_id, chat_id)
        self.assertEqual(votes[0], 1)
        self.assertEqual(votes[1], 0)
        chat_id = "2"

        votes = get_karma_given_by_user_in_chat(self.graph, user_id, chat_id)
        self.assertEqual(votes[0], 0)
        self.assertEqual(votes[1], 1)




if __name__ == "__main__":
    unittest.main()

