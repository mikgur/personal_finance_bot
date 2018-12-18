import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, ProgrammingError

from .model import CategoryType, Category, Currency, AccountType,\
                       TransactionType
import settings


def populate_db():
    try:
        db_string = f"postgres://{settings.DB_USER}:{settings.DB_PASSWORD}\
                    @{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_DATABASE}"
        db = create_engine(db_string)

        Session = sessionmaker(bind=db)
        session = Session()

        logging.info("Creative income/expense category types...")

        income_cat = CategoryType(name='income')
        expense_cat = CategoryType(name='expense')

        logging.info("Creating a few income and expense categories...")

        expenses_categories = ["Продукты", "Коммунальные услуги", "Кот", "Бары", "Рестораны"]
        expenses_categories_db = [Category(name=name, type=expense_cat) for name in expenses_categories]

        salary = Category(name="Зарплата", type=income_cat)

        logging.info("Creating 2 currencies...")

        rub = Currency(name="Рубль", shortname="руб")
        usd = Currency(name="Доллар", shortname="usd")

        logging.info("Creating account type...")

        ordinary_type = AccountType(name="обычный")

        logging.info("Creating 2 transaction types - income and expense")

        income_tr = TransactionType(name="income")
        expense_tr = TransactionType(name="expense")

        session.add_all([income_cat, expense_cat, salary])
        session.add_all(expenses_categories_db)
        session.add_all([rub, usd, ordinary_type])
        session.add_all([income_tr, expense_tr])

        session.commit()

        logging.info("Everything is ready. You can launch the bot!")
    except (OperationalError, ProgrammingError) as exc:
        logging.error(f"Error while working with DB: {exc}")
