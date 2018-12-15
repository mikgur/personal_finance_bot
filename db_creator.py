"""Script for creating a new database for personal_finance_bot"""

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy_utils import database_exists, create_database

from data_model import data_model
import settings


if __name__ == '__main__':
    try:
        db_string = f"postgres://{settings.DB_USER}:{settings.DB_PASSWORD}\
                    @{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_DATABASE}"
        db = create_engine(db_string)
        if not database_exists(db.url):
            print(f"Creating database {settings.DB_DATABASE}...")
            create_database(db.url)
            model = data_model()
            base = model.base
            base.metadata.create_all(db)
            print("Done!")
        else:
            print(f"Database {settings.DB_DATABASE} exist. Please provide another DB_DATABASE in settings.py")
    except (OperationalError, ProgrammingError) as exc:
        print(f"Error while working with DB: {exc}")
