'''This module facilitates data read/write operations to/from model
'''
import datetime
import logging

from sqlalchemy.orm import sessionmaker

from .model import (Account, AccountType, Category, CategoryType, Currency,
                    Transaction, TransactionType, User, db)


def is_existing_user(user_id):
    '''Does this user exist in database?
    '''
    logging.debug("is_existing_user")
    Session = sessionmaker(bind=db)
    session = Session()
    return bool(session.query(User).filter(User.user_id == user_id).all())


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

        category_type = session.query(CategoryType).filter(CategoryType.name == category_type_name).one()
        user = session.query(User).filter(User.user_id == user_id).one()

        session.add(Category(name=name, user=user, type=category_type))
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


def get_all_category_names(user_id, category_type_name="expense"):
    '''returns a list with names of all categories of particular type'''
    try:
        Session = sessionmaker(bind=db)
        session = Session()

        user = session.query(User).filter(User.user_id == user_id).one()
        query = session.query(Category).filter(Category.user == user)
        if category_type_name:
            category_type = session.query(CategoryType).filter(CategoryType.name == category_type_name).one()
            query = query.filter(Category.type == category_type)
        return [cat.name for cat in query.all()]
    except Exception as exc:
        logging.error(f'Cannot get categories from database: {exc}')
        return []


def get_all_currencies_shortnames():
    '''returns a list with shortnames of all currencies'''
    try:
        Session = sessionmaker(bind=db)
        session = Session()

        return [cur.shortname for cur in session.query(Currency).all()]
    except Exception as exc:
        logging.error(f'Cannot get currencies list from database: {exc}')
        return []
