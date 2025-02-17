import pandas as pd
import datetime
from utils.db import (
    create_db,
    App,
    Website,
    HourlyRecords,
    HourlyBrowserRecords,
)
from sqlalchemy import func


"""
This module provides functions to transform and summarize data from the database using pandas and sqlalchemy.
"""


def seconds_to_time(seconds: int) -> str:
    """
    Convert seconds to hours, minutes, and seconds
    Args:
        seconds (int): The number of seconds
    Returns:
        str: The formatted time string
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    if hours == 0:
        return f'{minutes}mins {seconds}secs'
    if minutes == 0:
        return f'{hours}hrs {seconds}secs'
    if seconds == 0:
        return f'{hours}hrs {minutes}mins'
    if hours == 0 and minutes == 0:
        return f'{seconds}secs'
    if hours == 0 and seconds == 0:
        return f'{minutes}mins'
    if minutes == 0 and seconds == 0:
        return f'{hours}hrs'
    return f'{hours}hrs {minutes}mins {seconds}secs'


def get_usage_by_apps(date: datetime.date, n_top: int=5) -> pd.DataFrame:
    """
    Get the usage counts for all apps at a given date
    Args:
        date (date): The date to get the usage counts for
    Returns:
        pd.DataFrame: A DataFrame with the app names and the usage counts in minutes
    """
    session = create_db()
    query = (
        session.query(
            App.app_name,
            func.sum(HourlyRecords.duration).label('total_duration')
        )
        .join(HourlyRecords)
        .filter(func.date(HourlyRecords.datetime) == date)
        .group_by(App.app_name)
        .having(func.sum(HourlyRecords.duration) >= 60) # filter out apps used less than 1 minute
        .order_by(func.sum(HourlyRecords.duration).asc())
    )
    results = query.all()
    session.close()
    app_counts = pd.DataFrame(results, columns=['app_name', 'usage'])
    app_counts['usage'] = app_counts['usage'] / 60  # timestamp is in seconds
    # filter top apps
    return filter_top(app_counts, n_top)


def get_denormalized_records() -> pd.DataFrame:
    session = create_db()
    query = session.query(HourlyRecords.datetime, App.app_name, HourlyRecords.duration).join(App)
    result = pd.read_sql(query.statement, session.bind)
    session.close()
    return result


def get_unique_days(for_browser: bool=False) -> list:
    session = create_db()
    if for_browser:
        query = session.query(func.distinct(func.date(HourlyBrowserRecords.datetime))).order_by(func.date(HourlyBrowserRecords.datetime).asc())
    else:
        query = session.query(func.distinct(func.date(HourlyRecords.datetime))).order_by(func.date(HourlyRecords.datetime).asc())
    result = [date[0] for date in query.all()]
    session.close()
    return result


def get_daily_usage() -> pd.DataFrame:
    session = create_db()
    query = session.query(
        func.date(HourlyRecords.datetime).label('date'),
        func.sum(HourlyRecords.duration).label('usage')
    ).group_by(func.date(HourlyRecords.datetime)).order_by(func.date(HourlyRecords.datetime))
    
    result = pd.read_sql(query.statement, session.bind)   
    if result.empty:
        return pd.DataFrame(columns=['date', 'usage'])   
    # Convert 'date' to datetime and 'usage' to minutes
    result['date'] = pd.to_datetime(result['date'])
    session.close()
    return result


def filter_top(df: pd.DataFrame, n_top: int, add_other: bool=True) -> pd.DataFrame:
    if len(df) <= n_top:
        return df
    if 'domain_name' in df.columns:
        df = df.rename(columns={'domain_name': 'app_name'})
    # assuming df has app_name and usage columns
    df.sort_values(by='usage', ascending=False, inplace=True)
    top_websites = df.head(n_top).reset_index(drop=True)
    # add others row
    if add_other:
        other_apps = pd.DataFrame({
            'app_name': ['Other'],
            'usage': [df['usage'].sum() - top_websites['usage'].sum()]
        })
        top_websites = pd.concat([other_apps, top_websites], ignore_index=True)
    return top_websites


def get_usage_by_websites(date: datetime.date, n_top: int=5) -> pd.DataFrame:
    """
    Get the usage counts for all websites at a given date
    Args:
        date (date): The date to get the usage counts for
    Returns:
        pd.DataFrame: A DataFrame with the website names and the usage counts in minutes
    """
    session = create_db()
    query = (
        session.query(
            Website.domain_name,
            func.sum(HourlyBrowserRecords.duration).label('total_duration')
        )
        .join(HourlyBrowserRecords)
        .filter(func.date(HourlyBrowserRecords.datetime) == date)
        .group_by(Website.domain_name)
        .having(func.sum(HourlyBrowserRecords.duration) >= 60) # filter out apps used less than 1 minute
        .order_by(func.sum(HourlyBrowserRecords.duration).asc())
    )
    results = query.all()
    session.close()
    website_counts = pd.DataFrame(results, columns=['app_name', 'usage'])
    website_counts['usage'] = website_counts['usage'] / 60  # timestamp is in seconds
    # filter top websites
    return filter_top(website_counts, n_top)


def get_daily_browser_usage() -> pd.DataFrame:
    session = create_db()
    query = session.query(
        func.date(HourlyBrowserRecords.datetime).label('date'),
        func.sum(HourlyBrowserRecords.duration).label('usage')
    ).group_by(func.date(HourlyBrowserRecords.datetime)).order_by(func.date(HourlyBrowserRecords.datetime))
    
    result = pd.read_sql(query.statement, session.bind)   
    if result.empty:
        return pd.DataFrame(columns=['date', 'usage'])   
    # Convert 'date' to datetime and 'usage' to minutes
    result['date'] = pd.to_datetime(result['date'])
    session.close()
    return result


def get_usage_todate(start_date: datetime.date=None) -> pd.DataFrame:
    session = create_db()
    if start_date is None:
        start_date = datetime.date.min
    query = session.query(
        func.date(HourlyRecords.datetime).label('date'),
        App.app_name,
        func.sum(HourlyRecords.duration).label('usage')
    ).join(
        App
    ).filter(
        func.date(HourlyRecords.datetime) >= start_date
    ).group_by(
        func.date(HourlyRecords.datetime),
        App.app_name
    ).order_by(func.date(HourlyRecords.datetime))
    result = pd.read_sql(query.statement, session.bind)
    return result


def get_browser_usage_todate(start_date: datetime.date=None) -> pd.DataFrame:
    session = create_db()
    if start_date is None:
        start_date = datetime.date.min
    query = session.query(
        func.date(HourlyBrowserRecords.datetime).label('date'),
        Website.domain_name,
        func.sum(HourlyBrowserRecords.duration).label('usage')
    ).join(
        Website
    ).filter(
        func.date(HourlyBrowserRecords.datetime) >= start_date
    ).group_by(
        func.date(HourlyBrowserRecords.datetime),
        Website.domain_name
    ).order_by(func.date(HourlyBrowserRecords.datetime))
    result = pd.read_sql(query.statement, session.bind)
    return result


if __name__ == '__main__':
    df = get_daily_usage()
    print(df)
