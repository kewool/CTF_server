from flask import Flask, render_template, request, redirect, url_for, session, abort
from flask_wtf.csrf import CSRFProtect, CSRFError
import os
import random as rd
import datetime
import logging
from db import *
logging.basicConfig(filename = "logs/project.log", level = logging.INFO)
app = Flask(__name__, template_folder="pages/")
csrf = CSRFProtect(app)
host = "ctf.kewool.net"
dockerHost = "ctf.nahee.kim"
SECRET_KEY = os.urandom(32)

def run_docker(token, problemName):
    try:
        os.system(f"docker run -e TOKEN={token} -e HOST={host} -d --rm --name {token} -p {rd.randrange(20000,30000)}:3000 --cpus=0.1 --memory=200m --memory-swap=200m ctf_{problemName}")
    except:
        run_docker()

def check_admin():
    userId = session.get("ctf_user_id")
    if not userId:
        abort(404)
    if not db.execute("SELECT ctf_user_admin FROM ctf_users WHERE ctf_user_id=?", (userId, )).fetchone()[0]:
        abort(404)

def check_login():
    return not session.get("ctf_user_id", None)

def check_container(problemName):
    token = hashlib.sha256(session.get("ctf_user_id").encode() + SECRET_KEY).hexdigest() + problemName
    run = os.popen("docker ps --format '{{.Ports}} {{.Names}}' | grep " + token).read().split(" ")[0]
    if run == "":
        return "none"
    return run

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
            return render_template("login/index.html", invalid=1)
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
        return redirect(url_for("login_page"))
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
            db.execute("UPDATE ctf_solved SET ctf_user_name=? WHERE ctf_user_id=?",(userName, userId))
        return {"result":"successful"}

@app.route("/scoreboard", methods=['GET'])
def user_scoreboard_page():
    db.execute("SELECT ctf_user_name, ctf_user_score FROM ctf_users WHERE ctf_user_visible=1 ORDER BY ctf_user_score desc, ctf_user_last_solved_date asc")
    user_list = db.fetchall()
    return render_template("scoreboard/index.html", user_list=user_list)

@app.route("/challanges", methods=['GET'])
def ctf_page():
    if check_login():
        return redirect(url_for("login_page"))
    return render_template("ctf/index.html", host=dockerHost)

@app.route("/notice", methods=['GET'])
def note_page():
    notice_list = db.execute("SELECT ctf_notice_title, ctf_notice_contents FROM ctf_notices ORDER BY ctf_notice_idx desc").fetchall()
    return render_template("notice/index.html", notice_list=notice_list)

@app.route("/api/ctf/list", methods=['POST'])
def ctf_list():
    if check_login():
        return abort(401)
    problemList = db.execute("SELECT ctf_problem_type, ctf_problem_name, ctf_problem_score FROM ctf_problems WHERE ctf_problem_visible=1 ORDER BY ctf_problem_type asc, ctf_problem_score asc").fetchall()
    solvedList = db.execute("SELECT ctf_problem_name FROM ctf_solved WHERE ctf_user_id=?", (session.get("ctf_user_id"), )).fetchall()
    return {"contents":problemList, "solved":solvedList}

@app.route("/api/ctf/get", methods=['POST'])
def ctf_get():
    if check_login():
        return abort(401)
    problemName, *_ = request.form.values()
    problemContents = db.execute("SELECT ctf_problem_score, ctf_problem_contents, ctf_problem_file, ctf_problem_solved FROM ctf_problems WHERE ctf_problem_visible=1 AND ctf_problem_name=?", (problemName, )).fetchone()
    return {"contents":problemContents, "docker": check_container(problemName)}

