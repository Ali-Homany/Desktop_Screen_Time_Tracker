import win32gui
import win32process
import wmi
import time
import os
from datetime import datetime
from db import add_record, get_all_apps_names, update_app_icon
from icon_extractor import extract_icon
import threading


# Error log directory in AppData\Roaming
appdata_dir = os.path.join(os.getenv('APPDATA'), 'Screen_Time_Tracker')
os.makedirs(appdata_dir, exist_ok=True)
ERROR_LOG_PATH = os.path.join(appdata_dir, 'error_log.txt')
icons_dir = os.path.join(os.path.expanduser('~'), 'Documents', 'Screen_Time_Tracker', 'Icons')
os.makedirs(icons_dir, exist_ok=True)

c = wmi.WMI()

def get_active_window_info() -> dict:
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        for process in c.Win32_Process(ProcessId=pid):
            if not process:
                return {'title': 'Unknown', 'app_name': 'Unknown', 'exe_path': 'Unknown'}
            app_name = process.Name.replace('.exe', '').capitalize()
            if process.Name.lower() == 'code.exe':
                app_name = 'Visual Studio Code'
            return {
                'title': win32gui.GetWindowText(hwnd),
                'app_name': app_name or 'Unknown',
                'exe_path': process.ExecutablePath or 'Unknown'
            }
    except Exception as e:
        log(f"Error getting window info: {e}")
        return {'title': 'Unknown', 'app_name': 'Unknown', 'exe_path': 'Unknown'}

def save_app_icon(app_info: dict) -> None:
    try:
        icon_path = extract_icon(app_info['app_name'], app_info['exe_path'], icons_dir)
    except Exception as e:
        log(f"Error extracting icon: {e}")
        icon_path = 'Unknown'
    # update app record adding the icon
    update_app_icon(app_info['app_name'], icon_path, app_info['exe_path'])

batch_size = 30
batch_records = []
unique_apps_names = set(get_all_apps_names())

def record_active_window() -> None:
    global batch_records
    window_info = get_active_window_info()
    # add new app to unique apps names
    if window_info['app_name'] not in unique_apps_names:
        unique_apps_names.add(window_info['app_name'])
        threading.Thread(target=save_app_icon, args=(window_info,)).start()
    window_info['timestamp'] = int(time.time())
    # add new record to batch
    batch_records.append(window_info)
    # insert batch to db if its size reached its threshold
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
