"""Runs integration test on the bot
"""
import os
import unittest
from tgintegration import BotIntegrationClient
from responses import *

class IntegrationTests(unittest.TestCase):
    """ Runs intergation tests"""
    def setUp(self):
        """ Sets up the environment"""
        API_ID = os.environ.get("API_ID")
        API_HASH = os.environ.get("API_HASH")
        TEST_BOT_NAME = os.environ.get("TEST_BOT_NAME")
        if None in [API_HASH, API_ID, TEST_BOT_NAME]:
            print("API_ID, API_HASH, TEST_BOT_NAME not set")
            raise ValueError()

        
        
        client = BotIntegrationClient(
            bot_under_test=TEST_BOT_NAME,
            session_name='./session/my_account',  # Arbitrary file path to the Pyrogram session file
            api_id=API_ID,  # See "Requirements" above, ...
            api_hash=API_HASH,  # alternatively use a `config.ini` file
            max_wait_response=15,  # Maximum timeout for bot responses
            min_wait_consecutive=2  # Minimum time to wait for consecutive messages
        )
        client.start()
        #client.clear_chat()
        self.client = client
    def tearDown(self):
        self.client.stop()
        #pass
        
    def test_start(self):
        """ Test start command"""
        response = self.client.send_command_await("start", num_expected=1)
        #print(f"my constant: {MY_CONSTANT}")

        self.assertEqual(len(response.messages), 1)
        self.assertEqual(response.messages[0].text, "I'm a bot, please talk to me!")
        
        #assert response.num_messages == 1
        #self.assertTrue(self.client is not None)
        #self.assertEqual(response.num_messages, 1)
        
    #def test_showkarma(self):
        #clear chat
        #run showkarma (capture message id)
        #make sure has empty result
        #plus 1 showkarma message
        #make sure there is a number 1 in karma
        #pass


if __name__ == "__main__":
    unittest.main()
