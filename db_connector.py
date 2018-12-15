from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, ProgrammingError

from data_model import data_model
import settings


if __name__ == '__main__':
    try:
        db_string = f"postgres://{settings.DB_USER}:{settings.DB_PASSWORD}\
                    @{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_DATABASE}"
        db = create_engine(db_string)
        model = data_model()
        base = model.base

        Session = sessionmaker(bind=db)
        session = Session()

        print("Creative income/expense category types...")

        income_cat = model.CategoryType(name='income')
        expense_cat = model.CategoryType(name='expense')

        print("Creating a few income and expense categories...")

        expenses_categories = ["Продукты", "Коммунальные услуги", "Кот", "Бары", "Рестораны"]
        expenses_categories_db = [model.Category(name=name, type=expense_cat) for name in expenses_categories]

        salary = model.Category(name="Зарплата", type=income_cat)

        print("Creating 2 currencies...")

        rub = model.Currency(name="Рубль", shortname="руб")
        usd = model.Currency(name="Доллар", shortname="usd")

        print("Creating account type...")

        ordinary_type = model.AccountType(name="обычный")

        print("Creating 2 transaction types - income and expense")

        income_tr = model.TransactionType(name="income")
        expense_tr = model.TransactionType(name="expense")

        session.add_all([income_cat, expense_cat, salary])
        session.add_all(expenses_categories_db)
        session.add_all([rub, usd, ordinary_type])
        session.add_all([income_tr, expense_tr])

        session.commit()

        print("Everything is ready. You can launch the bot!")
    except (OperationalError, ProgrammingError) as exc:
        print(f"Error while working with DB: {exc}")
