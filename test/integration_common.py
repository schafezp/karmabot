import os
import unittest
from tgintegration import BotIntegrationClient


class Common_Integration(unittest.TestCase):
    def setUp(self):
        self.setup_bot_client(self)

    def tearDown(self):
        self.tear_down_bot_client(self)

    def setup_bot_client(self):
        API_ID = os.environ.get("API_ID")
        API_HASH = os.environ.get("API_HASH")
        TEST_BOT_NAME = os.environ.get("TEST_BOT_NAME")
        if None in [API_HASH, API_ID, TEST_BOT_NAME]:
            print("API_ID, API_HASH, TEST_BOT_NAME not set")
            raise ValueError()

        # botname on test object
        self.TEST_BOT_NAME = TEST_BOT_NAME
        SESSION_NAME = './session/my_account'

        client = BotIntegrationClient(
            bot_under_test=TEST_BOT_NAME,
            session_name=SESSION_NAME,  # Arbitrary file path to the Pyrogram session file
            api_id=API_ID,  # See "Requirements" above, ...
            api_hash=API_HASH,  # alternatively use a `config.ini` file
            max_wait_response=15,  # Maximum timeout for bot responses
            min_wait_consecutive=2  # Minimum time to wait for consecutive messages
        )
        self.client = client
        #TODO: move start
        client.start()

    def tear_down_bot_client(test_suite):
        test_suite.client.stop()

#https://github.com/schafezp/tgintegration.git