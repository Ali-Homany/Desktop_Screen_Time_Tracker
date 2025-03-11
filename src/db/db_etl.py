from datetime import datetime
from db.db_init import (
    App,
    Record,
    HourlyRecords,
    HourlyBrowserRecords,
    BrowserRecord,
    Session
)


"""
This module is responsible for data transformation, specifically transforming
existing records from Records table into HourlyRecords table
"""


def is_transformation_needed(db: Session) -> int:
    """
    Checks if transformation is needed or not
    """
    count = db.query(Record).count()
    db.close()
    # Check if there are more than max records
    # 600 records (10 minutes)
    MAX_RECORDS = 600
    return max(0, MAX_RECORDS - count)


def transform_new_data(db: Session) -> None:
    """
    Transform & migrate the existing data from BrowserRecords & Records tables
    into HourlyBrowserRecords & HourlyRecords tables respectively
    """
    # Get all records from Records table where app is a browser
    records_in_browser = (
        db.query(Record)
        .join(App, Record.app_id == App.id)
        .filter(App.app_name == 'Chrome')
        .subquery()
    )
    # Get all records from BrowserRecords table joined with Records table
    browser_records = (
        db.query(BrowserRecord)
        .join(
            records_in_browser,
            BrowserRecord.timestamp == records_in_browser.c.timestamp
        )
        .all()
    )
    # group all records from BrowserRecords table based on primary key
    hourly_browser_records_dict = {}
    for record in browser_records:
        website_id = record.website_id
        timestamp = record.timestamp
        hour = datetime.fromtimestamp(timestamp)
        hour = hour.replace(minute=0, second=0, microsecond=0)
        if (hour, website_id) not in hourly_browser_records_dict:
            hourly_browser_records_dict[(hour, website_id)] = 0
        # timestamp are in seconds
        hourly_browser_records_dict[(hour, website_id)] += 1
    # load into HourlyBrowserRecords (as upsert query)
    for (hour, website_id), duration in hourly_browser_records_dict.items():
        existing_hourly_browser_record = (
            db.query(HourlyBrowserRecords)
            .filter_by(datetime=hour, website_id=website_id)
            .first()
        )
        if existing_hourly_browser_record:
            existing_hourly_browser_record.duration += duration
        else:
            new_hourly_browser_record = HourlyBrowserRecords(
                datetime=hour,
                website_id=website_id,
                duration=duration
            )
            db.add(new_hourly_browser_record)
    # truncate BrowserRecords
    db.query(BrowserRecord).delete()

    # Get all records from Records table
    records = db.query(Record).all()
    # group all records from Records table based on primary key
    hourly_records_dict = {}
    for record in records:
        app_id = record.app_id
        timestamp = record.timestamp
        hour = datetime.fromtimestamp(timestamp)
        hour = hour.replace(minute=0, second=0, microsecond=0)
        if (hour, app_id) not in hourly_records_dict:
            hourly_records_dict[(hour, app_id)] = 0
        hourly_records_dict[(hour, app_id)] += 1  # timestamp are in seconds
    # load into HourlyRecords (as upsert query)
    for (hour, app_id), duration in hourly_records_dict.items():
        existing_hourly_record = (
            db.query(HourlyRecords)
            .filter_by(datetime=hour, app_id=app_id)
            .first()
        )
        if existing_hourly_record:
            existing_hourly_record.duration += duration
        else:
            new_hourly_record = HourlyRecords(
                datetime=hour,
                app_id=app_id,
                duration=duration
            )
            db.add(new_hourly_record)
    # truncate Records
    db.query(Record).delete()
    # commit
    db.commit()
