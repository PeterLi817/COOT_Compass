import pytest
from website import create_app, db
import os
from website.models import User

# This file is where we can create fixtures and set up the testing environment

@pytest.fixture()
def app():
    """
    Create a new Flask app instance for each test run,
    configured to use TestingConfig.
    """
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()

    # Establish app context for DB setup
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def test_client(app):
    """
    Create a clean test client for each test.
    """
    with app.test_client() as client:
        yield client



@pytest.fixture()
def admin_manager_user(app):
    """
    Create a test admin_manager user in the database.
    """
    user = User(
        email="admin_manager@colby.edu",
        first_name="Admin",
        last_name="Manager",
        role="admin_manager",
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def admin_user(app):
    """
    Create a test admin user in the database.
    """
    user = User(
        email="admin@colby.edu",
        first_name="Test",
        last_name="Admin",
        role="admin",
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def student_user(app):
    """
    Create a test student user in the database.
    """
    user = User(
        email="student@colby.edu",
        first_name="Test",
        last_name="Student",
        role="student",
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def no_role_user(app):
    """
    Create a test user with no role in the database.
    """
    user = User(
        email="norole@colby.edu",
        first_name="No",
        last_name="Role",
        role=None,
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def logged_in_admin_manager(test_client, admin_manager_user):
    """
    Return a test client with admin_manager already logged in.
    """
    with test_client.session_transaction() as sess:
        sess['_user_id'] = admin_manager_user.get_id()
        sess['_fresh'] = True

    return test_client


@pytest.fixture()
def logged_in_admin(test_client, admin_user):
    """
    Return a test client with admin already logged in.
    """
    with test_client.session_transaction() as sess:
        sess['_user_id'] = admin_user.get_id()
        sess['_fresh'] = True

    return test_client


@pytest.fixture()
def logged_in_student(test_client, student_user):
    """
    Return a test client with student already logged in.
    """
    with test_client.session_transaction() as sess:
        sess['_user_id'] = student_user.get_id()
        sess['_fresh'] = True

    return test_client


@pytest.fixture()
def logged_in_no_role(test_client, no_role_user):
    """
    Return a test client with user (no role) already logged in.
    """
    with test_client.session_transaction() as sess:
        sess['_user_id'] = no_role_user.get_id()
        sess['_fresh'] = True

    return test_client