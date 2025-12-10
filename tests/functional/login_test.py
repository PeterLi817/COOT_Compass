def test_login_page(test_client):
# This test is not robust, just making sure that the fixtures work.
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/')
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'google' in response.data


def test_landing_page_admin_manager(logged_in_admin_manager):
# This test is not robust, just making sure that the fixtures work.
    response = logged_in_admin_manager.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert b'Groups' in response.data
    assert b'Trips' in response.data
    assert b'First Years' in response.data
    assert b'Settings' in response.data


def test_landing_page_admin(logged_in_admin):
# This test is not robust, just making sure that the fixtures work.
    response = logged_in_admin.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert b'Groups' in response.data
    assert b'Trips' in response.data
    assert b'First Years' in response.data
    assert b'Settings' in response.data

def test_landing_no_access(logged_in_no_role):
# This test is not robust, just making sure that the fixtures work.
    response = logged_in_no_role.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert b'Logged in as' in response.data
    assert b'You do not have access' in response.data
    assert b'Logout' in response.data

