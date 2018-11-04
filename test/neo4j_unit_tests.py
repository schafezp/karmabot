import unittest
from py2neo import Graph


class Neo_Test(unittest.TestCase):
    def setUp(self):
        self.graph = Graph(host="neo4j", password="admin")
    def test_connect(self):
        print(self.graph)
        print(self.graph.run("MATCH (n:User) return n"))

        # logging.info(self.graph.data("MATCH (n:User) return n"))


if __name__ == "__main__":
    unittest.main()

