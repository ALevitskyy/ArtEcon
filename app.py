from flask import Flask
import os
from flask_script import Manager
from flask_basicauth import BasicAuth
from flask.ext.session import Session
basedir=os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config["SQLALCHEMY_DATABASE_URI"]=os.environ['DATABASE_URL']
app.config["SQLALCHEMY_COMMIT_OR_TEARDOWN"]=True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['BASIC_AUTH_USERNAME'] = os.environ['SECRET_KEY']
app.config['BASIC_AUTH_PASSWORD'] = os.environ['SECRET_KEY']
Session(app)
basic_auth = BasicAuth(app)
manager=Manager(app)

from models import db

db.init_app(app)


