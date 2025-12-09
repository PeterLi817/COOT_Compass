from flask import Flask
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ENVIRONMENT = os.getenv('ENVIRONMENT')
SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
if ENVIRONMENT == 'production' and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    from .views import main
    from .models import User, db
    from .fill_db import add_fake_data #for development purposes
    from .auth import auth_blueprint, init_oauth
    from .api_routes import api
    from flask_login import LoginManager

    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set")
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_message = ''  # Disable default flash message
    login_manager.login_view = 'auth.login_page'  # public login page, not protected
    init_oauth(app)

    @login_manager.user_loader
    def load_user(email):
        return db.session.get(User, email)

    app.register_blueprint(main)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(api)

    with app.app_context():
        db.create_all()

    return app