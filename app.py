"""Main application entry point for COOT Compass.

This module initializes the Flask application and serves as the entry point
for running the application in development mode.
"""

from website import create_app

app = create_app()

if __name__ == '__main__':
    app.run()
