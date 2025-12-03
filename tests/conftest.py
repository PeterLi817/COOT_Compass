import pytest
from website import create_app
import os

# This file is where we can create fixtures and set up the testing environment

@pytest.fixture()
def test_client():
    """
    Pytest fixture to create a Flask test client with TestingConfig.
    """
    # Set the Testing configuration prior to creating the Flask application
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()
    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as test_client:
        yield test_client