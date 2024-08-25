import dash
from dash import dcc, html
import pandas as pd
from summarizer import get_daily_usage
import plotly.express as px
from dash.dependencies import Input, Output

# Initialize the Dash app
app = dash.Dash(__name__)

# Load the data
df = get_daily_usage('active_apps_log.csv')
df['date'] = pd.to_datetime(df['date'])

# Function to aggregate data and format the date column
def aggregate_data(df, level):
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
    html.H1(children='Screen Time Tracker', style={'textAlign': 'center', 'color': '#A61436', 'font-family': 'Solway, sans-serif', 'font-weight': '700', 'font-size': '50px'}),

    html.Div(children='''\nA simple Dash app to track screen time usage at different levels.\n''',
    style={'textAlign': 'center', 'color': '#A61436', 'font-family': 'Solway, sans-serif', 'font-weight': '700', 'font-size': '20px'}
    ),

    dcc.RadioItems(
        id='aggregation-level',
        options=[
            {'label': 'Daily', 'value': 'Daily'},
            {'label': 'Monthly', 'value': 'Monthly'},
            {'label': 'Yearly', 'value': 'Yearly'}
        ],
        value='Daily',
        labelStyle={'display': 'inline-block'},
        style={'textAlign': 'right', 'color': '#00', 'font-family': 'Solway, sans-serif', 'font-weight': '400', 'font-size': '20px', 'margin-top': '100px', 'margin-right': '80px'}
    ),

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
    )
])

# Callback to update the graph based on the selected aggregation level
@app.callback(
    Output('Daily Usage Graph', 'figure'),
    [Input('aggregation-level', 'value')]
)
def update_graph(selected_level):
    aggregated_df = aggregate_data(df, selected_level)
    fig = px.bar(aggregated_df, x='formatted_date', y='usage', title=f'{selected_level} Screen Time Usage')
    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Usage')
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
