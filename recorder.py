import win32gui
import time
import csv


def get_active_window_title():
    hwnd = win32gui.GetForegroundWindow()
    title = win32gui.GetWindowText(hwnd)
    return title


def extract_app_name(title):
    # Remove the window title from the window text
    if '-' in title:
        app_name = title.split(' - ')[-1]
    elif '\\' in title:
        app_name = 'File Explorer'
    else:
        app_name = title
    return app_name


def record_active_window(interval=1):
    timestamp = time.time()
    title = get_active_window_title()
    app_name = extract_app_name(title)
    with open('active_apps_log.csv', 'a', newline='') as csvfile:
        fieldnames = ['timestamp', 'title', 'app_name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if csvfile.tell() == 0:
            writer.writeheader()
        writer.writerow({'timestamp': timestamp, 'title': title, 'app_name': app_name})

if __name__ == '__main__':
    while True:
        record_active_window()
        time.sleep(1)
