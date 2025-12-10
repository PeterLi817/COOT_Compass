"""Functional tests for database models.

Tests focus on database interactions, relationships, and constraints
with a real database instance.
"""
import pytest
from website.models import User, Student, Trip, AppSettings
from website import db


class TestUserModelDatabase:
    """Test cases for User model database operations."""

    def test_create_user(self, app):
        """Test creating and saving a user to the database."""
        with app.app_context():
            user = User(
                email="newuser@colby.edu",
                first_name="New",
                last_name="User",
                role="student"
            )
            db.session.add(user)
            db.session.commit()

            # Retrieve and verify
            retrieved = User.query.filter_by(email="newuser@colby.edu").first()
            assert retrieved is not None
            assert retrieved.email == "newuser@colby.edu"
            assert retrieved.first_name == "New"
            assert retrieved.last_name == "User"
            assert retrieved.role == "student"

    def test_user_email_is_primary_key(self, app):
        """Test that email serves as the primary key."""
        with app.app_context():
            user = User(
                email="pk_test@colby.edu",
                first_name="PK",
                last_name="Test",
                role="admin"
            )
            db.session.add(user)
            db.session.commit()

            # Query by primary key (email)
            retrieved = db.session.get(User, "pk_test@colby.edu")
            assert retrieved is not None
            assert retrieved.email == "pk_test@colby.edu"

    def test_user_student_relationship(self, app):
        """Test one-to-one relationship between User and Student."""
        with app.app_context():
            user = User(
                email="student_rel@colby.edu",
                first_name="Student",
                last_name="Rel",
                role="student"
            )
            db.session.add(user)
            db.session.commit()

            student = Student(
                student_id="S11111",
                first_name="Student",
                last_name="Rel",
                email="student_rel_own@colby.edu",
                user_email="student_rel@colby.edu"
            )
            db.session.add(student)
            db.session.commit()

            # Test relationship from user side
            retrieved_user = db.session.get(User, "student_rel@colby.edu")
            assert retrieved_user.student is not None
            assert retrieved_user.student.student_id == "S11111"

            # Test backref from student side
            retrieved_student = Student.query.filter_by(student_id="S11111").first()
            assert retrieved_student.user is not None
            assert retrieved_student.user.email == "student_rel@colby.edu"


class TestStudentModelDatabase:
    """Test cases for Student model database operations."""

    def test_create_student(self, app):
        """Test creating and saving a student to the database."""
        with app.app_context():
            student = Student(
                student_id="S99999",
                first_name="Test",
                last_name="Student",
                email="teststudent@colby.edu",
                trip_pref_1="backpacking",
                trip_pref_2="canoeing",
                trip_pref_3="basecamp",
                dorm="Dana",
                athletic_team="Soccer",
                gender="female",
                water_comfort=4,
                tent_comfort=5,
                hometown="Portland",
                poc=True,
                fli_international=False
            )
            db.session.add(student)
            db.session.commit()

            # Retrieve and verify
            retrieved = Student.query.filter_by(student_id="S99999").first()
            assert retrieved is not None
            assert retrieved.first_name == "Test"
            assert retrieved.last_name == "Student"
            assert retrieved.trip_pref_1 == "backpacking"
            assert retrieved.water_comfort == 4
            assert retrieved.poc is True

    def test_student_email_unique_constraint(self, app):
        """Test that student emails must be unique."""
        with app.app_context():
            student1 = Student(
                student_id="S11111",
                first_name="First",
                last_name="Student",
                email="duplicate@colby.edu"
            )
            db.session.add(student1)
            db.session.commit()

            # Try to create another student with same email
            student2 = Student(
                student_id="S22222",
                first_name="Second",
                last_name="Student",
                email="duplicate@colby.edu"
            )
            db.session.add(student2)

            with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
                db.session.commit()
            db.session.rollback()

    def test_student_id_unique_constraint(self, app):
        """Test that student_id must be unique."""
        with app.app_context():
            student1 = Student(
                student_id="S33333",
                first_name="First",
                last_name="Student",
                email="first@colby.edu"
            )
            db.session.add(student1)
            db.session.commit()

            # Try to create another student with same student_id
            student2 = Student(
                student_id="S33333",
                first_name="Second",
                last_name="Student",
                email="second@colby.edu"
            )
            db.session.add(student2)

            with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
                db.session.commit()
            db.session.rollback()

    def test_student_trip_relationship(self, app):
        """Test relationship between Student and Trip."""
        with app.app_context():
            trip = Trip(
                trip_type="backpacking",
                trip_name="Mountain Trek",
                capacity=12,
                water=False,
                tent=True
            )
            db.session.add(trip)
            db.session.commit()

            student = Student(
                student_id="S44444",
                first_name="Trip",
                last_name="Tester",
                email="triptester@colby.edu",
                trip_id=trip.id
            )
            db.session.add(student)
            db.session.commit()

            # Test relationship from student side
            retrieved_student = Student.query.filter_by(student_id="S44444").first()
            assert retrieved_student.trip is not None
            assert retrieved_student.trip.trip_name == "Mountain Trek"

            # Test backref from trip side
            retrieved_trip = db.session.get(Trip, trip.id)
            assert len(retrieved_trip.students) == 1
            assert retrieved_trip.students[0].student_id == "S44444"


