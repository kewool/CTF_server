from flask import Flask, request, redirect, session
from flask_wtf.csrf import CSRFProtect, CSRFError
import subprocess
import hashlib
import random as rd
app = Flask(__name__)
csrf = CSRFProtect(app)
SECRET_KEY = "secretkey"
def check_login():
    return not session.get("ctf_user_id", None)

def check_container(problemName):
    token = hashlib.sha256(session.get("ctf_user_id").encode() + SECRET_KEY).hexdigest() + problemName
    run = subprocess.Popen("docker ps --format '{{.Ports}} {{.Names}}' | grep " + token, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).communicate()[0].decode('utf-8').split(" ")[0]
    if run == "":
        return "none"
    return run

def run_docker(token, problemName):
    try:
        problemName = problemName.replace(" ", "").replace(";","").replace("$","")
        subprocess.Popen(f"docker run -e TOKEN={token} -e HOST={host} -d --rm --name {token} -p {rd.randrange(20000,30000)}:3000 --cpus=0.1 --memory=128m --memory-swap=128m ctf_{problemName}", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    except:
        run_docker()

@app.route("/api/ctf/docker/get", methods=['POST'])
def ctf_get_api():
    if check_login():
        return redirect(url_for("login_page"))
    problemName, *_ = request.form.values()
    token = hashlib.sha256(session.get("ctf_user_id").encode() + SECRET_KEY).hexdigest()
    run = subprocess.Popen("docker ps --format '{{.Ports}} {{.Names}}' | grep " + token, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).communicate()[0].decode('utf-8').split(" ")[0]
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
    subprocess.Popen(f"docker kill $(docker ps -q -f name={token})", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    token += problemName
    run_docker(token, problemName)
    return {"docker":subprocess.Popen("docker ps --format '{{.Ports}} {{.Names}}' | grep " + token, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).communicate()[0].decode('utf-8').split(" ")[0]}
    

@app.route('/api/ctf/docker/stop/<token>', methods=['GET'])
def ctf_stop_api(token):
    token = token.replace(" ", "").replace(";","").replace("$","")
    try:
        subprocess.Popen(f"docker kill {token}", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    except:
        return 'failed'
    return 'successful'

if __name__ == '__main__':
    app.config["SECRET_KEY"] = SECRET_KEY
    app.run(port=5325)