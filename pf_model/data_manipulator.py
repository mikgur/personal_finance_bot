'''This module facilitates data write operations to model
'''
import datetime
import logging

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from .data_observer import get_all_category_names, get_all_account_names
from .exceptions import (
    AccountNotFoundOrMultipleAccounts, CategoryNotFoundOrMultipleCategories,
    ObjectAlreadyExist, TransactionTypeNotFoundOrMultipleTransactionTypes,
    UserNotFoundOrMultipleUsers, WrongCategoryType
)
from .model import (
    Account, AccountType, Category, CategoryType, Currency, Transaction,
    TransactionType, User, db
)
from .utils import get_category_type_by_alias


def add_account(
    name, user_id, currency_name, balance=0, account_type_name="general"
):
    '''Add Account to database.
    name - account name
    user_id - telegram user id (number)
    currency_name - shortname of currency (eg 'usd')
    account_type_name - name of type
    '''

    name = name.capitalize()
    if name in get_all_account_names(
        user_id, account_type_name, with_amounts=False
    ):
        raise ObjectAlreadyExist

    try:
        Session = sessionmaker(bind=db)
        session = Session()

        account_type = session.query(AccountType).filter(
            AccountType.name == account_type_name
        ).one()
        user = session.query(User).filter(User.user_id == user_id).one()
        currency = session.query(Currency).filter(
            Currency.shortname == currency_name
        ).one()

        query = session.query(Account).filter(
            Account.user == user, Account.name == name,
            Account.type == account_type
        )
        existing_account = query.first()
        if existing_account:
            existing_account.is_deleted = False
        else:
            session.add(
                Account(
                    name=name,
                    user=user,
                    currency=currency,
                    type=account_type,
                    initial_balance=balance,
                    is_deleted=False
                )
            )
        session.commit()
        return True
    except Exception as exc:
        logging.error(f'Error while adding account: {exc}')
        return False


def add_category(name, user_id, category_type_name="expense"):
    '''Add Category to database.
    name - category name
    user_id - telegram user id (number)
    category_type_name - name of type
    '''
    try:
        name = name.capitalize()
        if name in get_all_category_names(
            user_id, category_type_name, "active"
        ):
            raise ObjectAlreadyExist
        Session = sessionmaker(bind=db)
        session = Session()

        category_type_name_db = get_category_type_by_alias(category_type_name)
        category_type = session.query(CategoryType).filter(
            CategoryType.name == category_type_name_db
        ).one()
        user = session.query(User).filter(User.user_id == user_id).one()

        query = session.query(Category).filter(
            Category.user == user, Category.name == name,
            Category.type == category_type
        )
        existing_category = query.first()
        if existing_category:
            existing_category.is_deleted = False
        else:
            session.add(
                Category(
                    name=name, user=user, type=category_type, is_deleted=False
                )
            )
        session.commit()
        return True
    except WrongCategoryType:
        logging.error("Wrong category type is used to access database")
        return False
    except ObjectAlreadyExist:
        logging.error("Trying to add category which already exist")
        raise
    except Exception as exc:
        logging.error(f'Error while adding category: {exc}')
        return False


def add_transaction(transaction, user_id):

    Session = sessionmaker(bind=db)
    session = Session()
    try:
        # Search current user
        user = session.query(User).filter(User.user_id == user_id).one()
        # Search account for current user
    except (NoResultFound, MultipleResultsFound) as exc:
        logging.error(f"Cannot get user from database: {exc}")
        raise UserNotFoundOrMultipleUsers

    try:
        account = session.query(Account).filter(Account.user_id == user.id)\
            .filter(Account.name == transaction["account"]).one()
    except (NoResultFound, MultipleResultsFound) as exc:
        logging.error(f"Cannot get account from database: {exc}")
        raise AccountNotFoundOrMultipleAccounts

    try:
        # Search category for current user
        category = session.query(Category).filter(Category.user_id == user.id)\
            .filter(Category.name == transaction["category"]).one()
    except (NoResultFound, MultipleResultsFound) as exc:
        logging.error(f"Cannot get account from database: {exc}")
        raise CategoryNotFoundOrMultipleCategories

    try:
        # Search transaction type
        transaction_type = session.query(TransactionType).filter(
            TransactionType.name == transaction["type"]
        ).one()
    except (NoResultFound, MultipleResultsFound) as exc:
        logging.error(f"Cannot get account from database: {exc}")
        raise TransactionTypeNotFoundOrMultipleTransactionTypes

    # Make a new transaction
    new_transaction = Transaction(
        date=datetime.date.today(),
        user=user,
        category=category,
        account=account,
        type=transaction_type,
        amount=float(transaction["amount"])
    )
    session.add(new_transaction)
    session.commit()


