import pytest
from website import create_app, db
import os
# from website.models import User, Student, Trip, AppSettings


@pytest.fixture()
def app():
    """
    Create a new Flask app instance for each test run,
    configured to use TestingConfig.
    """
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()

    # Server config to allow url_for outside of request context
    flask_app.config['SERVER_NAME'] = 'localhost'
    flask_app.config['PREFERRED_URL_SCHEME'] = 'https'

    # Establish app context for DB setup
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()
        # Close all database connections to prevent ResourceWarning
        db.engine.dispose()


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
    from website.models import User
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
    from website.models import User
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
    from website.models import User
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
    from website.models import User
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


@pytest.fixture()
def sample_trip(app):
    """
    Create a sample trip in the database.
    """
    from website.models import Trip
    trip = Trip(
        trip_name="Trip 1",
        trip_type="backpacking",
        capacity=10,
        address="123 Main St",
        water=False,
        tent=True,
        description="A challenging backpacking adventure"
    )
    db.session.add(trip)
    db.session.commit()
    return trip


@pytest.fixture()
def sample_student(app):
    """
    Create a sample student in the database.
    """
    from website.models import Student
    student = Student(
        student_id="S001",
        email="student1@colby.edu",
        first_name="John",
        last_name="Doe",
        gender="Male",
        dorm="Dana",
        athletic_team="Soccer",
        water_comfort=4,
        tent_comfort=5
    )
    db.session.add(student)
    db.session.commit()
    return student


@pytest.fixture()
def sample_student_with_trip(app, sample_trip):
    """
    Create a sample student assigned to a trip.
    """
    from website.models import Student
    student = Student(
        student_id="S002",
        email="student2@colby.edu",
        first_name="Jane",
        last_name="Smith",
        gender="Female",
        dorm="West",
        trip_id=sample_trip.id
    )
    db.session.add(student)
    db.session.commit()
    return student


@pytest.fixture()
def app_settings(app):
    """
    Create app settings in the database.
    """
    from website.models import AppSettings
    settings = AppSettings(show_trips_to_students=False)
    db.session.add(settings)
    db.session.commit()
    return settings