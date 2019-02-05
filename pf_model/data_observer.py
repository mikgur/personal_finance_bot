'''This module facilitates data write operations to model
'''
import logging

from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from .exceptions import UserNotFoundOrMultipleUsers, WrongCategoryType
from .model import (
    Account, AccountType, Category, CategoryType, Currency, Transaction,
    TransactionType, User, db
)
from .utils import get_category_type_by_alias


def get_all_account_names(
    user_id, account_type_name="general", with_amounts=True
):
    """returns a list with names of all accounts of particular type with/
    without corresponding currency
    """
    try:
        Session = sessionmaker(bind=db)
        session = Session()

        user = session.query(User).filter(User.user_id == user_id).one()
        query = session.query(Account).filter(Account.user == user)
        if account_type_name:
            account_type = (
                session.query(AccountType).filter(
                    AccountType.name == account_type_name
                ).one()
            )
            query = query.filter(Account.type == account_type)
        if with_amounts:
            expense = (
                session.query(TransactionType).filter(
                    TransactionType.name == "expense"
                ).one()
            )
            income = (
                session.query(TransactionType).filter(
                    TransactionType.name == "income"
                ).one()
            )
            accounts_info = []
            for acc in query.all():
                acc_balance = (
                    acc.initial_balance + sum(
                        tr.amount
                        for tr in acc.transactions if tr.type == income
                    ) - sum(
                        tr.amount
                        for tr in acc.transactions if tr.type == expense
                    )
                )

                accounts_info.append(
                    [
                        acc.name, f'{acc_balance:,.2f}'.replace(',', ' '),
                        acc.currency.shortname
                    ]
                )
            return accounts_info
        return [acc.name for acc in query.all()]
    except Exception as exc:
        logging.error(f'Cannot get accounts from database: {exc}')
        return []


def get_all_category_names(
    user_id, category_type_name="expense", status="active"
):
    """returns a list with names of all categories of particular type
        status = ["active", "deleted", "all"]
    """
    try:
        Session = sessionmaker(bind=db)
        session = Session()

        user = session.query(User).filter(User.user_id == user_id).one()
        query = session.query(Category).filter(Category.user == user)
        if category_type_name:
            category_type_name_db = get_category_type_by_alias(
                category_type_name
            )
            category_type = (
                session.query(CategoryType).filter(
                    CategoryType.name == category_type_name_db
                ).one()
            )
            query = query.filter(Category.type == category_type)
            if status == "active":
                query = query.filter(Category.is_deleted.is_(False))
            elif status == "deleted":
                query = query.filter(Category.is_deleted.is_(True))
        return [cat.name for cat in query.all()]
    except WrongCategoryType:
        logging.error("Wrong category type is used to access database")
        return []
    except Exception as exc:
        logging.error(f"Cannot get categories from database: {exc}")
        return []


def get_all_currency_shortnames():
    """returns a list with shortnames of all currencies"""
    try:
        Session = sessionmaker(bind=db)
        session = Session()

        return [cur.shortname for cur in session.query(Currency).all()]
    except Exception as exc:
        logging.error(f"Cannot get currencies list from database: {exc}")
        return []


def get_all_telegram_id():
    """returns a list of all telegram_id from database"""
    try:
        Session = sessionmaker(bind=db)
        session = Session()

        return [user.telegram_id for user in session.query(User).all()]
    except Exception as exc:
        logging.error(f"Cannot get user list from database: {exc}")
        return []


def get_list_of_transactions(user_id,
                             transaction_type_name="expense",
                             period=None):
    """returns a list of dictionaries with transaction info.
    Example:
    [{'date': 28/02/2019, 'category': 'Кот', 'account': 'Наличные',
    'amount': 3500, 'currency': 'руб'}]
    """
    Session = sessionmaker(bind=db)
    session = Session()

    try:
        user = session.query(User).filter(User.user_id == user_id).one()
    except (NoResultFound, MultipleResultsFound) as exc:
        logging.error(f"Cannot get user from database: {exc}")
        raise UserNotFoundOrMultipleUsers
    try:
        transaction_type = (session
                            .query(TransactionType)
                            .filter(
                                TransactionType.name == transaction_type_name
                            )
                            .one())
    except (NoResultFound, MultipleResultsFound) as exc:
        logging.error(f"Cannot get transaction_type from database: {exc}")
        raise WrongCategoryType

    try:
        query = session.query(
            Transaction.date,
            Category.name,
            Account.name,
            Transaction.amount,
            Currency.shortname
        ).join(Category, Account, Currency).filter(
            Transaction.user_id == user.id,
            Transaction.type_id == transaction_type.id
        )
        transactions_query = query
        if period:
            transactions_query = query.filter(
                Transaction.date >= period["start"],
                Transaction.date <= period["end"]
            )
    except Exception as exc:
        logging.error(f"Cannot get transactions info from database: {exc}")
        return []

    transactions_info = [
        {'date': f"{transaction[0]:%Y-%m-%d}",
         'category': transaction[1],
         'account': transaction[2],
         'amount': f'{transaction[3]:,.2f}'.replace(',', ' '),
         'currency': transaction[4]} for transaction
        in transactions_query.all()
    ]

    return transactions_info


def get_user_chat_id(telegram_id):
    try:
        Session = sessionmaker(bind=db)
        session = Session()
        user = session.query(User).filter(User.telegram_id == telegram_id
                                          ).one()
    except (NoResultFound, MultipleResultsFound) as exc:
        logging.error(f"Cannot get user from database: {exc}")
        raise UserNotFoundOrMultipleUsers

    return user.user_id


def statistics_for_period_by_category(
    user_id, period, category_type_name="expense"
):
    """returns a transaction amounts aggregated by categories for a period"""
    try:
        Session = sessionmaker(bind=db)
        session = Session()

        user = session.query(User).filter(User.user_id == user_id).one()
        category_type = (
            session.query(CategoryType).filter(
                CategoryType.name == category_type_name
            ).one()
        )

        query = session.query(
            func.sum(Transaction.amount).label('total'), Category.name
        ).join(Category, CategoryType).filter(
            Transaction.user_id == user.id,
            CategoryType.id == category_type.id, Transaction.date >= period[0],
            Transaction.date <= period[1]
        ).group_by(Category.name).order_by(
            func.sum(Transaction.amount).label('total').desc()
        )

        return query.all()

    except Exception as exc:
        logging.error(f"Cannot get transactions list from database: {exc}")
        return []
