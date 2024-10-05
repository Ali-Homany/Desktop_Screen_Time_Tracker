from app import create_app
from utils.db import is_transformation_needed, transform_new_data
import threading
import time
import webbrowser


# Auto-refresh the database when needed
def auto_refresh():
    while True:
        # revoke etl process if needed
        time_left = is_transformation_needed()
        print('time left ', time_left)
        if time_left == 0:
            transform_new_data()
        time.sleep(time_left)


# Start the auto-refresh thread
threading.Thread(target=auto_refresh, daemon=True).start()

# Open the webapp
port = 8050
webbrowser.open(f'http://127.0.0.1:{port}/')

# Run the webapp
app = create_app()
app.run(debug=False, port=port)
