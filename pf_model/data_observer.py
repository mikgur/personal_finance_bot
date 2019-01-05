'''This module facilitates data write operations to model
'''
import logging

from sqlalchemy.orm import sessionmaker

from pf_bot.exceptions import PFBWrongCategoryType

from .model import (Account, AccountType, Category, CategoryType, Currency,
                    User, db)
from .utils import get_category_type_by_alias


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


def get_all_currencies_shortnames():
    """returns a list with shortnames of all currencies"""
    try:
        Session = sessionmaker(bind=db)
        session = Session()

        return [cur.shortname for cur in session.query(Currency).all()]
    except Exception as exc:
        logging.error(f"Cannot get currencies list from database: {exc}")
        return []
