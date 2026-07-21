import sqlite3
import os

DATABASE = os.path.join(os.getcwd(), "users.db")

def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection