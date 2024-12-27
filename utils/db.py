import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, PrimaryKeyConstraint, text
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.ext.declarative import declarative_base
from pandas import DataFrame
from datetime import datetime

# DB file directory in Documents
documents_dir = os.path.join(os.path.expanduser('~'), 'Documents', 'Screen_Time_Tracker')
os.makedirs(documents_dir, exist_ok=True)
DB_PATH = f'sqlite:///{documents_dir}/screentime.db'

Base = declarative_base()
class PrintableBase(Base):
    __abstract__ = True
    def __str__(self):
        return f"{self.__class__.__name__}({', '.join(f'{k}={v}' for k, v in self.__dict__.items() if not k.startswith('_'))})"

class App(PrintableBase):
    __tablename__ = 'Apps'
    id = Column(Integer, primary_key=True)
    app_name = Column(String, unique=True)
    file_location = Column(String, nullable=False)

class Website(PrintableBase):
    __tablename__ = 'Websites'
    id = Column(Integer, primary_key=True)
    domain_name = Column(String, unique=True)

class Record(PrintableBase):
    __tablename__ = 'Records'
    id = Column(Integer, primary_key=True)
    timestamp = Column(Integer, nullable=False)
    app_id = Column(Integer, ForeignKey('Apps.id'), nullable=False)
    app = relationship("App")

class BrowserRecord(PrintableBase):
    __tablename__ = 'BrowserRecords'
    id = Column(Integer, primary_key=True)
    timestamp = Column(Integer, nullable=False)
    website_id = Column(Integer, ForeignKey('Websites.id'), nullable=False)
    website = relationship("Website")

class HourlyRecords(PrintableBase):
    __tablename__ = 'HourlyRecords'
    datetime = Column(DateTime, nullable=False)
    app_id = Column(Integer, ForeignKey('Apps.id'), nullable=False)
    duration = Column(Integer, nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint('datetime', 'app_id'),
    )
    app = relationship("App")

class HourlyBrowserRecords(PrintableBase):
    __tablename__ = 'HourlyBrowserRecords'
    datetime = Column(DateTime, nullable=False)
    website_id = Column(Integer, ForeignKey('Websites.id'), nullable=False)
    duration = Column(Integer, nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint('datetime', 'website_id'),
    )
    website = relationship("Website")

def create_db(readonly: bool=False) -> Session:
    if readonly:
        engine = create_engine(DB_PATH + '?mode=ro', uri=True)
    else:
        engine = create_engine(DB_PATH)
    PrintableBase.metadata.create_all(engine)
    session = sessionmaker(bind=engine)
    db = session()
    return db

def get_all_records() -> DataFrame:
    session = create_db()
    records = session.query(HourlyRecords).all()
    session.close()
    df = DataFrame([record.__dict__ for record in records])
    df.rename({'duration': 'usage'})
    return df
def get_all_apps_names() -> list[str]:
    session = create_db()
    apps = session.query(App).all()
    session.close()
    return [app.app_name for app in apps]
def get_all_websites_names() -> list[str]:
    session = create_db()
    websites = session.query(Website).all()
    session.close()
    return [website.domain_name for website in websites]
def get_last_browser_tab() -> str:
    session = create_db()
    record = session.query(BrowserRecord).join(Website, Website.id == BrowserRecord.website_id).order_by(BrowserRecord.timestamp.desc()).first()
    last_browser_tab = record.website.domain_name if record else None
    session.close()
    return last_browser_tab

def add_record(app_name: str, app_path: str, timestamp: int) -> None:
    # Create a database session
    session = create_db()
    # Check if the app is already in the database
    app = session.query(App).filter_by(app_name=app_name).first()
    if not app:
        # If not, create a new app entry
        app = App(app_name=app_name, file_location=app_path)
        session.add(app)
    # Create a new record entry
    record = Record(timestamp=timestamp, app=app)
    session.add(record)
    session.commit()
    session.close()
