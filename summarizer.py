import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt



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


def group_by_app(df: pd.DataFrame) -> pd.DataFrame:
    app_counts = df['app_name'].value_counts()
    return app_counts


def get_daily_usage(csv_file_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_file_path)
    df['date'] = pd.to_datetime(df['timestamp'], unit='s').dt.date
    result = df['date'].value_counts()
    result = result.reset_index(name='usage')
    return result


def usage_at_date(csv_file_path: str, date: datetime) -> pd.DataFrame:
    df = pd.read_csv(csv_file_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    df.set_index('timestamp', inplace=True)
    return df.loc[date]


if __name__ == '__main__':
    csv_file_path = 'active_apps_log.csv'
    df = get_daily_usage(csv_file_path)
    print(df)
