"""Runs integration test on the bot
"""
from tgintegration import BotIntegrationClient
import os

def main():
    """entrypoint for integration test"""
    API_ID = os.environ.get("API_ID")
    API_HASH = os.environ.get("API_HASH")
    TEST_BOT_NAME = os.environ.get("TEST_BOT_NAME")
    client = BotIntegrationClient(
        bot_under_test=TEST_BOT_NAME,
        session_name='./session/my_account',  # Arbitrary file path to the Pyrogram session file
        api_id=API_ID,  # See "Requirements" above, ...
        api_hash=API_HASH,  # alternatively use a `config.ini` file
        max_wait_response=15,  # Maximum timeout for bot responses
        min_wait_consecutive=2  # Minimum time to wait for consecutive messages
    )
    client.start()
    client.clear_chat()

    response = client.send_command_await("start", num_expected=1)
    assert response.num_messages == 1

if __name__ == "__main__":
    main()
