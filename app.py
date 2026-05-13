"""Main application entry point for COOT Compass."""

import os
import threading
import webbrowser

from waitress import serve
from website import create_app

app = create_app()


def open_browser():
    """Open browser after server starts."""
    webbrowser.open("http://127.0.0.1:5000")


if __name__ == '__main__':

    # Development mode
    if os.environ.get('ENVIRONMENT') == 'development':
        app.run(debug=True)

    # Local packaged app mode
    else:
        threading.Timer(1.5, open_browser).start()

        serve(
            app,
            host='127.0.0.1',
            port=5000,
            threads=8
        )