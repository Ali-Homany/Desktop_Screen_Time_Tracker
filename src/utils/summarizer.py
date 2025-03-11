import pandas as pd
import datetime
from sqlalchemy import func
from db.db_init import (
    App,
    Website,
    HourlyRecords,
    HourlyBrowserRecords,
    Session
)


"""
This module provides functions to transform and summarize data from the
database using pandas and sqlalchemy.
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


def get_usage_by_apps(
    db: Session,
    date: datetime.date,
    n_top: int=5
) -> pd.DataFrame:
    """
    Get the usage counts for all apps at a given date
    Args:
        date (date): The date to get the usage counts for
    Returns:
        pd.DataFrame: A DataFrame with the app names & usage counts in minutes
    """
    query = (
        db.query(
            App.app_name,
            func.sum(HourlyRecords.duration).label('total_duration')
        )
        .join(HourlyRecords)
        .filter(func.date(HourlyRecords.datetime) == date)
        .group_by(App.app_name)
        # filter out apps used less than 1 minute
        .having(func.sum(HourlyRecords.duration) >= 60)
        .order_by(func.sum(HourlyRecords.duration).desc())
    )
    results = query.all()
    app_counts = pd.DataFrame(results, columns=['app_name', 'usage'])
    app_counts['usage'] = app_counts['usage'] / 60  # timestamp is in seconds
    # filter top apps
    result = filter_top(app_counts, n_top, allow_less_than_n=True)
    return result


def get_denormalized_records(db: Session) -> pd.DataFrame:
    query = db.query(
        HourlyRecords.datetime,
        App.app_name,
        HourlyRecords.duration
    ).join(App)
    result = pd.read_sql(query.statement, db.bind)
    return result


def get_unique_days(db: Session, for_browser: bool=False) -> list:
    if for_browser:
        query = (
            db.query(func.distinct(func.date(HourlyBrowserRecords.datetime)))
            .order_by(func.date(HourlyBrowserRecords.datetime).asc())
        )
    else:
        query = (
            db.query(func.distinct(func.date(HourlyRecords.datetime)))
            .order_by(func.date(HourlyRecords.datetime).asc())
        )
    result = [date[0] for date in query.all()]
    return result


def get_daily_usage(db: Session) -> pd.DataFrame:
    query = (
        db.query(
            func.date(HourlyRecords.datetime).label('date'),
            func.sum(HourlyRecords.duration).label('usage')
        )
        .group_by(func.date(HourlyRecords.datetime))
        .order_by(func.date(HourlyRecords.datetime))
    )
    result = pd.read_sql(query.statement, db.bind)   
    if result.empty:
        return pd.DataFrame(columns=['date', 'usage'])   
    # Convert 'date' to datetime and 'usage' to minutes
    result['date'] = pd.to_datetime(result['date'])
    return result


def filter_top(
    df: pd.DataFrame,
    n_top: int,
    add_other: bool=True,
    allow_less_than_n: bool=False
) -> pd.DataFrame:
    if 'domain_name' in df.columns:
        df = df.rename(columns={'domain_name': 'app_name'})
    if len(df) <= n_top:
        if allow_less_than_n:
            return df
        return pd.DataFrame(columns=['app_name', 'usage'])
    # assuming df has app_name and usage columns
    df.sort_values(by='usage', ascending=False, inplace=True)
    top_websites = df.head(n_top).reset_index(drop=True)
    # add others row
    if add_other:
        other_apps = pd.DataFrame({
            'app_name': ['Other'],
            'usage': [df['usage'].sum() - top_websites['usage'].sum()]
        })
        top_websites = pd.concat([top_websites, other_apps], ignore_index=True)
    return top_websites


def get_usage_by_websites(
    db: Session,
    date: datetime.date,
    n_top: int=5
) -> pd.DataFrame:
    """
    Get the usage counts for all websites at a given date
    Args:
        date (date): The date to get the usage counts for
    Returns:
        pd.DataFrame: A DataFrame with website names and usage counts in mins
    """
    query = (
        db.query(
            Website.domain_name,
            func.sum(HourlyBrowserRecords.duration).label('total_duration')
        )
        .join(HourlyBrowserRecords)
        .filter(func.date(HourlyBrowserRecords.datetime) == date)
        .group_by(Website.domain_name)
        # filter out websites used less than 1 minute
        .having(func.sum(HourlyBrowserRecords.duration) >= 60)
        .order_by(func.sum(HourlyBrowserRecords.duration).desc())
    )
    results = query.all()
    website_counts = pd.DataFrame(results, columns=['app_name', 'usage'])
    # timestamp is in seconds
    website_counts['usage'] = website_counts['usage'] / 60
    # filter top websites
    result = filter_top(website_counts, n_top, allow_less_than_n=True)
    return result


def get_daily_browser_usage(db: Session) -> pd.DataFrame:
    query = (
        db.query(
            func.date(HourlyBrowserRecords.datetime).label('date'),
            func.sum(HourlyBrowserRecords.duration).label('usage')
        )
        .group_by(func.date(HourlyBrowserRecords.datetime))
        .order_by(func.date(HourlyBrowserRecords.datetime))
    )
    result = pd.read_sql(query.statement, db.bind)   
    if result.empty:
        return pd.DataFrame(columns=['date', 'usage'])   
    # Convert 'date' to datetime and 'usage' to minutes
    result['date'] = pd.to_datetime(result['date'])
    return result


def get_usage_todate(
    db: Session,
    start_date: datetime.date=None
) -> pd.DataFrame:
    if start_date is None:
        start_date = datetime.date.min
    query = (
        db.query(
            func.date(HourlyRecords.datetime).label('date'),
            App.app_name,
            func.sum(HourlyRecords.duration).label('usage')
        )
        .join(App)
        .filter(func.date(HourlyRecords.datetime) >= start_date)
        .group_by(
            func.date(HourlyRecords.datetime),
            App.app_name
        )
        .order_by(func.date(HourlyRecords.datetime))
    )
    result = pd.read_sql(query.statement, db.bind)
    return result


def get_browser_usage_todate(
    db: Session,
    start_date: datetime.date=None
) -> pd.DataFrame:
    if start_date is None:
        start_date = datetime.date.min
    query = (
        db.query(
            func.date(HourlyBrowserRecords.datetime).label('date'),
            Website.domain_name,
            func.sum(HourlyBrowserRecords.duration).label('usage')
        ).join(Website)
        .filter(func.date(HourlyBrowserRecords.datetime) >= start_date)
        .group_by(
            func.date(HourlyBrowserRecords.datetime),
            Website.domain_name
        )
        .order_by(func.date(HourlyBrowserRecords.datetime))
    )
    result = pd.read_sql(query.statement, db.bind)
    return result
