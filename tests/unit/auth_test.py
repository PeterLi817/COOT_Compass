"""Unit tests for authentication module functions.

Tests focus on isolated function behavior using mocks and stubs,
without requiring full application context or database connections.
"""
import pytest
from unittest.mock import patch, MagicMock, Mock
from website.auth import get_user, create_new_user, init_oauth
from website.models import User, Student


class TestGetUser:
    """Test cases for the get_user function."""

    @patch('website.auth.User')
    def test_get_existing_user(self, mock_user_model):
        """Test retrieving an existing user by email."""
        # Mock the database query
        mock_user = Mock()
        mock_user.email = "admin@colby.edu"
        mock_user.first_name = "Test"
        mock_user.last_name = "Admin"
        mock_user.role = "admin"

        mock_user_model.query.filter_by.return_value.first.return_value = mock_user

        result = get_user("admin@colby.edu")

        assert result is not None
        assert result.email == "admin@colby.edu"
        assert result.first_name == "Test"
        assert result.last_name == "Admin"
        mock_user_model.query.filter_by.assert_called_once_with(email="admin@colby.edu")

    @patch('website.auth.User')
    def test_get_nonexistent_user(self, mock_user_model):
        """Test that get_user returns None for non-existent email."""
        mock_user_model.query.filter_by.return_value.first.return_value = None

        result = get_user("nonexistent@colby.edu")

        assert result is None
        mock_user_model.query.filter_by.assert_called_once_with(email="nonexistent@colby.edu")

    @patch('website.auth.User')
    def test_get_user_called_with_correct_email(self, mock_user_model):
        """Test that get_user queries with the correct email parameter."""
        mock_user_model.query.filter_by.return_value.first.return_value = None

        get_user("test@example.com")

        mock_user_model.query.filter_by.assert_called_once_with(email="test@example.com")


class TestCreateNewUser:
    """Test cases for the create_new_user function."""

    @patch('website.auth.db')
    @patch('website.auth.Student')
    @patch('website.auth.User')
    def test_create_user_without_student_record(self, mock_user_model, mock_student_model, mock_db):
        """Test creating a new user when no Student record exists."""
        # Mock Student.query to return None (no student record)
        mock_student_model.query.filter_by.return_value.first.return_value = None

        # Mock User constructor to return a mock user instance
        mock_user_instance = Mock()
        mock_user_instance.email = 'newuser@colby.edu'
        mock_user_instance.first_name = 'New'
        mock_user_instance.last_name = 'User'
        mock_user_instance.role = None
        mock_user_instance.student = None
        mock_user_model.return_value = mock_user_instance

        google_user = {
            'email': 'newuser@colby.edu',
            'given_name': 'New',
            'family_name': 'User'
        }

        result = create_new_user(google_user)

        # Verify the returned user exists and has correct attributes
        assert result is not None
        assert result.email == 'newuser@colby.edu'
        assert result.first_name == 'New'
        assert result.last_name == 'User'
        assert result.role is None
        assert result.student is None

        # Verify User was created with correct parameters
        mock_user_model.assert_called_once_with(
            email='newuser@colby.edu',
            first_name='New',
            last_name='User',
            role=None
        )
        # Verify database operations
        mock_db.session.add.assert_called_once_with(result)
        mock_db.session.commit.assert_called_once()

    @patch('website.auth.db')
    @patch('website.auth.Student')
    @patch('website.auth.User')
    def test_create_user_with_existing_student_record(self, mock_user_model, mock_student_model, mock_db):
        """Test creating a user when a matching Student record exists."""
        # Mock Student record
        mock_student = Mock()
        mock_student.student_id = '12345'
        mock_student.email = 'student@colby.edu'
        mock_student_model.query.filter_by.return_value.first.return_value = mock_student

        # Mock User instance with all expected attributes
        mock_user_instance = Mock()
        mock_user_instance.email = 'student@colby.edu'
        mock_user_instance.first_name = 'Jane'
        mock_user_instance.last_name = 'Doe'
        mock_user_instance.role = 'student'
        mock_user_instance.student = mock_student
        mock_user_model.return_value = mock_user_instance

        google_user = {
            'email': 'student@colby.edu',
            'given_name': 'Jane',
            'family_name': 'Doe'
        }

        result = create_new_user(google_user)

        # Verify the returned user exists and has correct attributes
        assert result is not None
        assert result.email == 'student@colby.edu'
        assert result.first_name == 'Jane'
        assert result.last_name == 'Doe'
        assert result.role == 'student'
        assert result.student is not None
        assert result.student == mock_student

        # Verify User was created with student role
        mock_user_model.assert_called_once_with(
            email='student@colby.edu',
            first_name='Jane',
            last_name='Doe',
            role='student'
        )
        # Verify database operations
        mock_db.session.add.assert_called_once_with(result)
        mock_db.session.commit.assert_called_once()

    @patch('website.auth.db')
    @patch('website.auth.Student')
    @patch('website.auth.User')
    def test_create_user_database_operations(self, mock_user_model, mock_student_model, mock_db):
        """Test that create_new_user performs correct database operations."""
        mock_student_model.query.filter_by.return_value.first.return_value = None
        mock_user_instance = Mock()
        mock_user_model.return_value = mock_user_instance

        google_user = {
            'email': 'test@colby.edu',
            'given_name': 'Test',
            'family_name': 'User'
        }

        create_new_user(google_user)

        # Verify the user was added to session and committed
        mock_db.session.add.assert_called_once_with(mock_user_instance)
        mock_db.session.commit.assert_called_once()

    @patch('website.auth.db')
    @patch('website.auth.Student')
    @patch('website.auth.User')
    def test_create_user_queries_student_by_email(self, mock_user_model, mock_student_model, mock_db):
        """Test that create_new_user queries Student table with correct email."""
        mock_student_model.query.filter_by.return_value.first.return_value = None
        mock_user_model.return_value = Mock()

        google_user = {
            'email': 'check@colby.edu',
            'given_name': 'Check',
            'family_name': 'Email'
        }

        create_new_user(google_user)

        mock_student_model.query.filter_by.assert_called_once_with(email='check@colby.edu')


