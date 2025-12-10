"""Flask application factory for COOT Compass.

This module initializes the Flask application, configures the database,
sets up authentication, and registers all blueprints. It serves as the
central configuration point for the application.
"""

import os
from flask import Flask
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
    """Create and configure the Flask application instance.

    Initializes the Flask app with configuration from environment variables,
    sets up the database connection, configures Flask-Login for authentication,
    initializes OAuth for Google authentication, and registers all blueprints.

    Returns:
        Flask: The configured Flask application instance.

    Raises:
        ValueError: If SECRET_KEY environment variable is not set.
    """
    app = Flask(__name__)

    from .views import main # pylint: disable=import-outside-toplevel
    from .fill_db import add_fake_data #for development purposes
    from .auth import auth_blueprint, init_oauth # pylint: disable=import-outside-toplevel
    from .api_routes import api # pylint: disable=import-outside-toplevel
    from flask_login import LoginManager # pylint: disable=import-outside-toplevel
    from .models import User, Student, Trip, AppSettings # pylint: disable=import-outside-toplevel

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
        """Load a user by email for Flask-Login session management.

        This callback is used by Flask-Login to reload the user object
        from the user ID stored in the session.

        Args:
            email (str): The email address of the user to load.

        Returns:
            User: The User object if found, None otherwise.
        """
        return db.session.get(User, email)

    app.register_blueprint(main)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(api)

    with app.app_context():
        db.create_all()

    return app
