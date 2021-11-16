import sqlite3

db_con = sqlite3.connect("ctf.db", isolation_level=None)
db = db_con.cursor()

db.execute("CREATE TABLE IF NOT EXISTS ctf_users(ctf_user_id text PRIMARY KEY, ctf_user_password text")