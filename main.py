# Auto-refresh the database when needed
from utils.db import is_transformation_needed, transform_new_data
import time

def auto_refresh():
    while True:
        # revoke etl process if needed
        time_left = is_transformation_needed()
        if time_left < 10:
            transform_new_data()
        time.sleep(time_left)


# Start the auto-refresh thread
import threading
threading.Thread(target=auto_refresh, daemon=True).start()


# Open the webapp
import webbrowser

PORT = 8050
webbrowser.open(f'http://127.0.0.1:{PORT}/')


# retrieve user preferences
import json
import os

settings_path = os.path.join(os.path.expanduser('~'), 'Documents', 'Screen_Time_Tracker', 'settings.json')
if os.path.exists(settings_path):
    with open(settings_path, 'r') as f:
        config = json.load(f)
else:
    config = {
        'theme': 'light',
        'daily_goal': None
    }


# Set up the logger
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger('waitress').setLevel(logging.ERROR)
logging.info(f'Server running on http://127.0.0.1:{PORT}')


# Run the webapp
from app import create_app
import waitress

app = create_app(config)
HOST = 'localhost'
waitress.serve(app, host=HOST, port=PORT)
