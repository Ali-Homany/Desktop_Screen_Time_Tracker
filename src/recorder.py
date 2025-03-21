import os
import time
import threading
import wmi
import win32gui
import win32process
from db.db_init import create_session
from db.db_utils import add_record, get_all_apps_names, add_app
from utils.icon_extractor import extract_icon
from utils.logger import log


"""This module is responsible for recording the user's activity on the
computer. It uses the Windows API to get the current active window and its
process information. The process information is then used to determine the
application name and icon. Data then is sent to the database.
"""


# icons path
icons_dir = os.path.join(
    os.path.expanduser('~'),
    'Documents',
    'Screen_Time_Tracker',
    'Icons'
)
os.makedirs(icons_dir, exist_ok=True)


c = wmi.WMI()
db = create_session()
empty_record = {
    'title': 'Unknown',
    'app_name': 'Unknown',
    'exe_path': 'Unknown'
}


def get_active_window_info() -> dict:
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            processes = c.Win32_Process(ProcessId=pid)
        except wmi.x_wmi as wmi_error:
        # raise RuntimeError("Failed to get processes due to windows error")
            return empty_record
        for process in processes:
            if not process:
                # In case the process is not found, return default value
                return empty_record
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
        return empty_record


def save_new_app(app_info: dict) -> None:
    try:
        extract_icon(app_info['app_name'], app_info['exe_path'], icons_dir)
        add_app(
            db=db,
            app_name=app_info['app_name'],
            file_location=app_info['exe_path']
        )
    except Exception as e:
        log(f"Error extracting icon: {e}")


# batch size represents number of records to be inserted into database at once
batch_size = 30
batch_records = []
# unique apps names helps identify new apps
unique_apps_names = set(get_all_apps_names(db))


def record_active_window() -> None:
    global batch_records
    window_info = get_active_window_info() or empty_record
    # add new app to unique apps names
    if window_info['app_name'] not in unique_apps_names:
        unique_apps_names.add(window_info['app_name'])
        threading.Thread(target=save_new_app, args=(window_info,)).start()
    window_info['timestamp'] = int(time.time())
    # add new record to batch
    batch_records.append(window_info)
    # insert batch to db if its size reached its threshold
    if (len(batch_records) >= batch_size
        or time.time() - batch_records[0]['timestamp'] >= batch_size):
        for record in batch_records:
            add_record(
                db=db,
                app_name=record['app_name'],
                app_path=record['exe_path'],
                timestamp=record['timestamp']
            )
        batch_records = []


if __name__ == '__main__':
    last_recorded = time.time()
    while True:
        try:
            record_active_window()
            last_recorded = time.time()
        except Exception as e:
            log(e)
        time.sleep(max(0, 1 - (time.time() - last_recorded)))
