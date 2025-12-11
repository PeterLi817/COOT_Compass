"""Unit tests for database models.

Tests focus on model methods, properties, and logic in isolation
using mocks where appropriate.
"""
from unittest.mock import Mock, patch, MagicMock
import pytest
from website.models import User, Student, Trip, AppSettings


class TestUserModel:
    """Test cases for the User model."""

    def test_user_get_id_returns_email(self):
        """Test that get_id returns the user's email for Flask-Login."""
        user = User(
            email="test@colby.edu",
            first_name="Test",
            last_name="User",
            role="student"
        )
        assert user.get_id() == "test@colby.edu"

    def test_user_repr(self):
        """Test the string representation of a User."""
        user = User(
            email="admin@colby.edu",
            first_name="Admin",
            last_name="User",
            role="admin"
        )
        repr_str = repr(user)
        assert "admin@colby.edu" in repr_str
        assert "admin" in repr_str

    def test_user_get_id_with_none_email(self):
        """Test get_id when email is None."""
        user = User(
            email=None,
            first_name="Test",
            last_name="User"
        )
        assert user.get_id() is None


class TestStudentModel:
    """Test cases for the Student model."""

    def test_student_repr(self):
        """Test the string representation of a Student."""
        student = Student(
            id=1,
            student_id="S12345",
            first_name="Jane",
            last_name="Doe",
            email="jane@colby.edu",
            trip_id=5
        )
        repr_str = repr(student)
        assert "id=1" in repr_str
        assert "Jane Doe" in repr_str
        assert "trip_id=5" in repr_str

    def test_student_repr_without_trip(self):
        """Test Student repr when no trip is assigned."""
        student = Student(
            id=2,
            student_id="S67890",
            first_name="John",
            last_name="Smith",
            email="john@colby.edu",
            trip_id=None
        )
        repr_str = repr(student)
        assert "id=2" in repr_str
        assert "John Smith" in repr_str
        assert "trip_id=None" in repr_str


class TestTripModel:
    """Test cases for the Trip model."""

    def test_trip_repr(self):
        """Test the string representation of a Trip."""
        trip = Trip(
            id=10,
            trip_type="backpacking",
            trip_name="Mountain Adventure",
            capacity=12,
            water=False,
            tent=True,
            description="A great mountain adventure"
        )
        repr_str = repr(trip)
        assert "id=10" in repr_str
        assert "Mountain Adventure" in repr_str
        assert "backpacking" in repr_str
        assert "capacity=12" in repr_str


class TestAppSettingsModel:
    """Test cases for the AppSettings model."""

    @patch('website.models.AppSettings.query')
    @patch('website.models.db.session')
    def test_appsettings_get_returns_existing_settings(self, mock_session, mock_query):
        """Test that get() returns existing settings if they exist."""
        # Mock an existing settings record
        mock_settings = Mock(spec=AppSettings)
        mock_settings.show_trips_to_students = True
        mock_query.first.return_value = mock_settings

        result = AppSettings.get()

        assert result is mock_settings
        mock_query.first.assert_called_once()
        mock_session.add.assert_not_called()
        mock_session.commit.assert_not_called()

    @patch('website.models.AppSettings.query')
    @patch('website.models.db.session')
    def test_appsettings_get_creates_default_when_none_exist(self, mock_session, mock_query):
        """Test that get() creates default settings when none exist."""
        # Mock no existing settings
        mock_query.first.return_value = None

        result = AppSettings.get()

        mock_query.first.assert_called_once()
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

        # Check that the created settings has the default value
        assert result.show_trips_to_students is False

    @patch('website.models.AppSettings.query')
    @patch('website.models.db.session')
    def test_appsettings_get_creates_with_correct_default(self, mock_session, mock_query):
        """Test that get() creates settings with show_trips_to_students=False by default."""
        mock_query.first.return_value = None

        result = AppSettings.get()

        # Verify the default value is False
        assert hasattr(result, 'show_trips_to_students')
        assert result.show_trips_to_students is False


class TestModelAttributes:
    """Test cases for model attribute definitions."""

    def test_user_has_required_attributes(self):
        """Test that User model has all expected attributes."""
        user = User(
            email="test@colby.edu",
            first_name="Test",
            last_name="User",
            role="student"
        )
        assert hasattr(user, 'email')
        assert hasattr(user, 'first_name')
        assert hasattr(user, 'last_name')
        assert hasattr(user, 'role')
        assert hasattr(user, 'student')

    def test_student_has_required_attributes(self):
        """Test that Student model has all expected attributes."""
        student = Student(
            student_id="S12345",
            first_name="Test",
            last_name="Student",
            email="student@colby.edu"
        )
        assert hasattr(student, 'id')
        assert hasattr(student, 'student_id')
        assert hasattr(student, 'first_name')
        assert hasattr(student, 'last_name')
        assert hasattr(student, 'email')
        assert hasattr(student, 'trip_id')
        assert hasattr(student, 'trip_pref_1')
        assert hasattr(student, 'trip_pref_2')
        assert hasattr(student, 'trip_pref_3')
        assert hasattr(student, 'dorm')
        assert hasattr(student, 'athletic_team')
        assert hasattr(student, 'gender')
        assert hasattr(student, 'notes')
        assert hasattr(student, 'water_comfort')
        assert hasattr(student, 'tent_comfort')
        assert hasattr(student, 'hometown')
        assert hasattr(student, 'poc')
        assert hasattr(student, 'fli_international')
        assert hasattr(student, 'allergies_dietary_restrictions')
        assert hasattr(student, 'user_email')

    def test_trip_has_required_attributes(self):
        """Test that Trip model has all expected attributes."""
        trip = Trip(
            trip_type="backpacking",
            trip_name="Test Trip",
            capacity=10
        )
        assert hasattr(trip, 'id')
        assert hasattr(trip, 'trip_type')
        assert hasattr(trip, 'trip_name')
        assert hasattr(trip, 'capacity')
        assert hasattr(trip, 'address')
        assert hasattr(trip, 'water')
        assert hasattr(trip, 'tent')
        assert hasattr(trip, 'description')
        assert hasattr(trip, 'students')

    def test_appsettings_has_required_attributes(self):
        """Test that AppSettings model has all expected attributes."""
        settings = AppSettings(show_trips_to_students=True)
        assert hasattr(settings, 'id')
        assert hasattr(settings, 'show_trips_to_students')
