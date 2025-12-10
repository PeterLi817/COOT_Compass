"""Functional tests for authentication routes.

Tests cover the authentication routes including login_page, login, authorize,
and logout, testing the full request/response cycle with mocked OAuth.
"""
from unittest.mock import patch, MagicMock

from website.models import User, Student
from website import db


class TestLoginPage:
    """Functional tests for the login_page route."""

    def test_unauthenticated_user_sees_login_page(self, test_client):
        """Test that unauthenticated users see the login page."""
        response = test_client.get('/')

        assert response.status_code == 200
        assert b'login' in response.data.lower()

    def test_authenticated_student_redirects_to_student_view(self, logged_in_student):
        """Test that authenticated student is redirected to student view."""
        response = logged_in_student.get('/', follow_redirects=False)

        assert response.status_code == 302
        assert '/student_view' in response.location

    def test_authenticated_admin_redirects_to_groups(self, logged_in_admin):
        """Test that authenticated admin is redirected to groups page."""
        response = logged_in_admin.get('/', follow_redirects=False)

        assert response.status_code == 302
        assert '/groups' in response.location

    def test_authenticated_admin_manager_redirects_to_groups(self, logged_in_admin_manager):
        """Test that authenticated admin_manager is redirected to groups page."""
        response = logged_in_admin_manager.get('/', follow_redirects=False)

        assert response.status_code == 302
        assert '/groups' in response.location

    def test_authenticated_user_no_role_redirects_to_no_access(self, logged_in_no_role):
        """Test that authenticated user with no role is redirected to no_access page."""
        response = logged_in_no_role.get('/', follow_redirects=False)

        assert response.status_code == 302
        assert '/no_access' in response.location


class TestLoginRoute:
    """Functional tests for the login route."""

    @patch('website.auth.google')
    def test_login_initiates_oauth_flow(self, mock_google, test_client):
        """Test that /login initiates Google OAuth flow."""
        mock_google.authorize_redirect.return_value = test_client.application.response_class(
            status=302,
            headers={'Location': 'https://accounts.google.com/o/oauth2/auth'}
        )

        test_client.get('/login', follow_redirects=False)

        # Verify google.authorize_redirect was called
        mock_google.authorize_redirect.assert_called_once()
        # Verify it was called with the correct redirect URI
        call_args = mock_google.authorize_redirect.call_args[0]
        assert 'authorize' in call_args[0]

class TestLogoutRoute:
    """Functional tests for the logout route."""

    def test_logout_redirects_authenticated_user(self, logged_in_admin):
        """Test that logout redirects authenticated user to login page."""
        response = logged_in_admin.get('/logout', follow_redirects=False)

        assert response.status_code == 302
        assert '/' in response.location

    def test_logout_clears_session(self, logged_in_student):
        """Test that logout clears the user session."""
        with logged_in_student.session_transaction() as sess:
            assert '_user_id' in sess

        logged_in_student.get('/logout')

        with logged_in_student.session_transaction() as sess:
            assert '_user_id' not in sess

    def test_logout_requires_authentication(self, test_client):
        """Test that logout requires user to be logged in."""
        response = test_client.get('/logout', follow_redirects=False)

        # Should redirect to login page since user is not authenticated
        assert response.status_code == 302

    def test_logout_denies_access_to_admin_pages(self, logged_in_admin):
        """Test that after logout, admin pages are no longer accessible."""
        # Verify admin can access groups page while logged in
        response = logged_in_admin.get('/groups', follow_redirects=False)
        assert response.status_code in [200, 302]  # May redirect but not denied

        # Logout
        logged_in_admin.get('/logout')

        # Verify groups page returns 401 Unauthorized
        response = logged_in_admin.get('/groups', follow_redirects=False)
        assert response.status_code == 401

        # Verify settings page also returns 401 Unauthorized
        response = logged_in_admin.get('/settings', follow_redirects=False)
        assert response.status_code == 401


    def test_logout_denies_access_to_student_pages(self, logged_in_student):
        """Test that after logout, student pages are no longer accessible."""
        # Verify student can access student_view page while logged in
        response = logged_in_student.get('/student_view', follow_redirects=False)
        assert response.status_code in [200, 302]  # May redirect but not denied

        # Logout
        logged_in_student.get('/logout')

        # Verify student_view page returns 401 Unauthorized
        response = logged_in_student.get('/student_view', follow_redirects=False)
        assert response.status_code == 401

    def test_logout_denies_access_to_trips_for_admin_manager(self, logged_in_admin_manager):
        """Test that after logout, admin_manager cannot access trips page."""
        # Verify admin_manager can access trips page while logged in
        response = logged_in_admin_manager.get('/trips', follow_redirects=False)
        assert response.status_code in [200, 302]  # May redirect but not denied

        # Logout
        logged_in_admin_manager.get('/logout')

        # Verify trips page returns 401 Unauthorized
        response = logged_in_admin_manager.get('/trips', follow_redirects=False)
        assert response.status_code == 401


