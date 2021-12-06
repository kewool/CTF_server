from flask import Flask, render_template, request
import os
import random as rd
from db import *
app = Flask(__name__, template_folder="pages/")

def run_docker(token):
    try:
        os.system(f"docker run -e TOKEN={token} -d --rm --name {token} -p {rd.randrange(8000,65535)}:3000 --cpus=0.1 --memory=128m ctf_1")
    except:
        run_docker()

@app.route("/", methods=['GET','POST'])
def main():
    if request.method == 'GET':
        return sqlite3.version

@app.route("/login", methods=['GET','POST'])
def login_page():
    if request.method == 'GET':
        return render_template("login/index.html")
    elif request.method == 'POST':
        return

@app.route("/register", methods=['GET','POST'])
def register_page():
    if request.method == 'GET':
        return render_template("register/index.html")
    elif request.method == 'POST':
        return

@app.route('/api/ctf', methods=['POST'])
def ctf_api():
    if request.method == 'POST':
        token = request.form['token']
        run_docker(token)
        return os.popen(f"docker ps | grep {token}").read()

@app.route('/api/ctf/stop/<token>', methods=['GET'])
def ctf_stop_api(token):
    try:
        os.system(f"docker kill {token}")
    except:
        return 'failed'
    return 'successful'

if __name__ == '__main__':
    app.run(debug=True)