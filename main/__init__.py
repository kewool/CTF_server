from flask import Flask, render_template, request, redirect, url_for, session, abort
from flask_wtf.csrf import CSRFProtect, CSRFError
import os
import subprocess
import random as rd
import datetime
import logging
from db import *

app = Flask(__name__, template_folder="pages/")
csrf = CSRFProtect(app)
logging.basicConfig(filename = "logs/project.log", level = logging.INFO)
host = "ctf.kewool.net"
dockerHost = "ctf.nahee.kim"
SECRET_KEY = os.urandom(32)