@app.route("/api/ctf/solved", methods=['POST'])
def ctf_solved():
    if check_login():
        return abort(401)
    problemName, *_ = request.form.values()
    problemSolved = db.execute("SELECT ctf_solved.ctf_user_name, ctf_problem_solved_date FROM ctf_solved INNER JOIN ctf_users ON ctf_solved.ctf_user_name=ctf_users.ctf_user_name WHERE ctf_solved.ctf_problem_name=? AND ctf_user_visible=1", (problemName, )).fetchall()
    return {"contents":problemSolved}

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
        db.execute("INSERT INTO ctf_logs(ctf_user_id, ctf_problem_name, ctf_correct_answer, ctf_log_flag, ctf_log_date, ctf_log_user_ip) VALUES (?, ?, ?, ?, ?, ?)", (userId, problemName, "correct", flag, str(datetime.datetime.now()), request.headers.get("CF-Connecting-IP")))
        db.execute("INSERT INTO ctf_tried(ctf_user_id, ctf_problem_name, ctf_problem_tried_date, ctf_tried_user_ip) VALUES (?, ?, ?, ?)", (userId, problemName, str(datetime.datetime.now()), request.headers.get("CF-Connecting-IP")))
        db.execute("INSERT INTO ctf_solved(ctf_user_id, ctf_user_name, ctf_problem_name, ctf_problem_solved_date, ctf_solved_user_ip) VALUES (?, ?, ?, ?, ?)", (userId, db.execute("SELECT ctf_user_name FROM ctf_users WHERE ctf_user_id=?", (userId,)).fetchone()[0], problemName, str(datetime.datetime.now()), request.headers.get("CF-Connecting-IP")))
        if not db.execute("SELECT ctf_user_visible FROM ctf_users WHERE ctf_user_id=?", (userId, )).fetchone()[0]:
            return {"result":"correct"}
        db.execute("UPDATE ctf_problems SET ctf_problem_solved=ctf_problem_solved+1 WHERE ctf_problem_name=?", (problemName, ))
        db.execute("UPDATE ctf_problems SET ctf_problem_score=ctf_problem_score-(ctf_problem_solved-1)*2 WHERE ctf_problem_name=? AND ctf_problem_score>70", (problemName, ))
        db.execute("SELECT ctf_problem_solved FROM ctf_problems WHERE ctf_problem_name=?", (problemName, ))
        score = (db.fetchone()[0] - 1) * 2
        db.execute(f"UPDATE ctf_users SET ctf_user_score=ctf_user_score-? WHERE ctf_user_id IN (SELECT ctf_user_id FROM ctf_solved WHERE ctf_problem_name=?)", (score, problemName))
    else:
        db.execute("UPDATE ctf_users SET ctf_user_try=ctf_user_try+1 WHERE ctf_user_id=?", (userId, ))
        db.execute("INSERT INTO ctf_logs(ctf_user_id, ctf_problem_name, ctf_correct_answer, ctf_log_flag, ctf_log_date, ctf_log_user_ip) VALUES (?, ?, ?, ?, ?, ?)", (userId, problemName, "incorrect", flag, str(datetime.datetime.now()), request.headers.get("CF-Connecting-IP")))
        db.execute("INSERT INTO ctf_tried(ctf_user_id, ctf_problem_name, ctf_problem_tried_date, ctf_tried_user_ip) VALUES (?, ?, ?, ?)", (userId, problemName, str(datetime.datetime.now()), request.headers.get("CF-Connecting-IP")))
        return {"result":"incorrect"}
    return {"result":"correct"}

@app.route("/admin", methods=['GET'])
def admin_page():
    check_admin()
    user_list = db.execute("SELECT ctf_user_id, ctf_user_name FROM ctf_users").fetchall()
    problem_list = db.execute("SELECT ctf_problem_name FROM ctf_problems").fetchall()
    solved_list = db.execute("SELECT * FROM ctf_solved ORDER BY ctf_solved_idx desc").fetchall()
    log_list = db.execute("SELECT * FROM ctf_logs ORDER BY ctf_log_idx desc").fetchall()
    notice_list = db.execute("SELECT ctf_notice_idx, ctf_notice_title FROM ctf_notices ORDER BY ctf_notice_idx desc").fetchall()
    return render_template("admin/index.html", user_list=user_list, problem_list=problem_list, solved_list=solved_list, log_list=log_list, notice_list=notice_list)

