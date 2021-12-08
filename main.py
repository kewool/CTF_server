from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf.csrf import CSRFProtect, CSRFError
import os
import random as rd
from db import *
app = Flask(__name__, template_folder="pages/")
csrf = CSRFProtect(app)

def run_docker(token):
    try:
        os.system(f"docker run -e TOKEN={token} -d --rm --name {token} -p {rd.randrange(8000,65535)}:3000 --cpus=0.1 --memory=128m ctf_1")
    except:
        run_docker()

def check_admin():
    return session.get("ctf_user_id") == "admin"

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
        userId, userPw, _ = request.form.values()
        password = hashlib.sha256(userPw.encode()).hexdigest()
        db.execute("SELECT ctf_user_id FROM ctf_users WHERE ctf_user_id=? AND ctf_user_password=?", (userId, password))
        dbId = db.fetchone()
        if dbId == None:
            return render_template("login/index.html", idCheck=True)
        elif dbId[0] == userId:
            session['ctf_user_id'] = userId
        return redirect(url_for('main'))

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('ctf_user_id', None)
    return redirect(url_for("main"))

@app.route("/register", methods=['GET','POST'])
def register_page():
    if request.method == 'GET':
        return render_template("register/index.html")
    elif request.method == 'POST':
        userId, userPw, userName, userEmail, userSchool, _ = request.form.values()
        db.execute("SELECT * from ctf_users WHERE ctf_user_id=?", (userId, ))
        if db.fetchone() == None:
            password = hashlib.sha256(userPw.encode()).hexdigest()
            db.execute("INSERT INTO ctf_users(ctf_user_id, ctf_user_password, ctf_user_name, ctf_user_email, ctf_user_school, ctf_user_score, ctf_user_visible) VALUES (?, ?, ?, ?, ?, ?, ?)", (userId, password, userName, userEmail, userSchool, 0, 1))
        else:
            return render_template("register/index.html", idCheck=True, id=userId, name=userName, email=userEmail, school=userSchool)
        return redirect(url_for('main'))

@app.route("/users", methods=['GET'])
def user_list_page():
    db.execute("SELECT ctf_user_name FROM ctf_users WHERE ctf_user_visible=1")
    user_list = db.fetchall()
    return render_template("user_list/index.html", user_list=user_list)

@app.route("/ctf", methods=['GET'])
def ctf_page():
    return

@app.route("/admin", methods=['GET'])
def admin_page():
    #if not check_admin():
        #return "only admin"
    db.execute("SELECT * FROM ctf_problems")
    problem_list = db.fetchall()
    return render_template("admin/index.html", problem_list=problem_list)

@app.route("/admin/ctf/get", methods=['POST'])
def admin_page_ctf_get():
    if request.method =='POST':
        return

@app.route("/admin/ctf/add", methods=['POST'])
def admin_page_ctf_add():
    if request.method =='POST':
        problemName, problemFlag, problemType, problemContents, problemFile, problemVisible, *_ = request.form.values()
        visible = 1 if problemVisible == "visible" else 0
        try:
            db.execute("INSERT INTO ctf_problems(ctf_problem_name, ctf_problem_flag, ctf_problem_type, ctf_problem_contents, ctf_problem_file, ctf_problem_visible) VALUES (?, ?, ?, ?, ?, ?)", (problemName, problemFlag, problemType, problemContents, problemFile, visible))
        except:
            return {"result":"error"}
        return {"result":problemName}

@app.route("/admin/users", methods=['GET','POST'])
def admin_page_users():
    return render_template("admin/users.html")

@app.route('/api/ctf', methods=['POST'])
def ctf_api():
    token = session.get("ctf_user_id", None)
    if token:
        token = hashlib.sha256(token.encode()).hexdigest()
        run_docker(token)
    return os.popen(f"docker ps | grep {token}").read()

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
    app.config["SECRET_KEY"] = os.urandom(32)
    app.run(port=5324, debug=True)