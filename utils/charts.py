import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import pandas as pd
import json

from typing import Literal
THEME = Literal['light', 'dark']


def create_app_usage_figure(theme: THEME, app_usage_df: pd.DataFrame) -> str:
    # Create the bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=app_usage_df['usage'],
        y=app_usage_df['app_name'],
        orientation='h',
        marker_color='#6f54d3',
        width=0.4
    ))

    # dynamic icon size based on the num of rows
    num_bars = len(app_usage_df)
    icon_size = min((num_bars * 0.1), 0.6)

    # Add images (icons) as annotations
    for index, row in app_usage_df.iterrows():
        fig.add_layout_image(
            dict(
                source=f'/Icons/{row["app_name"]}.ico',
                xref="paper", yref="y",
                x=-0.1, y=row['app_name'],
                sizex=icon_size, sizey=icon_size,
                xanchor="right", yanchor="middle"
            )
        )
    # Customize layout
    fig.update_layout(
        xaxis_title='Usage (Minutes)',
        height=600,
        bargap=0.2,
        showlegend=False,
        margin=dict(l=200, t=20, b=20, r=20),
        modebar_remove=True,
        dragmode=False,
        template='plotly_dark' if theme == 'dark' else 'plotly_white',
        plot_bgcolor= "rgba(0, 0, 0, 0)",
        paper_bgcolor= "rgba(0, 0, 0, 0)",
    )
    fig_json = json.dumps(fig, cls=PlotlyJSONEncoder)
    return fig_json


def create_total_usage_graph(theme: THEME, total_hours: float, daily_goal: float=None) -> str | None:
    if not daily_goal:
        return None

    daily_goal = float(daily_goal)

    fig = go.Figure()
    if total_hours <= daily_goal:
        fig.add_trace(go.Bar(
            x=[total_hours],
            y=['Usage'],
            orientation='h',
            name='Used',
            marker_color='#6f54d3'
        ))
        fig.add_trace(go.Bar(
            x=[daily_goal - total_hours],
            y=['Usage'],
            orientation='h',
            name='Remaining',
            marker_color='#e5e5e5'
        ))
    else:
        fig.add_trace(go.Bar(
            x=[daily_goal],
            y=['Usage'],
            orientation='h',
            name='Goal',
            marker_color='#6f54d3'
        ))
        fig.add_trace(go.Bar(
            x=[total_hours - daily_goal],
            y=['Usage'],
            orientation='h',
            name='Overtime',
            marker_color='#A61436'
        ))

    fig.update_layout(
        title=f'Daily Usage: {total_hours:.2f} hrs / {daily_goal} hrs Goal',
        xaxis_title='Hours',
        barmode='stack',
        height=180,
        margin=dict(l=10, r=10, t=80, b=20),
        showlegend=False,
        xaxis=dict(range=[0, max(total_hours, daily_goal)]),
        template='plotly_dark' if theme == 'dark' else 'plotly_white',
        plot_bgcolor= "rgba(0, 0, 0, 0)",
        paper_bgcolor= "rgba(0, 0, 0, 0)",
    )

    fig_json = json.dumps(fig, cls=PlotlyJSONEncoder)
    return fig_json


def aggregate_data(df: pd.DataFrame, level: str) -> pd.DataFrame:
    """Aggregate data and format the date column based on the given aggregation level"""
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


def create_daily_usage_figure(theme: THEME, aggregated_df: pd.DataFrame, selected_level: str) -> str:
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
        dragmode=False,
        margin=dict(b=100),
        template='plotly_dark' if theme == 'dark' else 'plotly_white',
        plot_bgcolor= "rgba(0, 0, 0, 0)",
        paper_bgcolor= "rgba(0, 0, 0, 0)",
    )
    fig_json = json.dumps(fig, cls=PlotlyJSONEncoder)
    return fig_json
