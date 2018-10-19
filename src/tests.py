import unittest
from utils import attempt_connect

def hello_world():
    return "hello world"
class MyFirstTests(unittest.TestCase):
    def test_hello(self):
        conn = attempt_connect(DATABASE="test_db")
        self.assertEqual(hello_world(), 'hello world')
    

if __name__ == '__main__':
    unittest.main()