def add_user(user_id, first_name, username):
    '''Add a new user to database. Also add 5 expense categories,
    2 accounts and 1 income category
    '''
    try:
        Session = sessionmaker(bind=db)
        session = Session()

        new_user = User(
            user_id=user_id, user_name=first_name, telegram_id=username
        )
        session.add(new_user)
        session.commit()

        expenses_categories = [
            "Продукты", "Коммунальные услуги", "Кот", "Бары", "Рестораны"
        ]
        for category in expenses_categories:
            add_category(category, user_id)

        add_category("Зарплата", user_id, "income")
        add_account("Наличные", user_id, "руб")
        add_account("Банк", user_id, "руб")
        session.commit()
    except Exception as exc:
        logging.error(f'Error while adding user: {exc}')


def delete_account(user_id, account_name, account_type_name="general"):
    try:
        Session = sessionmaker(bind=db)
        session = Session()

        user = session.query(User).filter(User.user_id == user_id).one()
        query = session.query(Account).filter(Account.user == user)

        account_type = session.query(AccountType).filter(
            AccountType.name == account_type_name
        ).one()
        #  Search for category which needs to be deleted
        query = query.filter(
            Account.type == account_type, Account.name == account_name
        )
        #  Check that there is only one object in query
        account = query.one()
        transaction_query = session.query(Transaction).filter(
            Transaction.account == account
        )
        #  We will delete account if there were no transactions releated to
        # it, we will mark category as deleted otherwise
        if transaction_query.first():
            account.is_deleted = True
        else:
            query.delete()
        session.commit()
        return True
    except Exception as exc:
        logging.error(f"Cannot delete account: {exc}")
        return False


def delete_category(user_id, category_name, category_type_name):
    try:
        Session = sessionmaker(bind=db)
        session = Session()

        user = session.query(User).filter(User.user_id == user_id).one()
        query = session.query(Category).filter(Category.user == user)

        category_type_name_db = get_category_type_by_alias(category_type_name)
        category_type = session.query(CategoryType).filter(
            CategoryType.name == category_type_name_db
        ).one()
        #  Search for category which needs to be deleted
        query = query.filter(
            Category.type == category_type, Category.name == category_name
        )
        #  Check that there is only one object in query
        category = query.one()
        transaction_query = session.query(Transaction).filter(
            Transaction.category == category
        )
        #  We will delete category if there were no transactions releated to
        # it, we will mark category as deleted otherwise
        if transaction_query.first():
            category.is_deleted = True
        else:
            query.delete()
        session.commit()
        return True
    except WrongCategoryType:
        logging.error("Wrong category type is used to access database")
        return False
    except Exception as exc:
        logging.error(f"Cannot delete category: {exc}")
        return False


