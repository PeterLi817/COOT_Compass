"""Authentication routes and OAuth integration for COOT Compass.

This module handles user authentication using Google OAuth, user creation,
and session management. It integrates with Flask-Login for session handling
and automatically assigns roles based on student database records.
"""
import os

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user

from authlib.integrations.flask_client import OAuth

from website import db
from .models import User, Student

auth_blueprint = Blueprint('auth', __name__)

oauth = OAuth()
google = None
AUTH_REDIRECT_URI = 'auth.authorize'

@auth_blueprint.route('/')
def login_page():
    """Display the login page or redirect authenticated users.

    If the user is already authenticated, redirects them to the appropriate
    page based on their role. Otherwise, displays the login page.

    Returns:
        Response: Rendered login template or redirect to appropriate view.
    """
    if current_user.is_authenticated:
        if current_user.role is None:
            return redirect(url_for('main.no_access'))
        if current_user.role=='student':
            return redirect(url_for('main.student_view'))
        return redirect(url_for('main.groups'))
    return render_template('login.html')


def init_oauth(app):
    """Initialize OAuth and register Google provider with the Flask app.

    Configures Google OAuth using client credentials from environment variables.
    Sets up the OAuth client with OpenID Connect scopes for email and profile.

    Args:
        app (Flask): The Flask application instance to configure.

    Raises:
        ValueError: If GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET are not set
            in environment variables.
    """
    global google
    oauth.init_app(app)

    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

    if not client_id or not client_secret:
        raise ValueError("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set")

    google = oauth.register(
        name="google",
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_id=client_id,
        client_secret=client_secret,
        client_kwargs={"scope": "openid email profile"},
    )

@auth_blueprint.route('/login')
def login():
    """Initiate Google OAuth login flow.

    Redirects the user to Google's authorization page to begin the
    OAuth authentication process. If user is already authenticated,
    redirects to the home page.

    Returns:
        Response: Redirect to Google OAuth authorization page or home page.
    """
    if current_user.is_authenticated:
        return redirect(url_for('auth.login_page'))
    redirect_uri = url_for(AUTH_REDIRECT_URI, _external=True)
    return google.authorize_redirect(redirect_uri)

@auth_blueprint.route('/authorize')
def authorize():
    """Handle OAuth callback and authenticate user.

    Processes the OAuth callback from Google, retrieves user information,
    and either creates a new user or logs in an existing user. Automatically
    assigns the 'student' role if the user's email exists in the Student
    database. Links the User and Student records if applicable.

    The Google user info format includes:
        - id: Google user ID
        - email: User's email address
        - verified_email: Email verification status
        - name: Full name
        - given_name: First name
        - family_name: Last name
        - picture: Profile picture URL
        - hd: Hosted domain (e.g., 'colby.edu')

    Returns:
        Response: Redirect to appropriate page based on user role:
            - 'no_access' if user has no role
            - 'student_view' if user is a student
            - 'groups' for admin/admin_manager roles
    """
    token = google.authorize_access_token()
    resp = google.get('https://www.googleapis.com/oauth2/v1/userinfo', token=token)
    google_user = resp.json()

    app_user = get_user(google_user['email'])
    if not app_user:
        app_user = create_new_user(google_user)
    else:
        # If user exists but role is None, check if they should be a student
        student = Student.query.filter_by(email=google_user['email']).first()
        if student:
            app_user.student = student
            if app_user.role is None:
                app_user.role = 'student'
            db.session.commit()

    login_user(app_user)
    if app_user.role is None:
        return redirect(url_for('main.no_access'))
    if app_user.role=='student':
        return redirect(url_for('main.student_view'))
    return redirect(url_for('main.groups'))

@auth_blueprint.route('/logout')
@login_required
def logout():
    """Log out the current user and redirect to login page.

    Ends the user's session and redirects them to the login page.

    Returns:
        Response: Redirect to the login page.
    """
    logout_user()
    return redirect(url_for('auth.login_page'))

def get_user(email):
    """Retrieve a user from the database by email address.

    Args:
        email (str): The email address to search for.

    Returns:
        User: The User object if found, None otherwise.
    """
    existing_user = User.query.filter_by(email=email).first()
    return existing_user

def create_new_user(user):
    """Create a new user account from Google OAuth user information.

    Creates a new User record with information from the Google OAuth response.
    If the user's email exists in the Student database, automatically assigns
    the 'student' role and links the User and Student records.

    Args:
        user (dict): Dictionary containing Google user information with keys:
            - email: User's email address
            - given_name: User's first name
            - family_name: User's last name

    Returns:
        User: The newly created User object.
    """
    # Check if this email exists in the Student database
    student = Student.query.filter_by(email=user['email']).first()

    # Set role based on whether they're a student
    role = 'student' if student else None

    new_user = User(
        email=user['email'],
        first_name=user['given_name'],
        last_name=user['family_name'],
        role=role
    )

    # If this user is a student, link the user & student together
    if student:
        new_user.student = student

    db.session.add(new_user)
    db.session.commit()

    return new_user
