import unittest
from py2neo import Graph



class Neo_Test(unittest.TestCase):
    def setUp(self):
        self.graph = Graph(host="neo4j", password="admin")
    def test_connect(self):
        print("show graph")
        with open("neo4j_unittest_setup.cql") as cql_setup_files:
            cql_lines = cql_setup_files.readlines()
            line = " ".join([line.replace("\n","") for line in cql_lines])
            print("line: " + line)
            self.graph.run(line)
            # for line in lines:
            #     if line != "\n":


        print(self.graph.run("MATCH (n) return n").to_table())

        # logging.info(self.graph.data("MATCH (n:User) return n"))


if __name__ == "__main__":
    unittest.main()

