from app import create_app
from utils.db import is_transformation_needed, transform_new_data
import threading
import time
import webbrowser
import json
import os


# Auto-refresh the database when needed
def auto_refresh():
    while True:
        # revoke etl process if needed
        time_left = is_transformation_needed()
        print('time left ', time_left)
        if time_left < 10:
            transform_new_data()
        time.sleep(time_left)


# Start the auto-refresh thread
threading.Thread(target=auto_refresh, daemon=True).start()

# Open the webapp
port = 8050
webbrowser.open(f'http://127.0.0.1:{port}/')

# retrieve user preferences
settings_path = os.path.join(os.path.expanduser('~'), 'Documents', 'Screen_Time_Tracker', 'settings.json')
if os.path.exists(settings_path):
    with open(settings_path, 'r') as f:
        config = json.load(f)
else:
    config = {
        'theme': 'light',
        'daily_goal': None
    }

# Run the webapp
app = create_app(config)
app.run(debug=False, port=port)
