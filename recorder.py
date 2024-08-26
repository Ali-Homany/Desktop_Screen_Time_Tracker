import win32gui
import win32process
import wmi
import time
import csv
import os
from datetime import datetime

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
    
    file_exists = os.path.exists('active_apps_log.csv')
    
    with open('active_apps_log.csv', 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['timestamp', 'title', 'app_name', 'exe_path']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            'timestamp': timestamp,
            'title': window_info['title'],
            'app_name': window_info['app_name'],
            'exe_path': window_info['exe_path']
        })


def log(e: Exception) -> None:
    # save to log file
    with open('error_log.txt', 'a') as f:
        f.write(f'{datetime.now()}: {e}\n')


if __name__ == '__main__':
    while True:
        try:
            record_active_window()
        except Exception as e:
            log(e)
        time.sleep(1)