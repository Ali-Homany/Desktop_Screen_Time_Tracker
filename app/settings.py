from flask import Blueprint, render_template, make_response, session, url_for, redirect, request
from utils.summarizer import get_denormalized_records
import os
import json


settings = Blueprint('settings', __name__)

# Route for the settings page
@settings.route('/settings', methods=['GET'])
def index():
    # Render the settings page with the empty graph initially
    return render_template('settings.html')

def update_settings():
    settings_path = os.path.join(os.path.expanduser('~'), 'Documents', 'Screen_Time_Tracker', 'settings.json')
    with open(settings_path, 'w') as f:
        json.dump(session['settings'], f)

@settings.route('/export-data', methods=['GET'])
def export_data():
    df = get_denormalized_records()
    df = df.rename(columns={'duration': 'duration (in seconds)', 'datetime': 'datetime (every hour)'})
    # Create a CSV file from the data
    csv_data = df.to_csv(index=False)

    # Create a response with the CSV file
    response = make_response(csv_data)
    response.headers['Content-Disposition'] = 'attachment; filename="screentime_data.csv"'
    response.headers['Content-Type'] = 'text/csv'

    return response

@settings.route('/change-theme')
def change_theme():
    if session['settings']['theme'] == 'light':
        session['settings']['theme'] = 'dark'
    else:
        session['settings']['theme'] = 'light'
    update_settings()
    return redirect(url_for('settings.index'))

@settings.route('/set-goal', methods=['POST'])
def set_goal():
    goal = request.form['goal']
    session['settings']['daily_goal'] = goal
    update_settings()
    return redirect(url_for('settings.index'))
