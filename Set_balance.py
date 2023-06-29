import sqlite3 as sql

connect = sql.connect('users.db')
cursor = connect.cursor()

balance = 100
user_id = 1114704281
cursor.execute(f"UPDATE users_list SET counts={balance} WHERE id={user_id}")
connect.commit()