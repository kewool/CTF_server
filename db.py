import sqlite3
import hashlib

db_con = sqlite3.connect("ctf.db", isolation_level=None, check_same_thread=False)
db = db_con.cursor()

db.execute("CREATE TABLE IF NOT EXISTS ctf_users(ctf_user_id text PRIMARY KEY, ctf_user_password text, ctf_user_name text unique, ctf_user_email text unique, ctf_user_school text, ctf_user_score int, ctf_user_solved int, ctf_user_try int, ctf_user_visible int, ctf_user_register_date text default (datetime('now', 'localtime')), ctf_user_last_solved_date int, ctf_user_admin int default 0)")
db.execute("CREATE TABLE IF NOT EXISTS ctf_problems(ctf_problem_name text PRIMARY KEY, ctf_problem_flag text, ctf_problem_type text, ctf_problem_contents text, ctf_problem_file text, ctf_problem_solved int, ctf_problem_score int, ctf_problem_visible int)")
db.execute("CREATE TABLE IF NOT EXISTS ctf_solved(ctf_solved_idx INTEGER PRIMARY KEY AUTOINCREMENT, ctf_user_id text, ctf_problem_name text, ctf_problem_solved_date text, ctf_solved_user_ip text)")
db.execute("CREATE TABLE IF NOT EXISTS ctf_tried(ctf_tried_idx INTEGER PRIMARY KEY AUTOINCREMENT, ctf_user_id text, ctf_problem_name text, ctf_problem_tried_date text, ctf_tried_user_ip text)")
db.execute("CREATE TABLE IF NOT EXISTS ctf_logs(ctf_log_idx INTEGER PRIMARY KEY AUTOINCREMENT, ctf_user_id text, ctf_problem_name text, ctf_correct_answer text, ctf_log_flag text, ctf_log_date text, ctf_log_user_ip text)")
db.execute("CREATE TABLE IF NOT EXISTS ctf_notices(ctf_notice_idx INTEGER PRIMARY KEY AUTOINCREMENT, ctf_notice_title text, ctf_notice_contents text)")
try:
    db.execute("INSERT INTO ctf_users(ctf_user_id, ctf_user_password, ctf_user_name, ctf_user_email, ctf_user_school, ctf_user_score, ctf_user_solved, ctf_user_try, ctf_user_visible, ctf_user_admin) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", ("admin", hashlib.sha256("admin".encode()).hexdigest(), "admin", None, None, 0, 0, 0, 0, 1))
except:
    None