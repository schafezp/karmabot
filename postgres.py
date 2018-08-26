import psycopg2

conn = psycopg2.connect(host="db_1", database="database", user="TEST_USER", password="TEST_PASS")