from pandas import DataFrame
from db.db_init import (
    App,
    Website,
    Record,
    HourlyRecords,
    BrowserRecord,
    Session
)


"""
This module provides necessary methods to interact with the database
"""


def get_all_records(db: Session) -> DataFrame:
    records = db.query(HourlyRecords).all()
    df = DataFrame([record.__dict__ for record in records])
    df.rename({'duration': 'usage'})
    return df


def get_all_apps_names(db: Session) -> list[str]:
    apps = db.query(App).all()
    return [app.app_name for app in apps]


def get_all_websites_names(db: Session) -> list[str]:
    websites = db.query(Website).all()
    return [website.domain_name for website in websites]


def get_last_browser_tab(db: Session) -> str:
    record = (
        db.query(BrowserRecord)
        .join(Website, Website.id == BrowserRecord.website_id)
        .order_by(BrowserRecord.timestamp.desc())
        .first()
    )
    last_browser_tab = record.website.domain_name if record else None
    return last_browser_tab


def add_record(
    db: Session,
    app_name: str,
    app_path: str,
    timestamp: int
) -> None:
    # Create a database db
    # Check if the app is already in the database
    app = db.query(App).filter_by(app_name=app_name).first()
    if not app:
        # If not, create a new app entry
        app = App(app_name=app_name, file_location=app_path)
        db.add(app)
    # Create a new record entry
    record = Record(timestamp=timestamp, app=app)
    db.add(record)
    db.commit()


def add_browser_record(db: Session, domain_name: str, timestamp: int) -> None:
    # Create a database db
    # Check if the app is already in the database
    website = db.query(Website).filter_by(domain_name=domain_name).first()
    if not website:
        # If not, create a new app entry
        website = Website(domain_name=domain_name)
        db.add(website)
    # Create a new browser_record entry
    browser_record = BrowserRecord(timestamp=timestamp, website=website)
    db.add(browser_record)
    db.commit()


def add_app(db: Session, app_name: str, file_location: str='') -> None:
    app = db.query(App).filter_by(app_name=app_name).first()
    if not app:
        app = App(app_name=app_name, file_location=file_location or 'Unknown')
        db.add(app)
    db.commit()


def add_website(db: Session, website_name: str) -> None:
    website = db.query(Website).filter_by(domain_name=website_name).first()
    if not website:
        website = Website(domain_name=website_name)
        db.add(website)
    db.commit()
