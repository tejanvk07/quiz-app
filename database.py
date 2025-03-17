import sqlite3
from flask import *

def connect_database():
    sql = sqlite3.connect('quizapp.db')
    sql.row_factory = sqlite3.Row
    return sql

def get_database():
    if not hasattr(g , "quizapp.db"):
        g.sqlite_db = connect_database()
    return g.sqlite_db

