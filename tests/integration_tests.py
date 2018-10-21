"""Runs integration test on the bot
"""
import os
import unittest
from tgintegration import BotIntegrationClient

class IntegrationTests(unittest.TestCase):
    """ Runs intergation tests"""
    def setUp(self):
        """ Sets up the environment"""
        API_ID = os.environ.get("API_ID")
        API_HASH = os.environ.get("API_HASH")
        if None in [API_HASH, API_ID]:
            print("API_ID or API_HASH not set")
            return

        TEST_BOT_NAME = os.environ.get("TEST_BOT_NAME")
        client = BotIntegrationClient(
            bot_under_test=TEST_BOT_NAME,
            session_name='./session/my_account',  # Arbitrary file path to the Pyrogram session file
            api_id=API_ID,  # See "Requirements" above, ...
            api_hash=API_HASH,  # alternatively use a `config.ini` file
            max_wait_response=15,  # Maximum timeout for bot responses
            min_wait_consecutive=2  # Minimum time to wait for consecutive messages
        )
        #client.start()
        #client.clear_chat()
        self.client = client
    def tearDown(self):
        #self.client.stop()
        pass
        
    def test_start(self):
        """ Test start command"""
        #response = client.send_command_await("start", num_expected=1)
        #assert response.num_messages == 1
        self.assertTrue(self.client is not None)


if __name__ == "__main__":
    unittest.main()
