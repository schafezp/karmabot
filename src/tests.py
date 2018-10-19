"""
Module for testing the project.
"""
import unittest
from utils import attempt_connect
def clear_db_cmds():
    """ Clears the database"""
    tables = ["telegram_user", "telegram_chat", "user_in_chat", "telegram_message", "user_reacted_to_message", "command_used"]
    cmds = ["truncate " + tablename + " cascade" for tablename in tables]
    conn = attempt_connect(DATABASE="test_db")
    with conn:
        with conn.cursor() as crs:
            for cmd in cmds:
                print(cmd)
                crs.execute(cmd, [])

def hello_world():
    """returns hello world"""
    return "hello world"
class MyFirstTests(unittest.TestCase):
    """Test class"""
    def test_hello(self):
        """tests hello_world()"""
        self.assertEqual(hello_world(), 'hello world')


if __name__ == '__main__':
    unittest.main()
