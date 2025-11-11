from flask import Blueprint, render_template, redirect, url_for, flash
from flask import request, session
from models import db, User
from flask_login import login_user, login_required, logout_user, current_user
from authlib.integrations.flask_client import OAuth
import os

auth_blueprint = Blueprint('auth', __name__)

oauth = OAuth()
google = None
AUTH_REDIRECT_URI = 'auth.authorize'

@auth_blueprint.route('/')
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('main.groups'))
    return render_template('login.html')


def init_oauth(app):
    """Initialize OAuth and register Google provider."""
    global google
    oauth.init_app(app)

    google = oauth.register(
        name="google",
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        client_kwargs={"scope": "openid email profile"},
    )

@auth_blueprint.route('/login')
def login():
    redirect_uri = url_for(AUTH_REDIRECT_URI, _external=True)
    return google.authorize_redirect(redirect_uri)

@auth_blueprint.route('/authorize')
def authorize():
    """
    Authorize user and fetch user info from Google

    the user item is in the following format:
    {
        'id': '114544450990536914219',
        'email': 'bmjaff26@colby.edu',
        'verified_email': True,
        'name': 'Benjamin Jaffe',
        'given_name': 'Benjamin',
        'family_name': 'Jaffe',
        'picture': 'https://lh3.googleusercontent.com/a/ACg8ocJwc-igE1-1TWV732HsBwAAu8kC9JpfbLsPOGVQD1aO2Cp_9w=s96-c',
        'hd': 'colby.edu'
    }
    """
    token = google.authorize_access_token()
    resp = google.get('https://www.googleapis.com/oauth2/v1/userinfo', token=token)
    google_user = resp.json()
    print(google_user)

    app_user = get_user(google_user['email'])
    if not app_user:
        app_user = create_new_user(google_user)

    login_user(app_user)
    return redirect(url_for('main.groups'))

@auth_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login_page'))

def get_user(email):
    """
    Checks for existing user by email, if found return said user, else return None
    """
    existing_user = User.query.filter_by(email=email).first()
    return existing_user

def create_new_user(user):
    """
    This function exists so in the future, when we add roles and stuff
    we will add the roles here.
    """
    new_user = User(
        email=user['email'],
        first_name=user['given_name'],
        last_name=user['family_name'],
    )
    db.session.add(new_user)
    db.session.commit()
    return new_user
