import requests
from flask import Blueprint, request, jsonify, render_template, session
from db.db_init import create_session
from utils.charts import (
    create_app_usage_figure,
    create_daily_usage_figure,
    aggregate_data
)
from utils.summarizer import (
    get_unique_days,
    get_usage_by_websites,
    get_daily_browser_usage
)


"""
This module contains routes and functions for the browser page,
which displays the browser time usage.
"""


browser = Blueprint('browser', __name__)
db = create_session()


# Route for the browser page
@browser.route('/browser', methods=['GET'])
def index():
    try:
        is_extension_active = requests.get(
            'http://localhost:8049/check_extension',
            timeout=.5
        ).json()['is_extension_active']
    except:
        is_extension_active = False
    # Render the browser page with the empty graph initially
    return render_template(
        'browser.html',
        is_extension_active=is_extension_active
    )


unique_days = get_unique_days(db, for_browser=True)
# Route for updating the app usage graph
@browser.route('/browser/get-app-usage', methods=['GET'])
def update_app_usage_graph():
    # get the args
    selected_date = request.args.get('date')
    if not selected_date or selected_date == 'NaN':
        if unique_days:
            selected_date = unique_days[-1]
        else:
            return jsonify({
                'appUsageJSON': None,
                'message': 'Recorded usage data is not enough yet.'
            })

    # Fetch the app usage data for the selected date
    website_usage_df = get_usage_by_websites(db, selected_date)

    # Handle empty df
    if website_usage_df.empty:
        # If empty, return a message to the frontend to indicate no data
        return jsonify({
            'appUsageJSON': None,
            'message': 'No usage data available for this day.'
        })
    # Create graphs
    app_usage_json = create_app_usage_figure(
        session.get('settings').get('theme'),
        website_usage_df,
        icons_dir_url='Websites_Icons'
    )
    total_hours = website_usage_df['usage'].sum() / 60
    return jsonify({
        'graphJSON': app_usage_json,
        'dayHours': total_hours,
        'selectedDate': selected_date
    })


# Route for updating the daily usage graph
@browser.route('/browser/get-daily-usage', methods=['GET'])
def update_daily_usage_graph():
    # get the args
    selected_level = request.args.get('level')
    if not selected_level or selected_level == 'NaN':
        selected_level = 'Daily'

    # Fetch the daily usage data and aggregate it based on the selected level
    df = get_daily_browser_usage(db)
    aggregated_df = aggregate_data(df, selected_level)
    
    if aggregated_df.empty:
        return jsonify({
            'graphJSON': None,
            'message': 'No usage data available for this aggregation level.'
        })
    # Create the Plotly figure
    daily_usage_json = create_daily_usage_figure(
        session.get('settings').get('theme'),
        aggregated_df,
        selected_level
    )
    # Convert the figure to JSON and return it
    return jsonify({'graphJSON': daily_usage_json})
