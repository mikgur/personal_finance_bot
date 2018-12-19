'''This module facilitates data read/write operations to/from model
'''
import logging

from sqlalchemy.orm import sessionmaker

from .model import db, Account, AccountType, Category, CategoryType, Currency, User


def is_existing_user(user_id):
    '''Does this user exist in database?
    '''
    logging.debug("is_existing_user")
    Session = sessionmaker(bind=db)
    session = Session()
    return bool(session.query(User).filter(User.user_id == user_id).all())


def add_user(user_id, user_name):
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


def add_category(name, user_id, category_type_name="expense"):
    Session = sessionmaker(bind=db)
    session = Session()

    category_type = session.query(CategoryType).filter(CategoryType.name == category_type_name).one()
    user = session.query(User).filter(User.user_id == user_id).one()

    session.add(Category(name=name, user=user, type=category_type))
    session.commit()


def get_all_category_names(user_id, category_type_name="expense"):
    Session = sessionmaker(bind=db)
    session = Session()

    user = session.query(User).filter(User.user_id == user_id).one()
    query = session.query(Category).filter(Category.user == user)
    if category_type_name:
        category_type = session.query(CategoryType).filter(CategoryType.name == category_type_name).one()
        query = query.filter(Category.type == category_type)
    return [cat.name for cat in query.all()]


def add_account(name, user_id, currency_name, account_type_name="general"):
    Session = sessionmaker(bind=db)
    session = Session()

    account_type = session.query(AccountType).filter(AccountType.name == account_type_name).one()
    user = session.query(User).filter(User.user_id == user_id).one()
    currency = session.query(Currency).filter(Currency.shortname == currency_name).one()

    session.add(Account(name=name, user=user, currency=currency, type=account_type))
    session.commit()


def get_all_account_names(user_id, account_type_name="general"):
    Session = sessionmaker(bind=db)
    session = Session()

    user = session.query(User).filter(User.user_id == user_id).one()
    query = session.query(Account).filter(Account.user == user)
    if account_type_name:
        account_type = session.query(AccountType).filter(AccountType.name == account_type_name).one()
        query = query.filter(Account.type == account_type)
    return [acc.name for acc in query.all()]
