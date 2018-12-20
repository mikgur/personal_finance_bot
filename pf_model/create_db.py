"""Script for creating a new database for personal_finance_bot"""
import logging

from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy_utils import database_exists, create_database

from .model import base, db, AccountType, CategoryType, Currency,\
                       TransactionType
import settings


def create_db():
    try:
        if not database_exists(db.url):
            logging.info(f"Creating database {settings.DB_DATABASE}...")
            create_database(db.url)
            base.metadata.create_all(db)
            logging.info("Done!")
        else:
            logging.warning(f"Database {settings.DB_DATABASE} exist. \
                             Please provide another DB_DATABASE in settings.py")

        Session = sessionmaker(bind=db)
        session = Session()

        logging.info("Creating income/expense category types...")

        income_cat = CategoryType(name='income')
        expense_cat = CategoryType(name='expense')

        logging.info("Creating 2 currencies...")

        rub = Currency(name="Рубль", shortname="руб")
        usd = Currency(name="Доллар", shortname="usd")

        logging.info("Creating account type...")

        ordinary_type = AccountType(name="general")

        logging.info("Creating 2 transaction types - income and expense")

        income_tr = TransactionType(name="income")
        expense_tr = TransactionType(name="expense")

        session.add_all([income_cat, expense_cat])
        session.add_all([rub, usd, ordinary_type])
        session.add_all([income_tr, expense_tr])

        session.commit()

        logging.info("Everything is ready. You can launch the bot!")
    except (OperationalError, ProgrammingError) as exc:
        logging.error(f"Error while working with DB: {exc}")
