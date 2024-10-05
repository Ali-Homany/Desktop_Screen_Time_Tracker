from flask import Blueprint, send_from_directory, request, jsonify
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
from utils.summarizer import get_daily_usage, get_unique_days, get_usage_by_apps
import json
import os
import pandas as pd

"""
This blueprint is responsible for routes related to charts interactivity.
Currently it provides 2 routes:
- update-app-usage
- update-daily-usage
and an extra route for icons
"""

charts = Blueprint('charts', __name__)
unique_days = get_unique_days()

# Serve files from the 'Icons' folder
icons_dir = os.path.join(os.path.expanduser('~'), 'Documents', 'Screen_Time_Tracker', 'Icons')
os.makedirs(icons_dir, exist_ok=True)
@charts.route('/Icons/<path:filename>')
def serve_icon(filename):
    return send_from_directory(icons_dir, filename)


def create_app_usage_figure(app_usage_df: pd.DataFrame) -> go.Figure:
    # Create the bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=app_usage_df['usage'],
        y=app_usage_df['app_name'],
        orientation='h',
        marker_color='#636efa',
    ))
    # Add images (icons) as annotations
    for index, row in app_usage_df.iterrows():
        fig.add_layout_image(
            dict(
                source=f'/Icons/{row["app_name"]}.ico',
                xref="paper", yref="y",
                x=-0.1, y=row['app_name'],
                sizex=0.5, sizey=0.5,
                xanchor="right", yanchor="middle"
            )
        )
    # Customize layout
    fig.update_layout(
        xaxis_title='Usage (Minutes)',
        height=600,
        bargap=0.2,
        showlegend=False,
        margin=dict(l=200),
        modebar_remove=True,
        dragmode=False
    )
    return fig

# Route for updating the app usage graph
@charts.route('/update-app-usage', methods=['GET'])
def update_app_usage_graph():
    # get the args
    selected_date = request.args.get('date')
    if not selected_date or selected_date == 'NaN':
        selected_date = unique_days[-1]

    # Fetch the app usage data for the selected date
    app_usage_df = get_usage_by_apps(selected_date)

    # Handle empty df
    if app_usage_df.empty:
        # If empty, return a message to the frontend to indicate no data
        return jsonify({'appUsageJSON': None, 'message': 'No usage data available for this day.'})
    
    # Create the Plotly figure
    fig = create_app_usage_figure(app_usage_df)
    # Convert the Plotly figure to JSON
    app_usage_json = json.dumps(fig, cls=PlotlyJSONEncoder)
    total_hours = app_usage_df['usage'].sum() / 60
    return jsonify({'graphJSON': app_usage_json, 'dayHoursDisplay': total_hours, 'selectedDate': selected_date})


# Function to aggregate data and format the date column
def aggregate_data(df: pd.DataFrame, level: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=['formatted_date', 'usage'])
    if level == 'Daily':
        df['formatted_date'] = df['date'].dt.strftime('%Y-%m-%d')
    elif level == 'Monthly':
        df = df.resample('ME', on='date').sum().reset_index()
        df['formatted_date'] = df['date'].dt.strftime('%Y-%m')
    elif level == 'Yearly':
        df = df.resample('YE', on='date').sum().reset_index()
        df['formatted_date'] = df['date'].dt.strftime('%Y')
    else:
        print('Incorrect level given')
        return pd.DataFrame(columns=['formatted_date', 'usage'])
    return df

def create_daily_usage_figure(aggregated_df: pd.DataFrame, selected_level: str) -> go.Figure:
    # Create a bar chart for the daily usage
    fig = go.Figure(data=[
        go.Bar(
            x=aggregated_df['formatted_date'],
            y=aggregated_df['usage'] // 3600,
        )
    ])
    fig.update_layout(
        title=f'{selected_level} Screen Time Usage',
        xaxis_title='Date',
        yaxis_title='Usage (in hrs)',
        bargap=0.3,
        height=500,
        modebar_remove=True,
        dragmode=False
    )
    return fig

# Route for updating the daily usage graph
@charts.route('/update-daily-usage', methods=['GET'])
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
    fig = create_daily_usage_figure(aggregated_df, selected_level)
    # Convert the figure to JSON and return it
    daily_usage_json = json.dumps(fig, cls=PlotlyJSONEncoder)
    return jsonify({'graphJSON': daily_usage_json})
