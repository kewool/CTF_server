from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import random as rd
from db import *

token_gl="abcd"

app = FastAPI()
templates = Jinja2Templates(directory="pages")

def run_docker(token):
    try:
        os.system(f"docker run -e TOKEN={token} -d --rm --name {token} -p {rd.randrange(8000,65535)}:3000 --cpus=0.1 --memory=128m ctf_1")
    except:
        run_docker()

@app.get("/")
async def main():
    return sqlite3.version

@app.get("/login")
async def login_page(request:Request):
    return templates.TemplateResponse("login/index.html", {"request":request})

@app.post('/login')
def login_page():
    return

@app.get('/api/ctf')
def ctf_api():
    return os.popen(f"docker ps | grep {token_gl}").read()

@app.post('/api/ctf')
def ctf_api():
    run_docker(token_gl)
    return os.popen(f"docker ps | grep {token_gl}").read()

@app.get('/api/ctf/{token}')
def ctf_api(token:str):
    try:
        os.system(f"docker kill {token}")
    except:
        return 'failed'
    return 'successful'