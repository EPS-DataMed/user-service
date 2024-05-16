import psycopg2
from psycopg2.extras import RealDictCursor
import time

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._conn = None
            cls._instance._cursor = None
            cls._instance._connect_db()
        return cls._instance

    def _connect_db(self):
        try:
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
def get_conn():
    return Database().get_conn()

def get_cursor():
    return Database().get_cursor()
