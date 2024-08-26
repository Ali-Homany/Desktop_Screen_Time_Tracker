# Desktop_Screen_Time_Tracker
Simple python screen time tracker for windows desktop.

## Components:
### 1. Recorder
Uses win32gui library to record the active window every second

Includes 3 methods:
- get_active_window_info
- record_active_window
- log

### 2. Summarizer
Reads the records file & does necessary transformation.

Includes 4 methods:
- group_by_app
- get_daily_usage
- usage_at_date
- seconds_to_time

### 3. App
Builds a simple Dash webapp that displays the screen time (for now) daily/monthly/yearly.

# Usage
1. Clone the repo
```
git clone https://github.com/yourusername/Desktop_Screen_Time_Tracker.git
```
2. Install the requirements
```
pip install -r requirements.txt
```
3. Create executables
```
pyinstaller --onefile --noconsole recorder.py
```
```
pyinstaller --onefile app.py
```
You will find the exectuables in the dist folder. Make sure to move the recorder.exe and app.exe to the root directory of the repository.

4. Create a shortcut for the recorder.exe

5. Move the shortcut to the `C:\Users\Admiin\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\`. Now the recorder will run on startup and log the screen time to the active_apps_log.csv file.

6. Run the app.exe to view the screen time.
You can view the screen time by going to http://127.0.0.1:8050/ on your browser.
