# Desktop_Screen_Time_Tracker
Simple python screen time tracker for windows desktop.

## Components:
### \# Utils:
Provides utilities functionalities for the recorder and webapp.
#### 1. DB: Creates database schema using SQLAlchemy, and provides necessary methods to interact with the database:
- create_db
- get_all_records
- add_record
- get_all_apps_names
- update_app_icon
- is_transformation_needed
- transform_new_data

#### 2. Summarizer: Reads the records file & does necessary transformation, includes following methods:
- seconds_to_time
- get_usage_by_apps
- get_denormalized_records
- get_unique_days
- get_daily_usage

#### 3. Icon Extractor: Uses PIL library to extract icons from the active window, if it is a new app, includes following methods:
- extract_icon
- ico_to_png
- png_to_svg


### \# Recorder
Uses win32gui library to record the active window every second

Includes following methods:
- get_active_window_info
- record_active_window
- log

### \# App:
Builds a simple Flask webapp that displays the screen time daily/monthly/yearly, and usage by apps for a selected day.

It consists of 2 blueprints:
- home.py: provides basic routes for the webapp
- charts.py: provides routes for displaying charts

Screenshots of the webapp:
<br>

<p align="center">
  <img src="./assets/dashboard1.png" alt="App Usage Dashboard" width="400"/>
  <img src="./assets/dashboard2.png" alt="Daily Usage Dashboard" width="400"/>
</p>
<br>

## To Do:
- ~~Set default value of App Usage Graph to today~~
- ~~Make tracking more efficient:~~
    - ~~Use db (sqlalchemy) instead of csv~~
    - ~~Save data in normalized form (saves alot of space instead of repeating apps names for e.g)~~
    - ~~Insert records as batches (keep 30s in-memory) to reduce I/O~~
    - ~~Summarize old days into hourly app usage data only (each 86,400 rows -> number of apps * 24)~~
- Improve Dashboard Design
- ~~Add export option to export data to csv or excel~~
- ~~Add app icons to dashboard~~
- ~~Migrate to Flask~~
- ~~Auto-Refresh Dashboard (auto-transform actually)~~
- Add setting page:
    - ~~Add dark theme~~
    - Add daily screen time goal (symbolic, doesn't block anything)
- ~~Wrap 6th+ apps as 'Others' so app usage graph contains max of 6 apps~~

These are just some ideas to be done soon, surely on the long-run many features could be added. Don't hesitate to share any suggestions!

<br>

## Usage
For the ready-to-use application, download the executable setup file from the latest release, [here](https://github.com/homanydata/Desktop_Screen_Time_Tracker/releases/tag/v0.1.0). Run it and follow the instructions within the installer.

To try the code yourself, you can do the following:

1. Clone the repo
    ```
    git clone https://github.com/yourusername/Desktop_Screen_Time_Tracker.git
    ```
2. Install the requirements
    ```
    pip install -r requirements.txt
    ```
3. Create executables

    Run the following commands in the command line (in the project directory)
    ```
    pyinstaller --onefile --noconsole --hidden-import=xml.parsers.expat recorder.py
    ```
    ```
    pyinstaller --onefile --hidden-import=xml.parsers.expat --add-data "assets;assets" main.py
    ```
    You will find the exectuables in the dist folder. Make sure to move the recorder.exe and app.exe to the root directory of the repository.

4. Create a shortcut for the recorder.exe

5. Run Recorder on Startup:

    Move the recorder shortcut to the `C:\Users\Admiin\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\`.
    
    Now the recorder will run on startup and log the screen time to the screentime.db file.

6. Run the main.exe to view the screen time.

<br><br>
## Get Involved!
If you're interested in contributing to or participating in this project, welcome! 😊

"Desktop_Screen_Time_Tracker" is a simple, fun, and casual project designed to help track your screen time on desktop, just a side project for learning and experimenting!