'''This module facilitates data read/write operations to/from model
'''
import datetime
import logging

from sqlalchemy.orm import sessionmaker

from pf_bot.exceptions import PFBWrongCategoryType

from .model import (Account, AccountType, Category, CategoryType, Currency,
                    Transaction, TransactionType, User, db)
from .utils import get_category_type_by_alias


def add_account(name, user_id, currency_name, account_type_name="general"):
    '''Add Account to database.
    name - account name
    user_id - telegram user id (number)
    currency_name - shortname of currency (eg 'usd')
    account_type_name - name of type
    '''
    try:
        Session = sessionmaker(bind=db)
        session = Session()

        account_type = session.query(AccountType).filter(AccountType.name == account_type_name).one()
        user = session.query(User).filter(User.user_id == user_id).one()
        currency = session.query(Currency).filter(Currency.shortname == currency_name).one()

        session.add(Account(name=name, user=user, currency=currency, type=account_type))
        session.commit()
    except Exception as exc:
        logging.error(f'Error while adding account: {exc}')


def add_category(name, user_id, category_type_name="expense"):
    '''Add Category to database.
    name - category name
    user_id - telegram user id (number)
    category_type_name - name of type
    '''
    try:
        Session = sessionmaker(bind=db)
        session = Session()

        category_type_name_db = get_category_type_by_alias(category_type_name)
        category_type = session.query(CategoryType).filter(CategoryType.name == category_type_name_db).one()
        user = session.query(User).filter(User.user_id == user_id).one()

        session.add(Category(name=name, user=user, type=category_type, is_deleted=False))
        session.commit()
    except Exception as exc:
        logging.error(f'Error while adding category: {exc}')


def add_transaction(transaction, user_id):
    try:
        Session = sessionmaker(bind=db)
        session = Session()

        # Search current user
        user = session.query(User).filter(User.user_id == user_id).one()
        # Search account for current user
        account = session.query(Account).filter(Account.user_id == user.id)\
                                        .filter(Account.name == transaction["account"]).one()
        # Search category for current user
        category = session.query(Category).filter(Category.user_id == user.id)\
                                          .filter(Category.name == transaction["category"]).one()
        # Search transaction type
        transaction_type = session.query(TransactionType).filter(TransactionType.name == transaction["type"]).one()
        # Make a new transaction
        new_transaction = Transaction(date=datetime.date.today(), user=user, category=category, account=account,
                                      type=transaction_type, amount=float(transaction["amount"]))
        session.add(new_transaction)
        session.commit()
    except Exception as exc:
        logging.error(f'Error while adding transaction: {exc}')


def add_user(user_id, user_name):
    '''Add a new user to database. Also add 5 expense categories,
    2 accounts and 1 income category
    '''
    try:
        Session = sessionmaker(bind=db)
        session = Session()

        new_user = User(user_id=user_id, user_name=user_name)
        session.add(new_user)
        session.commit()

        expenses_categories = ["Продукты", "Коммунальные услуги", "Кот", "Бары", "Рестораны"]
        for category in expenses_categories:
            add_category(category, user_id)

        add_category("Зарплата", user_id, "income")
        add_account("Наличные", user_id, "руб")
        add_account("Банк", user_id, "руб")
        session.commit()
    except Exception as exc:
        logging.error(f'Error while adding user: {exc}')


def get_all_account_names(user_id, account_type_name="general"):
    '''returns a list with names of all accounts of particular type'''
    try:
        Session = sessionmaker(bind=db)
        session = Session()

        user = session.query(User).filter(User.user_id == user_id).one()
        query = session.query(Account).filter(Account.user == user)
        if account_type_name:
            account_type = session.query(AccountType).filter(AccountType.name == account_type_name).one()
            query = query.filter(Account.type == account_type)
        return [acc.name for acc in query.all()]
    except Exception as exc:
        logging.error(f'Cannot get accounts from database: {exc}')
        return []


def get_all_category_names(user_id, category_type_name="expense", status="active"):
    """returns a list with names of all categories of particular type
        status = ["active", "deleted", "all"]
    """
    try:
        Session = sessionmaker(bind=db)
        session = Session()

        user = session.query(User).filter(User.user_id == user_id).one()
        query = session.query(Category).filter(Category.user == user)
        if category_type_name:
            category_type_name_db = get_category_type_by_alias(category_type_name)
            category_type = session.query(CategoryType).filter(CategoryType.name == category_type_name_db).one()
            query = query.filter(Category.type == category_type)
            if status == "active":
                query = query.filter(Category.is_deleted.is_(False))
            elif status == "deleted":
                query = query.filter(Category.is_deleted.is_(True))
        return [cat.name for cat in query.all()]
    except PFBWrongCategoryType:
        logging.error("Wrong category type is used to access database")
        return []
    except Exception as exc:
        logging.error(f"Cannot get categories from database: {exc}")
        return []


def delete_category(user_id, category_name, category_type_name):
    logging.info(f"data.delete_category user: {user_id} category_name: {category_name} type: {category_type_name}")
    try:
        Session = sessionmaker(bind=db)
        session = Session()

        user = session.query(User).filter(User.user_id == user_id).one()
        query = session.query(Category).filter(Category.user == user)

        category_type_name_db = get_category_type_by_alias(category_type_name)
        category_type = session.query(CategoryType).filter(CategoryType.name == category_type_name_db).one()
        #  Search for category which needs to be deleted
        query = query.filter(Category.type == category_type, Category.name == category_name)
        #  Check that there is only one object in query
        category = query.one()
        if category:
            transaction_query = session.query(Transaction).filter(Transaction.category == category)
            #  We will delete category if there were no transactions releated to it,
            #  we will mark category as deleted otherwise
            if transaction_query.first():
                category.is_deleted = True
            else:
                query.delete()
            session.commit()
            return True
    except PFBWrongCategoryType:
        logging.error("Wrong category type is used to access database")
        return False
    except Exception as exc:
        logging.error(f"Cannot delete category: {exc}")
        return False


def get_all_currencies_shortnames():
    """returns a list with shortnames of all currencies"""
    try:
        Session = sessionmaker(bind=db)
        session = Session()

        return [cur.shortname for cur in session.query(Currency).all()]
    except Exception as exc:
        logging.error(f"Cannot get currencies list from database: {exc}")
        return []
