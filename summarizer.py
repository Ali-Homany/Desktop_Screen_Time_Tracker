import pandas as pd
from datetime import datetime
import os

# CSV file directory in Documents
documents_dir = os.path.join(os.path.expanduser('~'), 'Documents', 'ScreenTimeTracker')
CSV_FILE_PATH = os.path.join(documents_dir, 'active_apps_log.csv')

def seconds_to_time(seconds: int) -> str:
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


def get_usage_by_apps(date: datetime) -> pd.DataFrame:
    """
    Get the usage counts for all apps at a given date
    Args:
        date (datetime): The date to get the usage counts for
    Returns:
        pd.DataFrame: A DataFrame with the app names and the usage counts in minutes
    """
    df = usage_at_date(date)
    app_counts = df['app_name'].value_counts()
    app_counts = app_counts.reset_index(name='usage')
    app_counts['usage'] = app_counts['usage'] // 60
    app_counts = app_counts[app_counts['usage'] > 0]
    return app_counts

def read_data() -> pd.DataFrame:
    if not os.path.exists(CSV_FILE_PATH):
        os.makedirs(os.path.dirname(CSV_FILE_PATH), exist_ok=True)
        pd.DataFrame(columns=['timestamp', 'title', 'app_name', 'exe_path']).to_csv(CSV_FILE_PATH, index=False)
    return pd.read_csv(CSV_FILE_PATH, encoding='utf-8')

def get_unique_days() -> pd.DataFrame:
    df = read_data()
    df['date'] = pd.to_datetime(df['timestamp'], unit='s').dt.date
    result = df['date'].unique()
    return result


def get_daily_usage() -> pd.DataFrame:
    df = read_data()
    df['date'] = pd.to_datetime(df['timestamp'], unit='s').dt.date
    result = df['date'].value_counts()
    result = result.reset_index(name='usage')
    result['date'] = pd.to_datetime(result['date'])
    return result


def usage_at_date(date: datetime) -> pd.DataFrame:
    df = read_data()
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    df.set_index('timestamp', inplace=True)
    return df.loc[date]


if __name__ == '__main__':
    df = get_daily_usage()
    print(df)
