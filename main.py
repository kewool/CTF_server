from flask import Flask, render_template, request, redirect, url_for, session, abort
from flask_wtf.csrf import CSRFProtect, CSRFError
import os
import random as rd
import datetime
import re
from db import *
app = Flask(__name__, template_folder="pages/")
csrf = CSRFProtect(app)
SECRET_KEY = os.urandom(32)

def run_docker(token, problemName):
    try:
        os.system(f"docker run -e TOKEN={token} -d --rm --name {token} -p {rd.randrange(20000,30000)}:3000 --cpus=0.1 --memory=128m {problemName}")
    except:
        run_docker()

def check_admin():
    
    return session.get("ctf_user_id") != "admin"

def check_login():
    return session.get("ctf_user_id", None) == None

@app.route("/", methods=['GET'])
def main():
    if request.method == 'GET':
        userId = session.get('ctf_user_id', None)
        return render_template("main/index.html", userId=userId)

@app.route("/login", methods=['GET','POST'])
def login_page():
    if request.method == 'GET':
        return render_template("login/index.html")
    elif request.method == 'POST':
        userId, userPw, *_ = request.form.values()
        password = hashlib.sha256(userPw.encode()).hexdigest()
        db.execute("SELECT ctf_user_id FROM ctf_users WHERE ctf_user_id=? AND ctf_user_password=?", (userId, password))
        dbId = db.fetchone()
        if dbId == None:
            return {"result":"failed"}
        elif dbId[0] == userId:
            session["ctf_user_id"] = userId
        return redirect(url_for("main"))

@app.route("/logout", methods=['GET'])
def logout():
    session.pop("ctf_user_id", None)
    return redirect(url_for("main"))

