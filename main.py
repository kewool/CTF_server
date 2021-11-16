from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from db import *


app = FastAPI()
templates = Jinja2Templates(directory="pages")

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
    return os.popen(f"docker ps | grep {token}").read()

@app.post('/api/ctf')
def ctf_api():
    token="abcd"
    os.system(f"docker run -d --name {token} -p 3000 ctf_1")
    return os.popen(f"docker ps | grep {token}").read()