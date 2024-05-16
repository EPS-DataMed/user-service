import psycopg2
from psycopg2.extras import RealDictCursor
import time

class Database:
    _instance = None

    def __new__(cls, test=False, test_cursor=None, test_conn=None):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._conn = None
            cls._instance._cursor = None
            cls._instance._connect_db(test, test_cursor, test_conn)
        return cls._instance

    def _connect_db(self, test, test_cursor, test_conn):
        try:
            if test:
                self._conn = test_conn
                self._cursor = test_cursor
            else:
                self._conn = psycopg2.connect(
                    host="localhost",
                    database="datamed",
                    user="postgres",
                    password="123",
                    cursor_factory=RealDictCursor
                )
                self._cursor = self._conn.cursor()
            print("Connected to the database")
        except Exception as error:
            print("Error connecting to the database")
            print("Error:", error)
            time.sleep(5)

    def get_conn(self):
        return self._conn

    def get_cursor(self):
        return self._cursor

# Functions to get the singleton instance's connection and cursor
def get_conn(test=False, test_cursor=None, test_conn=None):
    return Database(test, test_cursor, test_conn).get_conn()

def get_cursor(test=False, test_cursor=None, test_conn=None):
    return Database(test, test_cursor, test_conn).get_cursor()
