import win32gui
import win32process
import wmi
import time
import csv
import os
from datetime import datetime


# Error log directory in AppData\Roaming
appdata_dir = os.path.join(os.getenv('APPDATA'), 'ScreenTimeTracker')
ERROR_LOG_PATH = os.path.join(appdata_dir, 'error_log.txt')

# CSV file directory in Documents
documents_dir = os.path.join(os.path.expanduser('~'), 'Documents', 'ScreenTimeTracker')
CSV_FILE_PATH = os.path.join(documents_dir, 'active_apps_log.csv')

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


def record_active_window() -> None:
    timestamp = time.time()
    window_info = get_active_window_info()
    
    # create csv file if it doesnt exist
    if not os.path.exists(CSV_FILE_PATH):
        os.makedirs(os.path.dirname(CSV_FILE_PATH), exist_ok=True)
        with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['timestamp', 'title', 'app_name', 'exe_path']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
    with open(CSV_FILE_PATH, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['timestamp', 'title', 'app_name', 'exe_path']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({
            'timestamp': timestamp,
            'title': window_info['title'],
            'app_name': window_info['app_name'],
            'exe_path': window_info['exe_path']
        })


def log(e: Exception) -> None:
    # create file if not exist
    os.makedirs(os.path.dirname(ERROR_LOG_PATH), exist_ok=True)
    # save to log file
    with open(ERROR_LOG_PATH, 'a') as f:
        f.write(f'{datetime.now()}: {e}\n')

if __name__ == '__main__':
    while True:
        try:
            record_active_window()
        except Exception as e:
            log(e)
        time.sleep(1)