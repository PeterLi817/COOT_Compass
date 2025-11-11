from flask import Flask
from views import main
from models import User, db
from fill_db import add_fake_data #for development purposes
from auth import auth_blueprint
from flask_login import LoginManager
from auth import init_oauth

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret_key' # Simple for development, replace in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_message = ''  # Disable default flash message
login_manager.login_view = 'auth.login_page'  # public login page, not protected
init_oauth(app)

@login_manager.user_loader
def load_user(email):
    return User.query.get(email)

app.register_blueprint(main)
app.register_blueprint(auth_blueprint)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create database tables
        add_fake_data()

    app.run(debug=True)