@app.route("/register", methods=['GET','POST'])
def register_page():
    if request.method == 'GET':
        return render_template("register/index.html")
    elif request.method == 'POST':
        userId, userPw, userName, userEmail, userSchool, *_ = request.form.values()
        db.execute("SELECT * from ctf_users WHERE ctf_user_id=?", (userId, ))
        if db.fetchone() == None:
            password = hashlib.sha256(userPw.encode()).hexdigest()
            db.execute("INSERT INTO ctf_users(ctf_user_id, ctf_user_password, ctf_user_name, ctf_user_email, ctf_user_school, ctf_user_score, ctf_user_solved, ctf_user_try, ctf_user_visible) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (userId, password, userName, userEmail, userSchool, 0, 0, 0, 1))
        else:
            return render_template("register/index.html", idCheck=True, id=userId, name=userName, email=userEmail, school=userSchool)
        return redirect(url_for('main'))

@app.route("/users", methods=['GET'])
def user_list_page():
    db.execute("SELECT ctf_user_name FROM ctf_users WHERE ctf_user_visible=1")
    user_list = db.fetchall()
    return render_template("user_list/index.html", user_list=user_list)

@app.route("/profile", methods=['GET', 'POST'])
def user_profile_page():
    if check_login():
        abort(401)
    if request.method == 'GET':
        user_info = db.execute("SELECT ctf_user_id, ctf_user_name, ctf_user_email, ctf_user_school FROM ctf_users WHERE ctf_user_id=?", (session.get("ctf_user_id"), )).fetchone()
        return render_template("profile/index.html", user_info=user_info)
    elif request.method == 'POST':
        userName, userPw, userEmail, userSchool, *_ = request.form.values()
        userId = session.get("ctf_user_id")
        password = hashlib.sha256(userPw.encode()).hexdigest()
        if db.execute("SELECT * FROM ctf_users WHERE ctf_user_id=? AND ctf_user_password=?", (userId, password)).fetchone() == None:
            return {"result":"incorrect password"}
        else:
            db.execute("UPDATE ctf_users SET ctf_user_name=?, ctf_user_email=?, ctf_user_school=? WHERE ctf_user_id=? AND ctf_user_password=?", (userName, userEmail, userSchool, userId, password))
        return {"result":"successful"}

@app.route("/scoreboard", methods=['GET'])
def user_scoreboard_page():
    db.execute("SELECT ctf_user_name, ctf_user_score FROM ctf_users WHERE ctf_user_visible=1 ORDER BY ctf_user_score desc, ctf_user_last_solved_date asc")
    user_list = db.fetchall()
    return render_template("scoreboard/index.html", user_list=user_list)

@app.route("/ctf", methods=['GET','POST'])
def ctf_page():
    if request.method == 'GET':
        if check_login():
            abort(401)
        db.execute("SELECT ctf_problem_name, ctf_problem_score FROM ctf_problems")
        problemList = db.fetchall()
        return render_template("ctf/index.html", problemList=problemList)
    if request.method == 'POST':
        
        return

@app.route("/api/flag/submit", methods=['POST'])
def flag_submit():
    if check_login():
        abort(401)
    userId = session.get("ctf_user_id")
    problemName, flag, *_ = request.form.values()
    if db.execute("SELECT * FROM ctf_solved WHERE ctf_user_id=? AND ctf_problem_name=?", (userId, problemName)).fetchone():
        return {"result":"duplication"}
    db.execute("SELECT ctf_problem_flag FROM ctf_problems WHERE ctf_problem_name=?", (problemName, ))
    correctFlag = db.fetchone()[0]
    if(flag == correctFlag):
        db.execute("UPDATE ctf_users SET ctf_user_solved=ctf_user_solved+1, ctf_user_try=ctf_user_try+1, ctf_user_score=ctf_user_score+(SELECT ctf_problem_score FROM ctf_problems WHERE ctf_problem_name=?), ctf_user_last_solved_date=? WHERE ctf_user_id=?", (problemName, str(datetime.datetime.now()), userId))
        db.execute("INSERT INTO ctf_logs(ctf_user_id, ctf_problem_name, ctf_correct_answer, ctf_log_flag, ctf_log_date, ctf_log_user_ip) VALUES (?, ?, ?, ?, ?, ?)", (userId, problemName, "correct", flag, str(datetime.datetime.now()), request.remote_addr))
        db.execute("INSERT INTO ctf_tried(ctf_user_id, ctf_problem_name, ctf_problem_tried_date, ctf_tried_user_ip) VALUES (?, ?, ?, ?)", (userId, problemName, str(datetime.datetime.now()), request.remote_addr))
        db.execute("INSERT INTO ctf_solved(ctf_user_id, ctf_problem_name, ctf_problem_solved_date, ctf_solved_user_ip) VALUES (?, ?, ?, ?)", (userId, problemName, str(datetime.datetime.now()), request.remote_addr))
        if not db.execute("SELECT ctf_user_visible FROM ctf_users WHERE ctf_user_id=?", (userId, )).fetchone()[0]:
            return {"result":"correct"}
        db.execute("UPDATE ctf_problems SET ctf_problem_solved=ctf_problem_solved+1 WHERE ctf_problem_name=?", (problemName, ))
        db.execute("UPDATE ctf_problems SET ctf_problem_score=ctf_problem_score-(ctf_problem_solved-1)*2 WHERE ctf_problem_name=? AND ctf_problem_score>70", (problemName, ))
        db.execute("SELECT ctf_problem_solved FROM ctf_problems WHERE ctf_problem_name=?", (problemName, ))
        score = (db.fetchone()[0] - 1) * 2
        db.execute(f"UPDATE ctf_users SET ctf_user_score=ctf_user_score-? WHERE ctf_user_id IN (SELECT ctf_user_id FROM ctf_solved WHERE ctf_problem_name=?)", (score, problemName))
    else:
        db.execute("UPDATE ctf_users SET ctf_user_try=ctf_user_try+1 WHERE ctf_user_id=?", (userId, ))
        db.execute("INSERT INTO ctf_logs(ctf_user_id, ctf_problem_name, ctf_correct_answer, ctf_log_flag, ctf_log_date, ctf_log_user_ip) VALUES (?, ?, ?, ?, ?, ?)", (userId, problemName, "incorrect", flag, str(datetime.datetime.now()), request.remote_addr))
        db.execute("INSERT INTO ctf_tried(ctf_user_id, ctf_problem_name, ctf_problem_tried_date, ctf_tried_user_ip) VALUES (?, ?, ?, ?)", (userId, problemName, str(datetime.datetime.now()), request.remote_addr))
        return {"result":"incorrect"}
    return {"result":"correct"}

@app.route("/admin", methods=['GET'])
def admin_page():
    if check_admin():
        abort(404)
    user_list = db.execute("SELECT ctf_user_id, ctf_user_name FROM ctf_users").fetchall()
    problem_list = db.execute("SELECT ctf_problem_name FROM ctf_problems").fetchall()
    solved_list = db.execute("SELECT * FROM ctf_solved ORDER BY ctf_solved_idx desc").fetchall()
    log_list = db.execute("SELECT * FROM ctf_logs ORDER BY ctf_log_idx desc").fetchall()
    notice_list = sorted(db.execute("SELECT ctf_notice_idx, ctf_notice_title FROM ctf_notices").fetchall(), reverse=True)
    return render_template("admin/index.html", user_list=user_list, problem_list=problem_list, solved_list=solved_list, log_list=log_list, notice_list=notice_list)

@app.route("/api/admin/ctf/get", methods=['POST'])
def admin_page_ctf_get():
    if check_admin():
        abort(404)
    problemName = request.form["problemName"]
    db.execute("SELECT * FROM ctf_problems WHERE ctf_problem_name=?", (problemName,))
    problem = db.fetchone()
    return {"ctf_problem_flag":problem[1], "ctf_problem_type":problem[2], "ctf_problem_contents":problem[3], "ctf_problem_file":problem[4], "ctf_problem_visible":problem[7]}

@app.route("/api/admin/ctf/add", methods=['POST'])
def admin_page_ctf_add():
    if check_admin():
        abort(404)
    problemName, problemFlag, problemType, problemContents, problemFile, problemVisible, *_ = request.form.values()
    visible = 1 if problemVisible == "visible" else 0
    try:
        db.execute("INSERT INTO ctf_problems(ctf_problem_name, ctf_problem_flag, ctf_problem_type, ctf_problem_contents, ctf_problem_file, ctf_problem_solved, ctf_problem_score, ctf_problem_visible) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (problemName, problemFlag, problemType, problemContents, problemFile, 0, 1000, visible))
    except:
        return {"result":"error"}
    return {"result":"successful", "problemName":problemName}

@app.route("/api/admin/ctf/update", methods=['POST'])
def admin_page_ctf_update():
    if check_admin():
        abort(404)
    problemName, problemFlag, problemType, problemContents, problemFile, problemVisible, *_ = request.form.values()
    visible = 1 if problemVisible == "visible" else 0
    visible_before = db.execute("SELECT ctf_problem_visible FROM ctf_problems WHERE ctf_problem_name=?", (problemName, )).fetchone()[0]
    if visible != visible_before:
        if visible:
            db.execute("UPDATE ctf_users SET ctf_user_try=ctf_user_try+1 WHERE ctf_user_id IN (SELECT ctf_user_id FROM ctf_tried WHERE ctf_problem_name=?)", (problemName, ))
            db.execute("UPDATE ctf_users SET ctf_user_solved=ctf_user_solved+1, ctf_user_score=ctf_user_score+(SELECT ctf_problem_score FROM ctf_problems WHERE ctf_problem_name=?) WHERE ctf_user_id IN (SELECT ctf_user_id FROM ctf_solved WHERE ctf_problem_name=?)", (problemName, problemName))
        else:
            db.execute("UPDATE ctf_users SET ctf_user_try=ctf_user_try-1 WHERE ctf_user_id IN (SELECT ctf_user_id FROM ctf_tried WHERE ctf_problem_name=?)", (problemName, ))
            db.execute("UPDATE ctf_users SET ctf_user_solved=ctf_user_solved-1, ctf_user_score=ctf_user_score-(SELECT ctf_problem_score FROM ctf_problems WHERE ctf_problem_name=?) WHERE ctf_user_id IN (SELECT ctf_user_id FROM ctf_solved WHERE ctf_problem_name=?)", (problemName, problemName))
    db.execute("UPDATE ctf_problems SET ctf_problem_flag=?, ctf_problem_type=?, ctf_problem_contents=?, ctf_problem_file=?, ctf_problem_visible=? WHERE ctf_problem_name=?",(problemFlag, problemType, problemContents, problemFile, visible, problemName))
    return {"result" : "successful"}

@app.route("/api/admin/ctf/delete", methods=['POST'])
def admin_page_ctf_delete():
    problemName, *_ = request.form.values()
    if db.execute("SELECT ctf_problem_visible FROM ctf_problems WHERE ctf_problem_name=?", (problemName, )).fetchone()[0]:
        db.execute("UPDATE ctf_users SET ctf_user_score=ctf_user_score-(SELECT ctf_problem_score FROM ctf_problems WHERE ctf_problem_name=?), ctf_user_solved=ctf_user_solved-1 WHERE ctf_user_id IN (SELECT ctf_user_id FROM ctf_solved WHERE ctf_problem_name=?)", (problemName, problemName))
        db.execute("UPDATE ctf_users SET ctf_user_try=ctf_user_try-1 WHERE ctf_user_id IN (SELECT ctf_user_id FROM ctf_tried WHERE ctf_problem_name=?)", (problemName, ))
    db.execute("DELETE FROM ctf_problems WHERE ctf_problem_name=?", (problemName, ))
    db.execute("DELETE FROM ctf_tried WHERE ctf_problem_name=?", (problemName, ))
    db.execute("DELETE FROM ctf_solved WHERE ctf_problem_name=?", (problemName, ))
    return {"result":"succesful"}

@app.route("/api/admin/user/get", methods=['POST'])
def admin_page_user_get():
    if check_admin():
        abort(404)
    userId, *_ = request.form.values()
    db.execute("SELECT * FROM ctf_users WHERE ctf_user_id=?", (userId, ))
    user = db.fetchone()
    return {"ctf_user_email":user[3], "ctf_user_school":user[4], "ctf_user_score":user[5], "ctf_user_solved":user[6], "ctf_user_try":user[7], "ctf_user_visible":user[8], "ctf_user_register_date":user[9], "ctf_user_last_solved_date":user[10]}

@app.route("/api/admin/user/update/profile", methods=['POST'])
def admin_page_user_update_profile():
    if check_admin():
        abort(404)
    userId, userName, userEmail, userSchool, userVisible, *_ = request.form.values()
    visible = 1 if userVisible == "visible" else 0
    visible_before = db.execute("SELECT ctf_user_visible FROM ctf_users WHERE ctf_user_id=?", (userId, )).fetchone()[0]
    try:
        db.execute("UPDATE ctf_users SET ctf_user_name=?, ctf_user_email=?, ctf_user_school=?, ctf_user_visible=? WHERE ctf_user_id=?", (userName, userEmail, userSchool, visible, userId))
    except:
        return {"result":"failed"}
    if visible != visible_before:
        if visible:
            db.execute("UPDATE ctf_problems SET ctf_problem_solved=ctf_problem_solved+1 WHERE ctf_problem_name IN (SELECT ctf_problem_name FROM ctf_solved WHERE ctf_user_id=?)", (userId, ))
            db.execute("UPDATE ctf_problems SET ctf_problem_score=ctf_problem_score-(ctf_problem_solved-1)*2 WHERE ctf_problem_name IN (SELECT ctf_problem_name FROM ctf_solved WHERE ctf_user_id=?) AND ctf_problem_score>70", (userId, ))
            db.execute("SELECT ctf_problem_solved FROM ctf_problems WHERE ctf_problem_name IN (SELECT ctf_problem_name FROM ctf_solved WHERE ctf_user_id=?)", (userId, ))
            score = list(db.fetchall())
            for i in score:
                db.execute("UPDATE ctf_users SET ctf_user_score=ctf_user_score-? WHERE ctf_user_id IN (SELECT ctf_user_id FROM ctf_solved WHERE ctf_problem_name IN (SELECT ctf_problem_name FROM ctf_solved WHERE ctf_user_id=?))", ((i[0] - 1) * 2, userId))
        elif not visible:
            db.execute("UPDATE ctf_problems SET ctf_problem_solved=ctf_problem_solved-1 WHERE ctf_problem_name IN (SELECT ctf_problem_name FROM ctf_solved WHERE ctf_user_id=?)", (userId, ))
            db.execute("UPDATE ctf_problems SET ctf_problem_score=ctf_problem_score+(ctf_problem_solved)*2 WHERE ctf_problem_name IN (SELECT ctf_problem_name FROM ctf_solved WHERE ctf_user_id=?)", (userId, ))
            db.execute("SELECT ctf_problem_solved FROM ctf_problems WHERE ctf_problem_name IN (SELECT ctf_problem_name FROM ctf_solved WHERE ctf_user_id=?)", (userId, ))
            score = list(db.fetchall())
            for i in score:
                db.execute("UPDATE ctf_users SET ctf_user_score=ctf_user_score+? WHERE ctf_user_id IN (SELECT ctf_user_id FROM ctf_solved WHERE ctf_problem_name IN (SELECT ctf_problem_name FROM ctf_solved WHERE ctf_user_id=?))", (i[0] * 2, userId))
    return {"result":"successful"}

@app.route("/api/admin/notice/get", methods=['POST'])
def admin_page_notice_get():
    notice_idx, *_ = request.form.values()
    contents = db.execute("SELECT ctf_notice_contents FROM ctf_notices WHERE ctf_notice_idx=?", (notice_idx, )).fetchone()[0]
    return {"contents": contents}

@app.route("/api/admin/notice/add", methods=['POST'])
def admin_page_notice_add():
    notice_title, notice_contents, *_ = request.form.values()
    db.execute("INSERT INTO ctf_notices(ctf_notice_title, ctf_notice_contents) VALUES(?, ?)", (notice_title, notice_contents))
    notice_idx = db.execute("SELECT ctf_notice_idx FROM ctf_notices WHERE ctf_notice_title=?", (notice_title, )).fetchone()[0]
    return {"result":"successful", "noticeIdx":notice_idx}

@app.route("/api/admin/notice/update", methods=['POST'])
def admin_page_notice_update():
    notice_idx, notice_title, notice_contents, *_ = request.form.values()
    db.execute("UPDATE ctf_notices SET ctf_notice_title=?, ctf_notice_contents=? WHERE ctf_notice_idx=?", (notice_title, notice_contents, notice_idx))
    return {"result":"successful"}

@app.route("/api/admin/notice/delete", methods=['POST'])
def admin_page_notice_delete():
    notice_idx, *_ = request.form.values()
    db.execute("DELETE FROM ctf_notices WHERE ctf_notice_idx=?", (notice_idx, ))
    return {"result":"successful"}

@app.route("/api/admin/user/changepassword", methods=['POST'])
def admin_page_user_changepassword():
    userId, userPw, *_ = request.form.values()
    db.execute("UPDATE ctf_users SET ctf_user_password=? WHERE ctf_user_id=?",(hashlib.sha256(userPw.encode()).hexdigest(), userId))
    return {"result":"successful"}

@app.route("/api/ctf/get", methods=['POST'])
def ctf_get_api():
    if check_login():
        abort(401)
    problemName, *_ = request.form.values()
    token = hashlib.sha256(session.get("ctf_user_id").encode() + SECRET_KEY).hexdigest() + problemName
    run = os.popen(f"docker ps | grep {token}").read()
    if run == "":
        return {"result":"none"}
    return re.findall(r'\d+', run.split(":")[2])[0]

@app.route('/api/ctf/run', methods=['POST'])
def ctf_run_api():
    if check_login():
        abort(401)
    problemName, *_ = request.form.values()
    token = hashlib.sha256(session.get("ctf_user_id").encode() + SECRET_KEY).hexdigest()
    os.system(f"docker kill $(docker ps -q -f name={token})")
    token += problemName
    run_docker(token, problemName)
    run = os.popen(f"docker ps | grep {token}").read()
    return re.findall(r'\d+', run.split(":")[2])[0]
    

@app.route('/api/ctf/stop/<token>', methods=['GET'])
def ctf_stop_api(token):
    try:
        os.system(f"docker kill {token}")
    except:
        return 'failed'
    return 'successful'

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('error/index.html')

if __name__ == '__main__':
    app.config["SECRET_KEY"] = SECRET_KEY
    app.run(port=5324, debug=True)