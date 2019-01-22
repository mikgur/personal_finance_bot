'''This module facilitates data write operations to model
'''
import datetime
import logging

from sqlalchemy.orm import sessionmaker

from pf_bot.exceptions import PFBWrongCategoryType, PFBCategoryAlreadyExist

from .data_observer import get_all_category_names
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
        name = name.capitalize()
        if name in get_all_category_names(user_id, category_type_name, "active"):
            raise PFBCategoryAlreadyExist
        Session = sessionmaker(bind=db)
        session = Session()

        category_type_name_db = get_category_type_by_alias(category_type_name)
        category_type = session.query(CategoryType).filter(CategoryType.name == category_type_name_db).one()
        user = session.query(User).filter(User.user_id == user_id).one()

        query = session.query(Category).filter(Category.user == user,
                                               Category.name == name,
                                               Category.type == category_type)
        existing_category = query.first()
        if existing_category:
            existing_category.is_deleted = False
        else:
            session.add(Category(name=name, user=user, type=category_type, is_deleted=False))
        session.commit()
        return True
    except PFBWrongCategoryType:
        logging.error("Wrong category type is used to access database")
        return False
    except PFBCategoryAlreadyExist:
        logging.error("Trying to add category which already exist")
        raise
    except Exception as exc:
        logging.error(f'Error while adding category: {exc}')
        return False


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


def rename_category(user_id, new_category_name, old_category_name, category_type_name):
    logging_text = (f"rename_category user: {user_id} new_category_name: {new_category_name}"
                    + "old_category_name: {old_category_name} type: {category_type_name}")
    logging.info(logging_text)
    try:
        new_category_name = new_category_name.capitalize()
        if new_category_name in get_all_category_names(user_id, category_type_name, "active"):
            raise PFBCategoryAlreadyExist
        Session = sessionmaker(bind=db)
        session = Session()

        user = session.query(User).filter(User.user_id == user_id).one()
        query = session.query(Category).filter(Category.user == user)

        category_type_name_db = get_category_type_by_alias(category_type_name)
        category_type = session.query(CategoryType).filter(CategoryType.name == category_type_name_db).one()
        #  Search for category which needs to be renamed
        query = query.filter(Category.type == category_type, Category.name == old_category_name)
        #  Check that there is only one object in query
        category = query.one()
        category.name = new_category_name
        session.commit()
    except PFBWrongCategoryType:
        logging.error("Wrong category type is used to access database")
        raise
    except PFBCategoryAlreadyExist:
        logging.error("Trying to add category which already exist")
        raise
    except Exception as exc:
        logging.error(f"Cannot delete category: {exc}")
        raise
