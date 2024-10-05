import pandas as pd
import datetime
from utils.db import (
    App,
    HourlyRecords,
    create_db
)
from sqlalchemy import func


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


def get_usage_by_apps(date: datetime.date) -> pd.DataFrame:
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
    return app_counts

def get_denormalized_records() -> pd.DataFrame:
    session = create_db()
    query = session.query(HourlyRecords.datetime, App.app_name, HourlyRecords.duration).join(App)
    result = pd.read_sql(query.statement, session.bind)
    session.close()
    return result

def get_unique_days() -> list:
    session = create_db()
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


if __name__ == '__main__':
    df = get_daily_usage()
    print(df)
