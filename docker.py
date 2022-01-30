from flask import Flask, request, redirect, session, url_for
from flask_cors import CORS, cross_origin
import subprocess
import hashlib
import logging
import random as rd
app = Flask(__name__)
logging.basicConfig(filename = "logs/main.log", level = logging.INFO)
SECRET_KEY = "secretkey"
app.config["SECRET_KEY"] = SECRET_KEY
app.config["WTF_CSRF_SECRET_KEY"] = SECRET_KEY
CORS(app)
problemNameJson = {"CookieCon":"cookiecon","Color":"color","통신 보안":"communicationsecurity","math":"math","name":"name","club":"club","strange_bank":"strange_bank","Ahoy~!":"ahoy","bashrc":"bashrc"}

def check_container(problemName, userId):
    token = hashlib.sha256(userId.encode() + SECRET_KEY).hexdigest() + problemName
    run = subprocess.Popen("docker ps --format '{{.Ports}} {{.Names}}' | grep " + token, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).communicate()[0].decode('utf-8').split(" ")[0]
    if run == "":
        return "none"
    return run

def run_docker(token, problemName, userId, host):
    try:
        problemName = problemName.replace(" ", "").replace(";","").replace("$","")
        subprocess.Popen(f"docker run -e TOKEN={token} -e HOST={host} -d --rm --name {token} -p {rd.randrange(20000,30000)}:3000 --cpus=0.1 --memory=128m --memory-swap=128m ctf_{problemName}", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    except:
        run_docker()

@app.route("/api/ctf/docker/get", methods=['POST'])
def ctf_get_api():
    problemName, userId, *_ = request.form.values()
    problemName = problemNameJson[problemName]
    token = hashlib.sha256(userId.encode() + SECRET_KEY).hexdigest() + problemName
    run = subprocess.Popen("docker ps --format '{{.Ports}} {{.Names}}' | grep " + token, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).communicate()[0].decode('utf-8').split(" ")[0]
    if run == "":
        return {"docker":"none"}
    return {"docker":run}

@app.route('/api/ctf/docker/run', methods=['POST'])
def ctf_run_api():
    problemName, userId, host, *_ = request.form.values()
    problemName = problemNameJson[problemName]
    check = check_container(problemName, userId)
    if check != "none":
        return {"docker":check}
    token = hashlib.sha256(userId.encode() + SECRET_KEY).hexdigest()
    # if os.system(f"docker ps --format '{{.Image}} {{.Names}}' | grep {token}").read().split(" ")[0] == problemName:
    #     return {"result":os.popen(f"docker ps --format '{{.Ports}}' | grep {token}").read().split(" ")[0]}
    subprocess.Popen(f"docker kill $(docker ps -q -f name={token})", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    token += problemName
    run_docker(token, problemName, userId, host)
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
    app.run(port=5325)