import unittest
from karmabot.repo.neo4j_repo import *
from karmabot.models.neo4j_models import Message
import warnings
import uuid

#TODO: break tests into multiple classes

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

    def test_get_user_that_exists(self):
        user_id = "1"
        username = "@user1"
        user = get_user(self.graph, user_id)
        self.assertIsNotNone(user)
        self.assertEqual(username, user.user_name)

    def test_get_user_that_does_not_exist(self):
        user_id = "10231"
        user = get_user(self.graph, user_id)
        self.assertIsNone(user)

    def test_get_users(self):
        users = get_all_users(self.graph)
        self.assertEqual(len(users), 3)


    def test_get_users_in_chat(self):
        chat_id = "1"
        chat_name = "A fun chat"
        result = get_users_in_chat(self.graph, chat_id)
        self.assertIsNotNone(result)
        users, chat = result
        self.assertTrue(chat.chat_id == chat_id)
        self.assertTrue(chat.chat_name == chat_name)
        self.assertEqual(len(users), 2)

    def test_get_message(self):
        message_id = "1"
        chat_id = "1"
        user_id = "1"

        message = get_message(self.graph, message_id)
        self.assertIsNotNone(message)
        self.assertEqual(message.chat_id, chat_id)
        self.assertEqual(message.author_user_id, user_id)

    def test_create_message(self):
        message_id = "59"
        chat_id = "1"
        user_id = "1"
        message_text = "this is a message"
        message = Message(message_id, chat_id, user_id, message_text)
        result = get_message(self.graph, message.message_id)
        self.assertIsNone(result)
        create_or_update_message(self.graph, message)
        result = get_message(self.graph, message.message_id)
        self.assertIsNotNone(result)
        self.assertEqual(result.message_id, message_id)
        self.assertEqual(result.chat_id, chat_id)
        self.assertEqual(result.author_user_id, user_id)
        self.assertEqual(result.message_text, message_text)

    def test_update_message(self):
        message_id = "59"
        chat_id = "1"
        user_id = "1"
        message_text = "this is a message"
        message = Message(message_id, chat_id, user_id, message_text)
        create_or_update_message(self.graph, message)
        result = get_message(self.graph, message.message_id)
        self.assertIsNotNone(result)
        self.assertEqual(result.message_id, message_id)
        self.assertEqual(result.chat_id, chat_id)
        self.assertEqual(result.author_user_id, user_id)
        self.assertEqual(result.message_text, message_text)
        updated_message_text = "another message"
        message.message_text = updated_message_text
        create_or_update_message(self.graph, message)
        result = get_message(self.graph, message.message_id)
        self.assertEqual(result.message_text, updated_message_text)


    def test_get_users_in_chat_for_chat_not_exists(self):
        """ Verifies that if a bad chat_id is used none is returned"""

        chat_id = "not_a_valid_chat_id"
        result = get_users_in_chat(self.graph, chat_id)
        self.assertEqual(result, None)

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

    def test_karma_received_by_user(self):
        user_id = "1"
        chat_id = "1"
        pos, neg = get_karma_received_by_user_in_chat(self.graph, user_id, chat_id)
        self.assertEqual(pos, 1)
        self.assertEqual(neg, 0)

    def test_give_karma(self):
        user_id_1 = "1"
        user_id_2 = "3"
        chat_id = "1"
        message_1_id = str(uuid.uuid4())
        message_1 = Message(message_1_id, chat_id, user_id_1, "+1 reply to message 2")
        message_2_id = str(uuid.uuid4())
        message_2 = Message(message_2_id, chat_id, user_id_2, "good content")
        upvote_amount = 1
        pos, neg = get_karma_received_by_user_in_chat(self.graph, user_id_2, chat_id)
        user_2_karma = get_user_karma_in_chat(self.graph, user_id_2, chat_id)

        vote_on_message(self.graph, message_1, message_2, upvote_amount)

        pos_after, neg_after = get_karma_received_by_user_in_chat(self.graph, user_id_2, chat_id)
        user_2_karma_after = get_user_karma_in_chat(self.graph, user_id_2, chat_id)
        self.assertTrue("+1 karma should have been given", pos_after == pos + 1)
        self.assertEqual(user_2_karma + 1, user_2_karma_after,
                         "karma value should be updated on relationship")


    def test_get_user_karma_in_chat(self):
        user_id = "1"
        chat_id = "1"
        result = get_user_karma_in_chat(self.graph, user_id, chat_id)
        self.assertIsNotNone(result)
        self.assertEqual(result, 5)





if __name__ == "__main__":
    unittest.main()

