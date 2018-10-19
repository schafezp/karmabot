import unittest
from utils import attempt_connect
def clear_db_cmds():
    tables = ["telegram_user", "telegram_chat", "user_in_chat", "telegram_message", "user_reacted_to_message", "command_used"]
    cmds = ["truncate " + tablename + " cascade" for tablename in tables]
    conn = attempt_connect(DATABASE="test_db")
    with conn:
        with conn.cursor() as crs:
            for cmd in clear_db_cmds():
                print(cmd)
                crs.execute(cmd,[])

def hello_world():
    return "hello world"
class MyFirstTests(unittest.TestCase):
    def test_hello(self):
        
        self.assertEqual(hello_world(), 'hello world')
    

if __name__ == '__main__':
    unittest.main()