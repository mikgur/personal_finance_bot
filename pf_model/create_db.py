"""Script for creating a new database for personal_finance_bot"""
import logging

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy_utils import database_exists, create_database

from .model import base
import settings


def create_db():
    try:
        db_string = f"postgres://{settings.DB_USER}:{settings.DB_PASSWORD}\
                    @{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_DATABASE}"
        db = create_engine(db_string)
        if not database_exists(db.url):
            logging.info(f"Creating database {settings.DB_DATABASE}...")
            create_database(db.url)
            base.metadata.create_all(db)
            logging.info("Done!")
        else:
            logging.warning(f"Database {settings.DB_DATABASE} exist. \
                             Please provide another DB_DATABASE in settings.py")
    except (OperationalError, ProgrammingError) as exc:
        logging.error(f"Error while working with DB: {exc}")
