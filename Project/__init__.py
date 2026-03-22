#--------------------------------Imports--------------------------------
import os
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

#----------------------------Flask app setup-------------------------------

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a7154f7d95055c045d0a85e4'

#-----------------------------Database setup-------------------------------

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'StageMetGert.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()
Migrate(app, db)

with app.app_context():
    db.init_app(app)
    db.create_all()

# -----------------------------Login setup---------------------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