class TestInitOAuth:
    """Test cases for OAuth initialization."""

    @patch('website.auth.oauth')
    @patch('os.getenv')
    def test_init_oauth_with_valid_credentials(self, mock_getenv, mock_oauth):
        """Test init_oauth successfully registers Google provider with valid credentials."""
        mock_app = Mock()
        mock_getenv.side_effect = lambda key: {
            'GOOGLE_CLIENT_ID': 'test_client_id',
            'GOOGLE_CLIENT_SECRET': 'test_client_secret'
        }.get(key)

        init_oauth(mock_app)

        # Verify OAuth was initialized with the app
        mock_oauth.init_app.assert_called_once_with(mock_app)
        # Verify Google provider was registered
        mock_oauth.register.assert_called_once()
        call_kwargs = mock_oauth.register.call_args[1]
        assert call_kwargs['name'] == 'google'
        assert call_kwargs['client_id'] == 'test_client_id'
        assert call_kwargs['client_secret'] == 'test_client_secret'

    @patch('website.auth.oauth')
    @patch('os.getenv')
    def test_init_oauth_missing_client_id(self, mock_getenv, mock_oauth):
        """Test that init_oauth raises ValueError when GOOGLE_CLIENT_ID is missing."""
        mock_app = Mock()
        mock_getenv.side_effect = lambda key: {
            'GOOGLE_CLIENT_ID': None,
            'GOOGLE_CLIENT_SECRET': 'test_secret'
        }.get(key)

        with pytest.raises(ValueError) as exc_info:
            init_oauth(mock_app)

        assert "GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set" in str(exc_info.value)

    @patch('website.auth.oauth')
    @patch('os.getenv')
    def test_init_oauth_missing_client_secret(self, mock_getenv, mock_oauth):
        """Test that init_oauth raises ValueError when GOOGLE_CLIENT_SECRET is missing."""
        mock_app = Mock()
        mock_getenv.side_effect = lambda key: {
            'GOOGLE_CLIENT_ID': 'test_id',
            'GOOGLE_CLIENT_SECRET': None
        }.get(key)

        with pytest.raises(ValueError) as exc_info:
            init_oauth(mock_app)

        assert "GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set" in str(exc_info.value)

    @patch('website.auth.oauth')
    @patch('os.getenv')
    def test_init_oauth_missing_both_credentials(self, mock_getenv, mock_oauth):
        """Test that init_oauth raises ValueError when both credentials are missing."""
        mock_app = Mock()
        mock_getenv.return_value = None

        with pytest.raises(ValueError) as exc_info:
            init_oauth(mock_app)

        assert "GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set" in str(exc_info.value)

    @patch('website.auth.oauth')
    @patch('os.getenv')
    def test_init_oauth_sets_correct_scopes(self, mock_getenv, mock_oauth):
        """Test that init_oauth configures correct OAuth scopes."""
        mock_app = Mock()
        mock_getenv.side_effect = lambda key: {
            'GOOGLE_CLIENT_ID': 'id',
            'GOOGLE_CLIENT_SECRET': 'secret'
        }.get(key)

        init_oauth(mock_app)

        call_kwargs = mock_oauth.register.call_args[1]
        assert 'client_kwargs' in call_kwargs
        assert call_kwargs['client_kwargs']['scope'] == 'openid email profile'
