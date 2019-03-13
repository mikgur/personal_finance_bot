'''This module facilitates data write operations to model
'''
import logging
import datetime

import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from .exceptions import (AccountNotFoundOrMultipleAccounts,
                         UserNotFoundOrMultipleUsers, WrongCategoryType)
from .model import (Account, AccountType, Category, CategoryType, Currency,
                    Transaction, TransactionType, User, db)
from .utils import get_category_type_by_alias


def get_all_account_names(
    user_id,
    account_type_name="general",
    with_info=True,
    with_numeric_amounts=False
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
        if with_info:
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
                        acc.name,
                        (acc_balance if with_numeric_amounts
                            else f'{acc_balance:,.2f}'.replace(',', ' ')),
                        acc.currency.shortname,
                        acc.creation_date,
                        acc.initial_balance
                    ]
                )
            return sorted(accounts_info, key=lambda a: a[0])
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
                             period=None,
                             amount_as_string=True):
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
                Transaction.date >= period[0],
                Transaction.date <= period[1]
            )
    except Exception as exc:
        logging.error(f"Cannot get transactions info from database: {exc}")
        return []

    if amount_as_string:
        transactions_info = [
            {'date': f"{transaction[0]:%Y-%m-%d}",
             'category': transaction[1],
             'account': transaction[2],
             'amount': f'{transaction[3]:,.2f}'.replace(',', ' '),
             'currency': transaction[4]} for transaction
            in transactions_query.all()
        ]
        return transactions_info

    transactions_info = [
            {'date': f"{transaction[0]:%Y-%m-%d}",
             'category': transaction[1],
             'account': transaction[2],
             'amount': transaction[3],
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


def get_categories_trends(
    user_id, period, transaction_type_name="expense"
):
    transactions = get_list_of_transactions(
        user_id=user_id,
        period=period,
        transaction_type_name=transaction_type_name,
        amount_as_string=False
    )

    transaction_data = [(tr['date'], tr['amount'], tr['category']) for
                        tr in transactions]
    categories = list(set(tr[2] for tr in transaction_data))
    for category in categories:
        dt_start_of_month = datetime.date(year=period[0].year,
                                          month=period[0].month,
                                          day=period[0].day)
        transaction_data.append((dt_start_of_month, 0, category))

    data = pd.DataFrame(transaction_data,
                        columns=['date', 'amount', 'category'])
    data['date'] = pd.to_datetime(data['date'])
    data.sort_values(by=['date'], inplace=True)

    result = {cat: data[data['category'] == cat].groupby('date').sum().cumsum()
              for cat in categories}

    dt_end_of_month = datetime.date(year=period[1].year,
                                    month=period[1].month,
                                    day=period[1].day)
    for cat in categories:
        result[cat].loc[dt_end_of_month] = result[cat].iloc[-1]
    return result


def get_account_balance(user_id, account_name, date):
    Session = sessionmaker(bind=db)
    session = Session()

    try:
        user = session.query(User).filter(User.user_id == user_id).one()
    except (NoResultFound, MultipleResultsFound) as exc:
        logging.error(f"Cannot get user from database: {exc}")
        raise UserNotFoundOrMultipleUsers

    try:
        account = session.query(Account).filter(
            Account.user == user,
            Account.name == account_name
        ).one()
    except (NoResultFound, MultipleResultsFound) as exc:
        logging.error(f"Cannot get account from database: {exc}")
        raise AccountNotFoundOrMultipleAccounts
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
    income_transactions = session.query(Transaction).filter(
        Transaction.account == account,
        Transaction.type == income,
        Transaction.date < date
    ).all()
    expense_transactions = session.query(Transaction).filter(
        Transaction.account == account,
        Transaction.type == expense,
        Transaction.date < date
    ).all()
    balance = (account.initial_balance
               if account.creation_date <= date else 0)
    balance += (sum(tr.amount for tr in income_transactions)
                - sum(tr.amount for tr in expense_transactions))
    return balance


def get_balances_trends(
    user_id, period
):
    expense = get_list_of_transactions(
        user_id=user_id,
        period=period,
        transaction_type_name="expense",
        amount_as_string=False
    )

    income = get_list_of_transactions(
        user_id=user_id,
        period=period,
        transaction_type_name="income",
        amount_as_string=False
    )

    expense_data = [(tr['date'], -tr['amount'], tr['account']) for
                    tr in expense]
    income_data = [(tr['date'], tr['amount'], tr['account']) for
                   tr in income]
    transaction_data = expense_data + income_data

    accounts = get_all_account_names(user_id)
    for account in accounts:
        dt_start_of_month = datetime.date(year=period[0].year,
                                          month=period[0].month,
                                          day=period[0].day)
        transaction_data.append((dt_start_of_month,
                                 get_account_balance(user_id,
                                                     account[0],
                                                     dt_start_of_month),
                                 account[0]))
        if period[0] < account[3] <= period[1]:
            transaction_data.append((account[3],
                                     account[4],
                                     account[0]))

    data = pd.DataFrame(transaction_data,
                        columns=['date', 'amount', 'account'])
    data['date'] = pd.to_datetime(data['date'])
    data.sort_values(by=['date'], inplace=True)

    result = {acc[0]:
              data[data['account'] == acc[0]].groupby('date').sum().cumsum()
              for acc in accounts}

    dt_end_of_month = datetime.date(year=period[1].year,
                                    month=period[1].month,
                                    day=period[1].day)
    for acc in accounts:
        result[acc[0]].loc[dt_end_of_month] = result[acc[0]].iloc[-1]
    return result
