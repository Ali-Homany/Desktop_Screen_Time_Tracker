from flask import Blueprint, request, jsonify, render_template, session
from utils.summarizer import get_unique_days, get_usage_by_apps, get_daily_usage
from utils.charts import create_app_usage_figure, create_daily_usage_figure, create_total_usage_graph, aggregate_data


home = Blueprint('home', __name__)


# Route for the index page
@home.route('/', methods=['GET'])
def index():
    # Render the index page with the empty graph initially
    return render_template('index.html')


unique_days = get_unique_days()
# Route for updating the app usage graph
@home.route('/get-app-usage', methods=['GET'])
def update_app_usage_graph():
    # get the args
    selected_date = request.args.get('date')
    if not selected_date or selected_date == 'NaN':
        if unique_days:
            selected_date = unique_days[-1]
        else:
            return jsonify({'appUsageJSON': None, 'message': 'Recorded usage data is not enough yet.'})

    # Fetch the app usage data for the selected date
    app_usage_df = get_usage_by_apps(selected_date)

    # Handle empty df
    if app_usage_df.empty:
        # If empty, return a message to the frontend to indicate no data
        return jsonify({'appUsageJSON': None, 'message': 'No usage data available for this day.'})

    # Create graphs
    app_usage_json = create_app_usage_figure(session.get('settings').get('theme'), app_usage_df, icons_dir_url='Icons')
    total_hours = app_usage_df['usage'].sum() / 60
    total_hours_graph_json = create_total_usage_graph(theme=session.get('settings').get('theme'), total_hours=total_hours, daily_goal=session.get('settings').get('daily_goal'))

    return jsonify({'graphJSON': app_usage_json, 'dayHours': total_hours, 'dayHoursGraph': total_hours_graph_json, 'selectedDate': selected_date})


# Route for updating the daily usage graph
@home.route('/get-daily-usage', methods=['GET'])
def update_daily_usage_graph():
    # get the args
    selected_level = request.args.get('level')
    if not selected_level or selected_level == 'NaN':
        selected_level = 'Daily'

    # Fetch the daily usage data and aggregate it based on the selected level
    df = get_daily_usage()
    aggregated_df = aggregate_data(df, selected_level)
    
    if aggregated_df.empty:
        return jsonify({'graphJSON': None, 'message': 'No usage data available for this aggregation level.'})
    # Create the Plotly figure
    fig = create_daily_usage_figure(session.get('settings').get('theme'), aggregated_df, selected_level)
    # Convert the figure to JSON and return it
    daily_usage_json = create_daily_usage_figure(session.get('settings').get('theme'), aggregated_df, selected_level)
    return jsonify({'graphJSON': daily_usage_json})
