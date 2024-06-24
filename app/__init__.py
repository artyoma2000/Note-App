from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os

# Инициализация Flask-приложения
app = Flask(__name__, static_folder='../static', template_folder='templates')
app.config['SECRET_KEY'] = 'your_secret_key'  # Замените на случайную строку
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация расширений
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Создание базы данных при необходимости
if not os.path.exists('instance/app.db'):
    with app.app_context():
        db.create_all()

from app import routes
