import os
from datetime import datetime


"""
This module is responsible for logging errors to a file.
"""


# Error log directory in AppData\Roaming
appdata_dir = os.path.join(os.getenv('APPDATA'), 'Screen_Time_Tracker')
os.makedirs(appdata_dir, exist_ok=True)
ERROR_LOG_PATH = os.path.join(appdata_dir, 'error_log.txt')

def log(e: Exception) -> None:
    # create file if not exist
    os.makedirs(os.path.dirname(ERROR_LOG_PATH), exist_ok=True)
    # save to log file
    with open(ERROR_LOG_PATH, 'a') as f:
        f.write(f'{datetime.now()}: {e}\n')
