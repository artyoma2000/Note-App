from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
import os

# Инициализация Flask-приложения
app = Flask(__name__, static_folder='../static', template_folder='templates')
app.config['SECRET_KEY'] = 'your_secret_key'  # Замените на случайную строку
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/dbname')
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
migrate = Migrate(app, db)  # Инициализация миграций

from app import routes, models  # Импорт моделей и маршрутов