class TestAuthorizeRoute:
    """Functional tests for the OAuth authorize callback route."""

    @patch('website.auth.google')
    def test_authorize_creates_new_user_without_student_record(self, mock_google, app, test_client):
        """Test that authorize creates a new user when one doesn't exist and no Student record."""
        with app.app_context():
            # Mock OAuth responses
            mock_google.authorize_access_token.return_value = {'access_token': 'fake_token'}
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'email': 'newuser@colby.edu',
                'given_name': 'New',
                'family_name': 'User'
            }
            mock_google.get.return_value = mock_response

            response = test_client.get('/authorize', follow_redirects=False)

            # Verify user was created
            user = User.query.filter_by(email='newuser@colby.edu').first()
            assert user is not None
            assert user.first_name == 'New'
            assert user.last_name == 'User'
            assert user.role is None

            # Should redirect to no_access since role is None
            assert response.status_code == 302
            assert '/no_access' in response.location

    @patch('website.auth.google')
    def test_authorize_creates_new_user_with_student_record(self, mock_google, app, test_client):
        """Test that authorize creates a new user and links to existing Student record."""
        with app.app_context():
            # Create a Student record first
            student = Student(
                student_id='12345',
                first_name='Jane',
                last_name='Doe',
                email='jane.doe@colby.edu',
                dorm='Test Dorm',
                gender='female'
            )
            db.session.add(student)
            db.session.commit()

            # Mock OAuth responses
            mock_google.authorize_access_token.return_value = {'access_token': 'fake_token'}
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'email': 'jane.doe@colby.edu',
                'given_name': 'Jane',
                'family_name': 'Doe'
            }
            mock_google.get.return_value = mock_response

            response = test_client.get('/authorize', follow_redirects=False)

            # Verify user was created with student role
            user = User.query.filter_by(email='jane.doe@colby.edu').first()
            assert user is not None
            assert user.role == 'student'
            assert user.student is not None
            assert user.student.student_id == '12345'

            # Should redirect to student_view
            assert response.status_code == 302
            assert '/student_view' in response.location

    @patch('website.auth.google')
    def test_authorize_existing_admin_user(self, mock_google, app, test_client, admin_user):  # pylint: disable=unused-argument
        """Test that authorize logs in existing admin user."""
        with app.app_context():
            # Mock OAuth responses
            mock_google.authorize_access_token.return_value = {'access_token': 'fake_token'}
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'email': 'admin@colby.edu',
                'given_name': 'Test',
                'family_name': 'Admin'
            }
            mock_google.get.return_value = mock_response

            response = test_client.get('/authorize', follow_redirects=False)

            # Should redirect to groups page for admin
            assert response.status_code == 302
            assert '/groups' in response.location

            # Verify user is logged in
            with test_client.session_transaction() as sess:
                assert '_user_id' in sess
                assert sess['_user_id'] == 'admin@colby.edu'

    @patch('website.auth.google')
    def test_authorize_upgrades_no_role_user_to_student(
        self, mock_google, app, test_client, no_role_user
    ):  # pylint: disable=unused-argument
        """Test that authorize upgrades existing user with no role to student
        when Student record exists.
        """
        with app.app_context():
            # Create a Student record with matching email
            student = Student(
                student_id='99999',
                first_name='No',
                last_name='Role',
                email='norole@colby.edu',
                dorm='Test Dorm',
                gender='other'
            )
            db.session.add(student)
            db.session.commit()

            # Mock OAuth responses
            mock_google.authorize_access_token.return_value = {'access_token': 'fake_token'}
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'email': 'norole@colby.edu',
                'given_name': 'No',
                'family_name': 'Role'
            }
            mock_google.get.return_value = mock_response

            response = test_client.get('/authorize', follow_redirects=False)

            # Verify user was updated to student role
            user = User.query.filter_by(email='norole@colby.edu').first()
            assert user.role == 'student'
            assert user.student is not None
            assert user.student.student_id == '99999'

            # Should redirect to student_view
            assert response.status_code == 302
            assert '/student_view' in response.location

    @patch('website.auth.google')
    def test_authorize_existing_user_no_student_record(
        self, mock_google, app, test_client, no_role_user
    ):  # pylint: disable=unused-argument
        """Test that authorize logs in existing user without upgrading
        when no Student record exists.
        """
        with app.app_context():
            # Mock OAuth responses
            mock_google.authorize_access_token.return_value = {'access_token': 'fake_token'}
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'email': 'norole@colby.edu',
                'given_name': 'No',
                'family_name': 'Role'
            }
            mock_google.get.return_value = mock_response

            response = test_client.get('/authorize', follow_redirects=False)

            # Verify user still has no role
            user = User.query.filter_by(email='norole@colby.edu').first()
            assert user.role is None

            # Should redirect to no_access
            assert response.status_code == 302
            assert '/no_access' in response.location

    @patch('website.auth.google')
    def test_authorize_admin_manager_redirects_to_groups(
        self, mock_google, app, test_client, admin_manager_user
    ):  # pylint: disable=unused-argument
        """Test that authorize redirects admin_manager to groups page."""
        with app.app_context():
            # Mock OAuth responses
            mock_google.authorize_access_token.return_value = {'access_token': 'fake_token'}
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'email': 'admin_manager@colby.edu',
                'given_name': 'Admin',
                'family_name': 'Manager'
            }
            mock_google.get.return_value = mock_response

            response = test_client.get('/authorize', follow_redirects=False)

            # Should redirect to groups page
            assert response.status_code == 302
            assert '/groups' in response.location
