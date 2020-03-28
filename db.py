import sqlite3
from pathlib import Path
import os.path

from commandify.utils import current_time

__location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))

def get_cache_dir():
    cache_dir = str(Path.home()) + '/.cache/commandify/'
    Path(cache_dir).mkdir(exist_ok=True)
    return cache_dir

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class DBProvider():
    def __init__(self, path=get_cache_dir() + 'data.sqlite'):
        self.path = path
        new_db = False
        if not os.path.isfile(self.path):
            new_db = True
        self.conn = self.get_new_conn()
        if new_db:
            with open(os.path.join(__location__, 'schema.sql')) as schema_file:
                self.conn.executescript(schema_file.read())

    def get_new_conn(self):
        conn = sqlite3.connect(self.path, check_same_thread=False)
        conn.row_factory = dict_factory
        return conn

    def cursor(self):
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def add_auth_code(self, code):
        c = self.cursor()
        c.execute('INSERT INTO auth_codes (time, code) VALUES (?, ?)',
                  (current_time(), code))
        self.commit()

    def get_auth_code(self):
        return self.cursor().execute('SELECT * FROM auth_codes ORDER BY\
                                      time DESC LIMIT 1').fetchone()

    def add_refresh_token(self, token):
        self.cursor().execute('INSERT INTO refresh_tokens (time, token)\
                               VALUES (?, ?)',
                              (current_time(), token))
        self.commit()

    def get_refresh_token(self):
        return self.cursor().execute('SELECT * FROM refresh_tokens ORDER BY\
                                      time DESC LIMIT 1').fetchone()

    def add_access_token(self, token):
        self.cursor().execute('INSERT INTO access_tokens (time, token)\
                               VALUES (?, ?)',
                              (current_time(), token))
        self.commit()

    def get_access_token(self):
        return self.cursor().execute('SELECT * FROM access_tokens ORDER BY time\
                                      DESC LIMIT 1').fetchone()
