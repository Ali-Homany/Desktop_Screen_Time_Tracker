import os
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    PrimaryKeyConstraint
)


"""
This module is responsible for interacting with the database,
including creating tables, inserting data, and querying data.
"""


# DB file directory in Documents
documents_dir = os.path.join(
    os.path.expanduser('~'),
    'Documents',
    'Screen_Time_Tracker'
)
os.makedirs(documents_dir, exist_ok=True)
DB_PATH = f'sqlite:///{documents_dir}/screentime.db'
Base = declarative_base()


class PrintableBase(Base):
    __abstract__ = True
    def __str__(self):
        string = f'{self.__class__.__name__}'
        string += f'({", ".join(
            f"{k}={v}"
            for k, v in self.__dict__.items()
            if not k.startswith('_')
        )})'
        return string


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
    app = relationship('App')


class BrowserRecord(PrintableBase):
    __tablename__ = 'BrowserRecords'
    id = Column(Integer, primary_key=True)
    timestamp = Column(Integer, nullable=False)
    website_id = Column(Integer, ForeignKey('Websites.id'), nullable=False)
    website = relationship('Website')


class HourlyRecords(PrintableBase):
    __tablename__ = 'HourlyRecords'
    datetime = Column(DateTime, nullable=False)
    app_id = Column(Integer, ForeignKey('Apps.id'), nullable=False)
    duration = Column(Integer, nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint('datetime', 'app_id'),
    )
    app = relationship('App')


class HourlyBrowserRecords(PrintableBase):
    __tablename__ = 'HourlyBrowserRecords'
    datetime = Column(DateTime, nullable=False)
    website_id = Column(Integer, ForeignKey('Websites.id'), nullable=False)
    duration = Column(Integer, nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint('datetime', 'website_id'),
    )
    website = relationship('Website')


def init_db_engine() -> Session:
    engine = create_engine(DB_PATH)
    PrintableBase.metadata.create_all(engine)
    return engine


def create_session(engine: Engine=None) -> Session:
    engine = engine or init_db_engine()
    session_maker = sessionmaker(bind=engine)
    session = session_maker()
    return session


def refresh_db(engine: Engine) -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text('VACUUM'))
        return True
    except Exception as e:
        print(e)
        return False


engine = init_db_engine()
