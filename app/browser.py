from flask import Blueprint, send_from_directory, request, jsonify, render_template, session
from utils.summarizer import get_unique_days, get_usage_by_websites, get_daily_browser_usage
from utils.charts import create_app_usage_figure, create_daily_usage_figure, aggregate_data


browser = Blueprint('browser', __name__)

# Route for the browser page
@browser.route('/browser', methods=['GET'])
def index():
    # Render the browser page with the empty graph initially
    return render_template('browser.html')


unique_days = get_unique_days()
# Route for updating the app usage graph
@browser.route('/browser/get-app-usage', methods=['GET'])
def update_app_usage_graph():
    # get the args
    selected_date = request.args.get('date')
    if not selected_date or selected_date == 'NaN':
        if unique_days:
            selected_date = unique_days[-1]
        else:
            return jsonify({'appUsageJSON': None, 'message': 'Recorded usage data is not enough yet.'})

    # Fetch the app usage data for the selected date
    website_usage_df = get_usage_by_websites(selected_date)

    # Handle empty df
    if website_usage_df.empty:
        # If empty, return a message to the frontend to indicate no data
        return jsonify({'appUsageJSON': None, 'message': 'No usage data available for this day.'})

    # Create graphs
    app_usage_json = create_app_usage_figure(session.get('settings').get('theme'), website_usage_df)

    return jsonify({'graphJSON': app_usage_json, 'selectedDate': selected_date})


# Route for updating the daily usage graph
@browser.route('/browser/get-daily-usage', methods=['GET'])
def update_daily_usage_graph():
    # get the args
    selected_level = request.args.get('level')
    if not selected_level or selected_level == 'NaN':
        selected_level = 'Daily'

    # Fetch the daily usage data and aggregate it based on the selected level
    df = get_daily_browser_usage()
    aggregated_df = aggregate_data(df, selected_level)
    
    if aggregated_df.empty:
        return jsonify({'graphJSON': None, 'message': 'No usage data available for this aggregation level.'})
    # Create the Plotly figure
    daily_usage_json = create_daily_usage_figure(session.get('settings').get('theme'), aggregated_df, selected_level)
    # Convert the figure to JSON and return it
    return jsonify({'graphJSON': daily_usage_json})