def add_browser_record(domain_name: str, timestamp: int) -> None:
    # Create a database session
    session = create_db()
    # Check if the app is already in the database
    website = session.query(Website).filter_by(domain_name=domain_name).first()
    if not website:
        # If not, create a new app entry
        website = Website(domain_name=domain_name)
        session.add(website)
    # Create a new browser_record entry
    browser_record = BrowserRecord(timestamp=timestamp, website=website)
    session.add(browser_record)
    session.commit()
    session.close()

def add_app(app_name: str, file_location: str='') -> None:
    session = create_db()
    app = session.query(App).filter_by(app_name=app_name).first()
    if not app:
        app = App(app_name=app_name, file_location=file_location or 'Unknown')
        session.add(app)
    session.commit()
    session.close()
def add_website(website_name: str) -> None:
    session = create_db()
    website = session.query(Website).filter_by(domain_name=website_name).first()
    if not website:
        website = Website(domain_name=website_name)
        session.add(website)
    session.commit()
    session.close()

def is_transformation_needed() -> int:
    """
    Checks if transformation is needed or not
    """
    session = create_db()
    count = session.query(Record).count()
    session.close()
    # Check if there are more than max records
    # 600 records (10 minutes)
    MAX_RECORDS = 600
    return max(0, MAX_RECORDS - count)

def transform_new_data() -> None:
    """
    Transform & migrate the existing data from BrowserRecords & Records tables
    into HourlyBrowserRecords & HourlyRecords tables respectively
    """
    session = create_db()
    # Get all records from Records table where app is a browser
    records_in_browser = session.query(Record).join(App, Record.app_id == App.id).filter(App.app_name == 'Chrome').subquery()
    # Get all records from BrowserRecords table joined with Records table
    browser_records = session.query(BrowserRecord).join(records_in_browser, BrowserRecord.timestamp == records_in_browser.c.timestamp).all()
    # group all records from BrowserRecords table based on primary key
    hourly_browser_records_dict = {}
    for record in browser_records:
        website_id = record.website_id
        timestamp = record.timestamp
        hour = datetime.fromtimestamp(timestamp).replace(minute=0, second=0, microsecond=0)
        if (hour, website_id) not in hourly_browser_records_dict:
            hourly_browser_records_dict[(hour, website_id)] = 0
        hourly_browser_records_dict[(hour, website_id)] += 1  # timestamp are in seconds
    # load into HourlyBrowserRecords (as upsert query)
    for (hour, website_id), duration in hourly_browser_records_dict.items():
        existing_hourly_browser_record = session.query(HourlyBrowserRecords).filter_by(datetime=hour, website_id=website_id).first()
        if existing_hourly_browser_record:
            existing_hourly_browser_record.duration += duration
        else:
            new_hourly_browser_record = HourlyBrowserRecords(datetime=hour, website_id=website_id, duration=duration)
            session.add(new_hourly_browser_record)
    # truncate BrowserRecords
    session.query(BrowserRecord).delete()

    # Get all records from Records table
    records = session.query(Record).all()
    # group all records from Records table based on primary key
    hourly_records_dict = {}
    for record in records:
        app_id = record.app_id
        timestamp = record.timestamp
        hour = datetime.fromtimestamp(timestamp).replace(minute=0, second=0, microsecond=0)
        if (hour, app_id) not in hourly_records_dict:
            hourly_records_dict[(hour, app_id)] = 0
        hourly_records_dict[(hour, app_id)] += 1  # timestamp are in seconds
    # load into HourlyRecords (as upsert query)
    for (hour, app_id), duration in hourly_records_dict.items():
        existing_hourly_record = session.query(HourlyRecords).filter_by(datetime=hour, app_id=app_id).first()
        if existing_hourly_record:
            existing_hourly_record.duration += duration
        else:
            new_hourly_record = HourlyRecords(datetime=hour, app_id=app_id, duration=duration)
            session.add(new_hourly_record)
    # truncate Records
    session.query(Record).delete()
    # commit
    session.commit()
    session.close()
    # refresh
    engine = create_engine(DB_PATH)
    with engine.connect() as connection:
        connection.execute(text("VACUUM"))
