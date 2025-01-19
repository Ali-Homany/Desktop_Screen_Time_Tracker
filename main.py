import os
import time
import json
import logging
import threading
import webbrowser
import waitress
from app import create_app
from utils.db import is_transformation_needed, transform_new_data

"""
This module serves as the main entry point for the webapp application.
It is responsible for setup, starting the webapp server, and auto-refreshing the database when needed.
"""


def auto_refresh():
    """Auto-refresh the database when needed."""
    while True:
        # revoke etl process if needed
        time_left = is_transformation_needed()
        if time_left < 10:
            transform_new_data()
        time.sleep(time_left)


# Start the auto-refresh thread
threading.Thread(target=auto_refresh, daemon=True).start()


# Open the webapp
PORT = 8050
webbrowser.open(f'http://127.0.0.1:{PORT}/')


# retrieve user preferences
settings_path = os.path.join(
    os.path.expanduser('~'),
    'Documents', 'Screen_Time_Tracker', 'settings.json'
)
if os.path.exists(settings_path):
    with open(settings_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
else:
    config = {
        'theme': 'light',
        'daily_goal': None
    }


# Set up the logger
logging.basicConfig(level=logging.INFO)
logging.getLogger('waitress').setLevel(logging.ERROR)
logging.info('Server running on http://127.0.0.1:%s', PORT)


# Run the webapp
app = create_app(config)
HOST = 'localhost'
waitress.serve(app, host=HOST, port=PORT)
