import sqlite3 as sql

connect = sql.connect('users.db')
cursor = connect.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS users_list(
    id INTEGER,
    username TEXT,
    counts INTEGER,
    lang TEXT
)""")

connect.commit()