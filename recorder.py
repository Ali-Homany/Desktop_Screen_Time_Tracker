import win32gui
import win32process
import wmi
import time
import os
from datetime import datetime
from db import add_record


# Error log directory in AppData\Roaming
appdata_dir = os.path.join(os.getenv('APPDATA'), 'Screen_Time_Tracker')
os.makedirs(appdata_dir, exist_ok=True)
ERROR_LOG_PATH = os.path.join(appdata_dir, 'error_log.txt')

c = wmi.WMI()

def get_active_window_info() -> dict:
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        for process in c.Win32_Process(ProcessId=pid):
            app_name = process.Name.replace('.exe', '').capitalize()
            if process.Name.lower() == 'code.exe':
                app_name = 'Visual Studio Code'
            return {
                'title': win32gui.GetWindowText(hwnd),
                'app_name': app_name,
                'exe_path': process.ExecutablePath
            }
    except Exception as e:
        log(f"Error getting window info: {e}")
        return {'title': 'Unknown', 'app_name': 'Unknown', 'exe_path': 'Unknown'}


batch_size = 30
batch_records = []

def record_active_window() -> None:
    global batch_records
    window_info = get_active_window_info()
    window_info['timestamp'] = int(time.time())
    batch_records.append(window_info)
    if len(batch_records) >= batch_size or time.time() - batch_records[0]['timestamp'] >= batch_size:
        for record in batch_records:
            add_record(record['app_name'], record['exe_path'], record['timestamp'])
        batch_records = []


def log(e: Exception) -> None:
    # create file if not exist
    os.makedirs(os.path.dirname(ERROR_LOG_PATH), exist_ok=True)
    # save to log file
    with open(ERROR_LOG_PATH, 'a') as f:
        f.write(f'{datetime.now()}: {e}\n')

if __name__ == '__main__':
    last_recorded = time.time()
    while True:
        try:
            record_active_window()
            last_recorded = time.time()
        except Exception as e:
            log(e)
        time.sleep(max(0, 1 - (time.time() - last_recorded)))
