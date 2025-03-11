import datetime
from flask import Blueprint, session, jsonify, render_template, request
from db.db_init import create_session, engine
from utils.charts import create_daily_usage_figure
from utils.summarizer import (
    get_usage_todate,
    get_browser_usage_todate,
    filter_top
)


"""
This module provides a concise report for the last week/month usage.
It includes:
- Daily Usage Graph with avg annotation
- Top 3 apps used
- Top 3 websites used
- # times goal is achieved
"""


report = Blueprint('report', __name__)
db = create_session(engine)


@report.route('/report')
def report_page():
    return render_template('report.html')


@report.route('/get-report', methods=['GET'])
def get_report():
    # get report level
    level = request.args.get('level').lower()
    if not level or level not in ['weekly', 'monthly']:
        level = 'weekly'
    start_date = datetime.date.today() - datetime.timedelta(
        days=7 if level == 'weekly' else 30)
    # load data
    data = get_usage_todate(db, start_date)
    data_by_app = data.groupby('app_name').sum().reset_index()
    data = data.groupby('date').sum().reset_index()
    top_apps = filter_top(
        df=data_by_app,
        n_top=3,
        add_other=False
    )
    if top_apps.empty:
        message = f'No usage data available for this {level[:-2]}.'
        return jsonify({
            'graphJSON': None,
            'message': message})
    top_apps = top_apps['app_name'].tolist()
    websites_df = (
        get_browser_usage_todate(db, start_date)
        .groupby('domain_name')
        .sum()
        .reset_index()
    )
    top_websites = filter_top(
        df=websites_df,
        n_top=3,
        add_other=False
    )
    if top_websites.empty:
        message = f'No browser usage data available for this {level[:-2]}.'
        return jsonify({
            'graphJSON': None,
            'message': message
        })
    top_websites = top_websites['app_name'].tolist()
    # calculate # times goal is achieved
    goal = float(session.get('settings').get('daily_goal')) * 3600
    # create charts
    daily_chart = create_daily_usage_figure(
        theme=session.get('settings').get('theme'),
        aggregated_df=data,
        selected_level='Daily',
        show_average=True,
        goal=goal
    )
    # return response
    return jsonify(
        graphJSON=daily_chart,
        topApps=top_apps,
        topWebsites=top_websites,
    )
