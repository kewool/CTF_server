from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf.csrf import CSRFProtect, CSRFError
import os
import random as rd
from db import *
import hashlib
app = Flask(__name__, template_folder="pages/")
csrf = CSRFProtect(app)

def run_docker(token):
    try:
        os.system(f"docker run -e TOKEN={token} -d --rm --name {token} -p {rd.randrange(8000,65535)}:3000 --cpus=0.1 --memory=128m ctf_1")
    except:
        run_docker()

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
            db.execute("INSERT INTO ctf_users(ctf_user_id, ctf_user_password, ctf_user_name, ctf_user_email, ctf_user_school) VALUES (?, ?, ?, ?, ?)", (userId, password, userName, userEmail, userSchool))
        else:
            return render_template("register/index.html", idCheck=True, id=userId, name=userName, email=userEmail, school=userSchool)
        return redirect(url_for('main'))

@app.route('/api/ctf', methods=['POST'])
def ctf_api():
    if request.method == 'POST':
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