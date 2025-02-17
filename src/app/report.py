import datetime
from flask import Blueprint, session, jsonify, render_template, request
from utils.charts import create_daily_usage_figure
from utils.summarizer import get_usage_todate, get_browser_usage_todate, filter_top


"""
This module provides a concise report for the last week/month usage.
It includes:
- Daily Usage Graph with avg annotation
- Top 3 apps used
- Top 3 websites used
- # times goal is achieved
"""

report = Blueprint('report', __name__)


@report.route('/report')
def report_page():
    return render_template('report.html')


@report.route('/get-report', methods=['GET'])
def get_report():
    # get report level
    selected_level = request.args.get('level').lower()
    if not selected_level or selected_level not in ['weekly', 'monthly']:
        selected_level = 'weekly'
    start_date = datetime.date.today() - datetime.timedelta(
        days=7 if selected_level == 'weekly' else 30
    )
    # load data
    data = get_usage_todate(start_date)
    data_by_app = data.groupby('app_name').sum().reset_index()
    data = data.groupby('date').sum().reset_index()
    top_apps = filter_top(
        df=data_by_app,
        n_top=3,
        add_other=False
    )['app_name'].tolist()
    top_websites = filter_top(
        df=get_browser_usage_todate(start_date).groupby('domain_name').sum().reset_index(),
        n_top=3,
        add_other=False
    )
    top_websites = top_websites['app_name'].tolist()
    # calculate # times goal is achieved
    goal = float(session.get('settings').get('daily_goal')) * 3600
    n_days_successful = data[data['usage'] >= goal].shape[0]
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
        nDaysSuccessful=n_days_successful
    )