@app.route("/api/admin/ctf/get", methods=['POST'])
def admin_page_ctf_get():
    check_admin()
    problemName = request.form["problemName"]
    db.execute("SELECT * FROM ctf_problems WHERE ctf_problem_name=?", (problemName,))
    problem = db.fetchone()
    return {"ctf_problem_flag":problem[1], "ctf_problem_type":problem[2], "ctf_problem_contents":problem[3], "ctf_problem_file":problem[4], "ctf_problem_solved":problem[5], "ctf_problem_score":problem[6], "ctf_problem_visible":problem[7], "ctf_problem_visible_score":problem[8]}

@app.route("/api/admin/ctf/add", methods=['POST'])
def admin_page_ctf_add():
    check_admin()
    problemName, problemFlag, problemType, problemContents, problemFile, problemVisible, problemScoreVisible, *_ = request.form.values()
    visible = 1 if problemVisible == "visible" else 0
    scoreVisible = 1 if problemScoreVisible == "visible" else 0
    db.execute("INSERT INTO ctf_problems(ctf_problem_name, ctf_problem_flag, ctf_problem_type, ctf_problem_contents, ctf_problem_file, ctf_problem_solved, ctf_problem_score, ctf_problem_visible, ctf_problem_visible_score) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (problemName, problemFlag, problemType, problemContents, problemFile, 0, 1000, visible, scoreVisible))
    return {"result":"successful", "problemName":problemName}

@app.route("/api/admin/ctf/update", methods=['POST'])
def admin_page_ctf_update():
    check_admin()
    problemName, problemFlag, problemType, problemContents, problemFile, problemVisible, problemScoreVisible, *_ = request.form.values()
    visible = 1 if problemVisible == "visible" else 0
    scoreVisible = 1 if problemScoreVisible == "visible" else 0
    scoreVisible_before = db.execute("SELECT ctf_problem_visible_score FROM ctf_problems WHERE ctf_problem_name=?", (problemName, )).fetchone()[0]
    if scoreVisible != scoreVisible_before:
        if scoreVisible:
            db.execute("UPDATE ctf_users SET ctf_user_try=ctf_user_try+1 WHERE ctf_user_id IN (SELECT ctf_user_id FROM ctf_tried WHERE ctf_problem_name=?)", (problemName, ))
            db.execute("UPDATE ctf_users SET ctf_user_solved=ctf_user_solved+1, ctf_user_score=ctf_user_score+(SELECT ctf_problem_score FROM ctf_problems WHERE ctf_problem_name=?) WHERE ctf_user_id IN (SELECT ctf_user_id FROM ctf_solved WHERE ctf_problem_name=?)", (problemName, problemName))
        else:
            db.execute("UPDATE ctf_users SET ctf_user_try=ctf_user_try-1 WHERE ctf_user_id IN (SELECT ctf_user_id FROM ctf_tried WHERE ctf_problem_name=?)", (problemName, ))
            db.execute("UPDATE ctf_users SET ctf_user_solved=ctf_user_solved-1, ctf_user_score=ctf_user_score-(SELECT ctf_problem_score FROM ctf_problems WHERE ctf_problem_name=?) WHERE ctf_user_id IN (SELECT ctf_user_id FROM ctf_solved WHERE ctf_problem_name=?)", (problemName, problemName))
    db.execute("UPDATE ctf_problems SET ctf_problem_flag=?, ctf_problem_type=?, ctf_problem_contents=?, ctf_problem_file=?, ctf_problem_visible=?, ctf_problem_visible_score=? WHERE ctf_problem_name=?",(problemFlag, problemType, problemContents, problemFile, visible, scoreVisible, problemName))
    return {"result" : "successful"}

@app.route("/api/admin/ctf/reset", methods=['POST'])
def admin_page_ctf_reset():
    problemName, *_ = request.form.values()
    if db.execute("SELECT ctf_problem_visible_score FROM ctf_problems WHERE ctf_problem_name=?", (problemName, )).fetchone()[0]:
        db.execute("UPDATE ctf_users SET ctf_user_try=ctf_user_try-1 WHERE ctf_user_id IN (SELECT ctf_user_id FROM ctf_tried WHERE ctf_problem_name=?)", (problemName, ))
        db.execute("UPDATE ctf_users SET ctf_user_solved=ctf_user_solved-1, ctf_user_score=ctf_user_score-(SELECT ctf_problem_score FROM ctf_problems WHERE ctf_problem_name=?) WHERE ctf_user_id IN (SELECT ctf_user_id FROM ctf_solved WHERE ctf_problem_name=?)", (problemName, problemName))
    db.execute("DELETE FROM ctf_tried WHERE ctf_problem_name=?", (problemName, ))
    db.execute("DELETE FROM ctf_solved WHERE ctf_problem_name=?", (problemName, ))
    db.execute("UPDATE ctf_problems SET ctf_problem_score=1000, ctf_problem_solved=0 WHERE ctf_problem_name=?",(problemName, ))
    return {"result":"successful"}

@app.route("/api/admin/ctf/delete", methods=['POST'])
def admin_page_ctf_delete():
    check_admin()
    problemName, *_ = request.form.values()
    if db.execute("SELECT ctf_problem_visible_score FROM ctf_problems WHERE ctf_problem_name=?", (problemName, )).fetchone()[0]:
        db.execute("UPDATE ctf_users SET ctf_user_score=ctf_user_score-(SELECT ctf_problem_score FROM ctf_problems WHERE ctf_problem_name=?), ctf_user_solved=ctf_user_solved-1 WHERE ctf_user_id IN (SELECT ctf_user_id FROM ctf_solved WHERE ctf_problem_name=?)", (problemName, problemName))
        db.execute("UPDATE ctf_users SET ctf_user_try=ctf_user_try-1 WHERE ctf_user_id IN (SELECT ctf_user_id FROM ctf_tried WHERE ctf_problem_name=?)", (problemName, ))
    db.execute("DELETE FROM ctf_problems WHERE ctf_problem_name=?", (problemName, ))
    db.execute("DELETE FROM ctf_tried WHERE ctf_problem_name=?", (problemName, ))
    db.execute("DELETE FROM ctf_solved WHERE ctf_problem_name=?", (problemName, ))
    return {"result":"succesful"}

@app.route("/api/admin/user/get", methods=['POST'])
def admin_page_user_get():
    check_admin()
    userId, *_ = request.form.values()
    db.execute("SELECT * FROM ctf_users WHERE ctf_user_id=?", (userId, ))
    user = db.fetchone()
    return {"ctf_user_email":user[3], "ctf_user_school":user[4], "ctf_user_score":user[5], "ctf_user_solved":user[6], "ctf_user_try":user[7], "ctf_user_visible":user[8], "ctf_user_register_date":user[9], "ctf_user_last_solved_date":user[10], "ctf_user_admin":user[11]}

@app.route("/api/admin/user/update/profile", methods=['POST'])
def admin_page_user_update_profile():
    check_admin()
    userId, userName, userEmail, userSchool, userVisible, userAdmin, *_ = request.form.values()
    visible = 1 if userVisible == "visible" else 0
    admin = 1 if userAdmin == "admin" else 0
    visible_before = db.execute("SELECT ctf_user_visible FROM ctf_users WHERE ctf_user_id=?", (userId, )).fetchone()[0]
    try:
        db.execute("UPDATE ctf_users SET ctf_user_name=?, ctf_user_email=?, ctf_user_school=?, ctf_user_visible=?, ctf_user_admin=? WHERE ctf_user_id=?", (userName, userEmail, userSchool, visible, admin, userId))
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

@app.route("/api/admin/user/change/password", methods=['POST'])
def admin_page_user_change_password():
    check_admin()
    userId, userPw, *_ = request.form.values()
    db.execute("UPDATE ctf_users SET ctf_user_password=? WHERE ctf_user_id=?",(hashlib.sha256(userPw.encode()).hexdigest(), userId))
    return {"result":"successful"}

@app.route("/api/admin/user/delete", methods=['POST'])
def admin_page_user_delete():
    check_admin()
    userId, *_ = request.form.values()
    db.execute("DELETE FROM ctf_users WHERE ctf_user_id=?", (userId, ))
    return {"result":"successful"}

@app.route("/api/admin/notice/get", methods=['POST'])
def admin_page_notice_get():
    check_admin()
    notice_idx, *_ = request.form.values()
    contents = db.execute("SELECT ctf_notice_contents FROM ctf_notices WHERE ctf_notice_idx=?", (notice_idx, )).fetchone()[0]
    return {"contents": contents}

@app.route("/api/admin/notice/add", methods=['POST'])
def admin_page_notice_add():
    check_admin()
    notice_title, notice_contents, *_ = request.form.values()
    db.execute("INSERT INTO ctf_notices(ctf_notice_title, ctf_notice_contents) VALUES(?, ?)", (notice_title, notice_contents))
    notice_idx = db.execute("SELECT ctf_notice_idx FROM ctf_notices WHERE ctf_notice_title=?", (notice_title, )).fetchone()[0]
    return {"result":"successful", "noticeIdx":notice_idx}

@app.route("/api/admin/notice/update", methods=['POST'])
def admin_page_notice_update():
    check_admin()
    notice_idx, notice_title, notice_contents, *_ = request.form.values()
    db.execute("UPDATE ctf_notices SET ctf_notice_title=?, ctf_notice_contents=? WHERE ctf_notice_idx=?", (notice_title, notice_contents, notice_idx))
    return {"result":"successful"}

@app.route("/api/admin/notice/delete", methods=['POST'])
def admin_page_notice_delete():
    check_admin()
    notice_idx, *_ = request.form.values()
    db.execute("DELETE FROM ctf_notices WHERE ctf_notice_idx=?", (notice_idx, ))
    return {"result":"successful"}

@app.route("/api/ctf/docker/get", methods=['POST'])
def ctf_get_api():
    if check_login():
        return redirect(url_for("login_page"))
    problemName, *_ = request.form.values()
    token = hashlib.sha256(session.get("ctf_user_id").encode() + SECRET_KEY).hexdigest() + problemName
    run = os.popen(f"docker ps --format '{{.Ports}} {{.Names}}' | grep {token}").read().split(" ")[0]
    if run == "":
        return {"docker":"none"}
    return {"docker":run}

@app.route('/api/ctf/docker/run', methods=['POST'])
def ctf_run_api():
    if check_login():
        return redirect(url_for("login_page"))
    problemName, *_ = request.form.values()
    check = check_container(problemName)
    if check != "none":
        return {"docker":check}
    token = hashlib.sha256(session.get("ctf_user_id").encode() + SECRET_KEY).hexdigest()
    # if os.system(f"docker ps --format '{{.Image}} {{.Names}}' | grep {token}").read().split(" ")[0] == problemName:
    #     return {"result":os.popen(f"docker ps --format '{{.Ports}}' | grep {token}").read().split(" ")[0]}
    os.system(f"docker kill $(docker ps -q -f name={token})")
    token += problemName
    run_docker(token, problemName)
    return {"docker":os.popen("docker ps --format '{{.Ports}} {{.Names}}' | grep " + token).read().split(" ")[0]}
    

@app.route('/api/ctf/docker/stop/<token>', methods=['GET'])
def ctf_stop_api(token):
    try:
        os.system(f"docker kill {token}")
    except:
        return 'failed'
    return 'successful'

@app.errorhandler(500)
def page_not_found(e):
    return {"result":"error"}

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('error/index.html')

if __name__ == '__main__':
    app.config["SECRET_KEY"] = SECRET_KEY
    app.run(port=5324)