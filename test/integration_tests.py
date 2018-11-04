"""Runs integration test on the bot
"""
import os
import unittest
import re
from tgintegration import BotIntegrationClient
from karmabot.responses import START_BOT_RESPONSE, SUCCESSFUL_CLEAR_CHAT, SHOW_KARMA_NO_HISTORY_RESPONSE
from karmabot.commands_strings import START_COMMAND, CLEAR_CHAT_COMMAND, SHOW_KARMA_COMMAND, USER_INFO_COMMAND, CHAT_INFO_COMMAND, SHOW_KARMA_KEYBOARD_COMMAND
from .integration_common import Common_Integration
#TODO: move to import module structure invocation from script


class IntegrationTests(Common_Integration):
    """ Runs intergation tests"""
    client: BotIntegrationClient
    def setUp(self):
        self.setup_bot_client()


    def tearDown(self):
        self.tear_down_bot_client()

    @unittest.skip("dont care that this works for now")
    def test_start(self):
        """ Test start command"""
        response = self.client.send_command_await(START_COMMAND, num_expected=1)
        self.assertEqual(len(response.messages), 1)
        self.assertEqual(response.messages[0].text, START_BOT_RESPONSE)

    @unittest.skip("dont care that this works for now")
    def test_showkarma_works_on_empty_chat(self):
        """Clears the chat and tests that showkarma doesn't give a response"""
        clear_chat_response = self.client.send_command_await(CLEAR_CHAT_COMMAND, num_expected=1)
        self.assertEqual(len(clear_chat_response.messages), 1)
        self.assertEqual(clear_chat_response.messages[0].text, SUCCESSFUL_CLEAR_CHAT)
        show_karma_response = self.client.send_command_await(SHOW_KARMA_COMMAND, num_expected=1)
        self.assertEqual(len(show_karma_response.messages), 1)
        self.assertEqual(show_karma_response.messages[0].text, SHOW_KARMA_NO_HISTORY_RESPONSE)

    @unittest.skip("vote overriding broken right now")
    def test_votes_can_be_overriden(self):
        """Tests that if a message is +1 and then -1, the total net karma is 0"""
        self.client.send_command_await(CLEAR_CHAT_COMMAND, num_expected=1)
        show_karma_response = self.client.send_command_await(SHOW_KARMA_COMMAND, num_expected=1)
        self.assertEqual(len(show_karma_response.messages), 1)

        message = show_karma_response.messages[0]
        chat_id = message.chat.id
        message_id = message.message_id
        self.client.send_message(chat_id, "+1", reply_to_message_id=message_id)

        show_karma_response = self.client.send_command_await(SHOW_KARMA_COMMAND, num_expected=1)
        self.assertEqual(len(show_karma_response.messages), 1)
        bot_response = show_karma_response.messages[0].text

        bot_name_without_at = self.TEST_BOT_NAME[1:]
        does_bot_have_1_karma = bool(re.search(f"{bot_name_without_at}: 1", bot_response))
        self.assertTrue(does_bot_have_1_karma)

        self.client.send_message(chat_id, "-1", reply_to_message_id=message_id)
        show_karma_response = self.client.send_command_await(SHOW_KARMA_COMMAND, num_expected=1)
        self.assertEqual(len(show_karma_response.messages), 1)

        does_bot_have_zero_karma = bool(re.search(f"{bot_name_without_at}: 0", show_karma_response.messages[0].text))
        self.assertTrue(does_bot_have_zero_karma, '-1 on same message should override last vote')

    @unittest.skip("TEMPORARY")
    def test_upvote(self):
        """Tests that upvoting a message results in +1 karma"""
        self.client.send_command_await(CLEAR_CHAT_COMMAND)
        show_karma_response = self.client.send_command_await(SHOW_KARMA_COMMAND, num_expected=1)
        self.assertEqual(len(show_karma_response.messages), 1)
        message = show_karma_response.messages[0]
        chat_id = message.chat.id
        message_id = message.message_id
        self.client.send_message(chat_id, "+1", reply_to_message_id=message_id)
        show_karma_response = self.client.send_command_await(SHOW_KARMA_COMMAND, num_expected=1)
        self.assertEqual(len(show_karma_response.messages), 1)

        bot_name_without_at = self.TEST_BOT_NAME[1:]
        bot_response = show_karma_response.messages[0].text
        does_bot_have_1_karma = re.search(f"{bot_name_without_at}: 1", bot_response)
        self.assertTrue(does_bot_have_1_karma, "Bot should have 1 karma after 1 plus 1")

    @unittest.skip("dont care that this works for now")
    def test_downvote(self):
        """Tests that downvoting a message results in -1 karma"""
        self.client.send_command_await(CLEAR_CHAT_COMMAND)
        show_karma_response = self.client.send_command_await(SHOW_KARMA_COMMAND, num_expected=1)
        self.assertEqual(len(show_karma_response.messages), 1)
        message = show_karma_response.messages[0]
        chat_id = message.chat.id
        message_id = message.message_id
        self.client.send_message(chat_id, "-1", reply_to_message_id=message_id)
        show_karma_response = self.client.send_command_await(SHOW_KARMA_COMMAND, num_expected=1)
        self.assertEqual(len(show_karma_response.messages), 1)

        bot_name_without_at = self.TEST_BOT_NAME[1:]
        bot_response = show_karma_response.messages[0].text
        does_bot_have_1_karma = re.search(f"{bot_name_without_at}: -1", bot_response)
        self.assertTrue(does_bot_have_1_karma, "Bot should have 1 karma after 1 plus 1")


        #(chat_id, "+1", send_to_message_id=message_id)
        #print(f"Message id: {message.message_id}")
        #TOOD: how to send message as response to other message. Could be done directly with pyrogram

        #print(clear_chat_response)
        #print(dir(clear_chat_response))
        #clear chat
        #run showkarma (capture message id)
        #make sure has empty result
        #plus 1 showkarma message
        #make sure there is a number 1 in karma
    #TODO: test keyboard implementation
    #TODO: test non existent use cases (userstats where userid doesn't exist, etc)
    #TODO: host multiple bots with swarm and split integration tests amoung them

    @unittest.skip("TEMPORARY")
    def test_userinfo(self):
        # self.client.send_command_await(CLEAR_CHAT_COMMAND)
        # show_karma_response = self.client.send_command_await(SHOW_KARMA_COMMAND, num_expected=1)
        # self.assertEqual(len(show_karma_response.messages), 1)
        # message = show_karma_response.messages[0]
        # chat_id = message.chat.id
        # message_id = message.message_id
        # self.client.send_message(chat_id, "+1", reply_to_message_id=message_id)
        command = f"{USER_INFO_COMMAND} {self.TEST_BOT_NAME[1:]}"
        user_info_response = self.client.send_command_await(command, num_expected=1)
        self.assertEqual(len(user_info_response.messages), 1)

    @unittest.skip("TEMPORARY")
    def test_chatinfo(self):
        response = self.client.send_command_await(CHAT_INFO_COMMAND, num_expected=1)
        self.assertEqual(len(response.messages), 1)
        #TODO: check that number of users with karma is 2
        #TODO: Check total reply count

    @unittest.skip("test not yet implemented")
    def test_history_graph(self):
        #TODO: run command, check that a file asset is sent back
        #TODO: add another test case for showing a file not being sent when there is no data in the chat
        pass

    def test_check_chat_karmas(self):
        response = self.client.send_command_await(SHOW_KARMA_KEYBOARD_COMMAND, num_expected=1)
        keyboards = response.inline_keyboards
        # TODO: how to verify that there is history in another chat?
        #TODO: perhaps there should be a hidden flag to include chat with the bot
        self.assertTrue(keyboards is not None)
        self.assertTrue(len(keyboards) > 0)
        keyboard = keyboards[0]
        karma_result = keyboard.press_button_await(pattern=r'.*', num_expected=1)
        bot_name_without_at = self.TEST_BOT_NAME[1:]
        #print(karma_result)
        did_bot_provide_karma = re.search(f"{bot_name_without_at}", str(karma_result))
        self.assertTrue(did_bot_provide_karma)





if __name__ == "__main__":
    #TOOD: seperate this into test suites for the various features
    unittest.main()