def delete_transaction(user_id, transaction, transaction_type_name="expense"):
    Session = sessionmaker(bind=db)
    session = Session()

    try:
        # Search current user
        user = session.query(User).filter(User.user_id == user_id).one()
        # Search account for current user
    except (NoResultFound, MultipleResultsFound) as exc:
        logging.error(f"Cannot get user from database: {exc}")
        raise UserNotFoundOrMultipleUsers

    try:
        account = session.query(Account).filter(Account.user_id == user.id)\
            .filter(Account.name == transaction["account"]).one()
    except (NoResultFound, MultipleResultsFound) as exc:
        logging.error(f"Cannot get account from database: {exc}")
        raise AccountNotFoundOrMultipleAccounts

    try:
        # Search category for current user
        category = session.query(Category).filter(Category.user_id == user.id)\
            .filter(Category.name == transaction["category"]).one()
    except (NoResultFound, MultipleResultsFound) as exc:
        logging.error(f"Cannot get account from database: {exc}")
        raise CategoryNotFoundOrMultipleCategories

    try:
        # Search transaction type
        transaction_type = session.query(TransactionType).filter(
            TransactionType.name == transaction_type_name
        ).one()
    except (NoResultFound, MultipleResultsFound) as exc:
        logging.error(f"Cannot get account from database: {exc}")
        raise TransactionTypeNotFoundOrMultipleTransactionTypes

    try:
        amount = float(transaction["amount"].replace(" ", ""))
    except ValueError:
        logging.error(f"cannot convert amount to float")
        return False

    query = session.query(
            Transaction
        ).join(Category, Account, Currency, TransactionType).filter(
            Transaction.user_id == user.id,
            Transaction.type_id == transaction_type.id,
            Transaction.account_id == account.id,
            Transaction.category_id == category.id,
            Transaction.date == transaction["date"],
            Transaction.amount == amount
        )

    db_transaction = query.first()
    if db_transaction:
        session.delete(db_transaction)
        session.commit()
        return True

    return False


def edit_account(
    user_id, new_account_name, old_account_name, account_type_name="general"
):
    logging_text = (
        f"edit_account user: {user_id} \
        new_account_name: {new_account_name} \
        old_account_name: {old_account_name} \
        type: {account_type_name}"
    )
    logging.info(logging_text)
    try:
        new_account_name = new_account_name.capitalize()
        if new_account_name in get_all_account_names(
            user_id, account_type_name, with_amounts=False
        ):
            raise ObjectAlreadyExist
        Session = sessionmaker(bind=db)
        session = Session()

        user = session.query(User).filter(User.user_id == user_id).one()
        query = session.query(Account).filter(Account.user == user)

        account_type = session.query(AccountType).filter(
            AccountType.name == account_type_name
        ).one()
        #  Search for account which needs to be renamed
        query = query.filter(
            Account.type == account_type, Account.name == old_account_name
        )
        #  Check that there is only one object in query
        account = query.one()
        account.name = new_account_name
        session.commit()
    except ObjectAlreadyExist:
        logging.error("Trying to add account which already exist")
        raise
    except Exception as exc:
        logging.error(f"Cannot edit account: {exc}")
        raise


def rename_category(
    user_id, new_category_name, old_category_name, category_type_name
):
    logging_text = (
        f"rename_category user: {user_id} \
        new_category_name: {new_category_name} \
        old_category_name: {old_category_name} \
        type: {category_type_name}"
    )
    logging.info(logging_text)
    try:
        new_category_name = new_category_name.capitalize()
        if new_category_name in get_all_category_names(
            user_id, category_type_name, "active"
        ):
            raise ObjectAlreadyExist
        Session = sessionmaker(bind=db)
        session = Session()

        user = session.query(User).filter(User.user_id == user_id).one()
        query = session.query(Category).filter(Category.user == user)

        category_type_name_db = get_category_type_by_alias(category_type_name)
        category_type = session.query(CategoryType).filter(
            CategoryType.name == category_type_name_db
        ).one()
        #  Search for category which needs to be renamed
        query = query.filter(
            Category.type == category_type, Category.name == old_category_name
        )
        #  Check that there is only one object in query
        category = query.one()
        category.name = new_category_name
        session.commit()
    except WrongCategoryType:
        logging.error("Wrong category type is used to access database")
        raise
    except ObjectAlreadyExist:
        logging.error("Trying to add category which already exist")
        raise
    except Exception as exc:
        logging.error(f"Cannot rename category: {exc}")
        raise


def set_otp_for_user(telegram_id, otp):
    Session = sessionmaker(bind=db)
    session = Session()

    # Search current user
    user = session.query(User).filter(User.telegram_id == telegram_id).one()
    user.set_otp(str(otp))

    session.commit()
