import os
import dash
from dash import dcc, html
import pandas as pd
from summarizer import get_daily_usage, get_unique_days, get_usage_by_apps
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output

# Initialize the Dash app
base_dir = os.path.dirname(os.path.realpath(__file__))
assets_path = os.path.join(base_dir, 'assets')
app = dash.Dash(__name__, assets_folder=assets_path)


# Function to aggregate data and format the date column
def aggregate_data(df: pd.DataFrame, level: str) -> pd.DataFrame:
    if level == 'Daily':
        df['formatted_date'] = df['date'].dt.strftime('%Y-%m-%d')
    elif level == 'Monthly':
        df = df.resample('ME', on='date').sum().reset_index()
        df['formatted_date'] = df['date'].dt.strftime('%Y-%m')
    elif level == 'Yearly':
        df = df.resample('YE', on='date').sum().reset_index()
        df['formatted_date'] = df['date'].dt.strftime('%Y')
    return df


# Define the layout of the app
app.layout = html.Div(children=[
    html.H1(children='Screen Time Tracker'),
    # Dropdown for selecting a specific day
    html.H2('Select a Day to View App Usage'),
    dcc.Dropdown(
        id='day-selection',
        options=[{'label': day, 'value': day} for day in get_unique_days()],
        placeholder='Select a day',
    ),
    # Total Hours in selected date
    html.Div(id='total-hours-display', style={'marginTop': '20px', 'fontSize': '20px'}),
    # Graph to display app usage for selected day
    dcc.Graph(
        id='App Usage Graph',
        config={
            'scrollZoom': True,
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': [
                'pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d',
                'autoScale2d', 'resetScale2d', 'hoverClosestCartesian',
                'hoverCompareCartesian', 'toggleSpikelines'
            ],
            'modeBarButtonsToAdd': ['toImage']
        }
    ),

    html.H2(children='''Daily screen time usage at different levels.'''),

    # Aggregation level selection
    dcc.RadioItems(
        id='aggregation-level',
        options=[
            {'label': 'Daily', 'value': 'Daily'},
            {'label': 'Monthly', 'value': 'Monthly'},
            {'label': 'Yearly', 'value': 'Yearly'}
        ],
        value='Daily',
        labelStyle={'display': 'inline-block'}
    ),
    # Main usage graph
    dcc.Graph(
        id='Daily Usage Graph',
        config={
            'scrollZoom': True,
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': [
                'pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d',
                'autoScale2d', 'resetScale2d', 'hoverClosestCartesian',
                'hoverCompareCartesian', 'toggleSpikelines'
            ],
            'modeBarButtonsToAdd': ['toImage']
        }
    ),
])


# Callback to update the main usage graph based on the selected aggregation level
@app.callback(
    Output('Daily Usage Graph', 'figure'),
    [Input('aggregation-level', 'value')]
)
def update_graph(selected_level):
    df = get_daily_usage()
    aggregated_df = aggregate_data(df, selected_level)
    fig = px.bar(aggregated_df, x='formatted_date', y='usage', title=f'{selected_level} Screen Time Usage')
    fig = go.Figure(data=[
        go.Bar(
            x=aggregated_df['formatted_date'],
            y=aggregated_df['usage']//3600,
        )
    ])
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Usage (in hrs)',
        bargap=0.3,
        height=500
    )
    return fig

# Callback to update the app usage graph based on the selected day
@app.callback(
    Output('App Usage Graph', 'figure'),
    [Input('day-selection', 'value')]
)
def update_app_usage(selected_day):
    if selected_day is None:
        return {}  # Return an empty figure if no day is selected

    app_usage_df = get_usage_by_apps(selected_day)
    app_usage_df = app_usage_df.sort_values(by='usage', ascending=True)  # Sort by usage in descending order
    fig = px.bar(app_usage_df, y='app_name', x='usage', orientation='h', title=f'App Usage on {selected_day}')
    fig.update_layout(
        xaxis_title='Screen Time (Minutes)',
        yaxis_title='App',
        bargap=0.2,
    )
    return fig
# Callback to update the total hours display based on the selected day
@app.callback(
    Output('total-hours-display', 'children'),
    [Input('day-selection', 'value')]
)
def update_total_hours(selected_day):
    if selected_day is None:
        return "Total Hours: N/A"

    # Retrieve app usage for the selected day and calculate total usage in hours
    app_usage_df = get_usage_by_apps(selected_day)
    total_minutes = app_usage_df['usage'].sum()  # Assuming 'usage' is in minutes
    total_hours = total_minutes / 60.0
    return f"Total Hours: {total_hours:.2f}"


if __name__ == '__main__':
    import webbrowser
    webbrowser.open('http://127.0.0.1:8050/')
    app.run()