class TestTripModelDatabase:
    """Test cases for Trip model database operations."""

    def test_create_trip(self, app):
        """Test creating and saving a trip to the database."""
        with app.app_context():
            trip = Trip(
                trip_type="canoeing",
                trip_name="River Adventure",
                capacity=10,
                address="123 River Rd, Maine",
                water=True,
                tent=False
            )
            db.session.add(trip)
            db.session.commit()

            # Retrieve and verify
            retrieved = Trip.query.filter_by(trip_name="River Adventure").first()
            assert retrieved is not None
            assert retrieved.trip_type == "canoeing"
            assert retrieved.capacity == 10
            assert retrieved.water is True
            assert retrieved.tent is False

    def test_trip_default_values(self, app):
        """Test that Trip boolean fields default to False."""
        with app.app_context():
            trip = Trip(
                trip_type="basecamp",
                trip_name="Base Camp Trip",
                capacity=15
            )
            db.session.add(trip)
            db.session.commit()

            retrieved = Trip.query.filter_by(trip_name="Base Camp Trip").first()
            assert retrieved.water is False
            assert retrieved.tent is False

    def test_trip_students_cascade(self, app):
        """Test that deleting a trip sets student trip_id to NULL."""
        with app.app_context():
            trip = Trip(
                trip_type="local exploration",
                trip_name="Local Tour",
                capacity=8
            )
            db.session.add(trip)
            db.session.commit()
            trip_id = trip.id

            student = Student(
                student_id="S55555",
                first_name="Cascade",
                last_name="Test",
                email="cascade@colby.edu",
                trip_id=trip_id
            )
            db.session.add(student)
            db.session.commit()

            # Delete the trip
            db.session.delete(trip)
            db.session.commit()

            # Check that student still exists but trip_id is NULL
            retrieved_student = Student.query.filter_by(student_id="S55555").first()
            assert retrieved_student is not None
            assert retrieved_student.trip_id is None

    def test_trip_multiple_students(self, app):
        """Test that a trip can have multiple students."""
        with app.app_context():
            trip = Trip(
                trip_type="backpacking",
                trip_name="Group Hike",
                capacity=15
            )
            db.session.add(trip)
            db.session.commit()

            # Add multiple students to the trip
            for i in range(3):
                student = Student(
                    student_id=f"S6666{i}",
                    first_name=f"Student{i}",
                    last_name="Multi",
                    email=f"multi{i}@colby.edu",
                    trip_id=trip.id
                )
                db.session.add(student)
            db.session.commit()

            # Verify all students are linked
            retrieved_trip = db.session.get(Trip, trip.id)
            assert len(retrieved_trip.students) == 3


class TestAppSettingsDatabase:
    """Test cases for AppSettings model database operations."""

    def test_appsettings_get_creates_settings(self, app):
        """Test that AppSettings.get() creates settings if none exist."""
        with app.app_context():
            settings = AppSettings.get()

            assert settings is not None
            assert settings.show_trips_to_students is False

            # Verify it was actually saved to database
            db_settings = AppSettings.query.first()
            assert db_settings is not None
            assert db_settings.id == settings.id

    def test_appsettings_get_returns_existing(self, app):
        """Test that AppSettings.get() returns existing settings."""
        with app.app_context():
            # Create settings
            existing = AppSettings(show_trips_to_students=True)
            db.session.add(existing)
            db.session.commit()
            existing_id = existing.id

            # Get should return the existing one
            settings = AppSettings.get()
            assert settings.id == existing_id
            assert settings.show_trips_to_students is True

    def test_appsettings_singleton_pattern(self, app):
        """Test that only one AppSettings record exists."""
        with app.app_context():
            # Call get() multiple times
            settings1 = AppSettings.get()
            settings2 = AppSettings.get()

            # Should be the same instance from database
            assert settings1.id == settings2.id

            # Should only be one record in database
            all_settings = AppSettings.query.all()
            assert len(all_settings) == 1

    def test_appsettings_update(self, app):
        """Test updating AppSettings values."""
        with app.app_context():
            settings = AppSettings.get()
            original_value = settings.show_trips_to_students

            # Update the value
            settings.show_trips_to_students = not original_value
            db.session.commit()

            # Retrieve again and verify
            updated_settings = AppSettings.get()
            assert updated_settings.show_trips_to_students == (not original_value)
