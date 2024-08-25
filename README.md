# Desktop_Screen_Time_Tracker
Simple python screen time tracker for windows desktop.

## Components:
### 1. Recorder
Uses win32gui library to record the active window every second

Includes 3 methods:
- get_active_window_title
- extract_app_name
- record_active_window

### 2. Summarizer
Reads the records file & does necessary transformation.

Includes 4 methods:
- group_by_app
- get_daily_usage
- usage_at_date
- seconds_to_time

### 3. App
Builds a simple Dash webapp that displays the screen time (for now) daily/monthly/yearly.
