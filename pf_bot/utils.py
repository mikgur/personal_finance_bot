import logging
import re

from pf_bot.exceptions import PFBNoCurrencies, PFBWrongCategory
from pf_model import data

AMOUNT_PATTERN = r"(^|\s)\d+([.,]\d{1,2})?"


def parse_transaction(line, user_id):
    text = line.lower()
    try:
        #  Search for transaction amount and currency
        amount_mo = re.search(amount_with_currency_pattern(), text)
        transaction_amount_currency = amount_mo.group().strip()
    except PFBNoCurrencies:
        logging.error("There are no currencies in database")
        raise

    transaction_amount = re.search(AMOUNT_PATTERN, transaction_amount_currency).group()
    transaction_currency = transaction_amount_currency.replace(transaction_amount, "").strip()
    transaction_amount = transaction_amount.replace(',', '.')
    text = text.replace(transaction_amount_currency, "")

    #  Search for category
    expense_category_list = [category for category in data.get_all_category_names(user_id)
                             if category.lower() in text]
    transaction_category = ""
    transaction_type = ""
    if expense_category_list:
        transaction_category = max(expense_category_list, key=len)
        text = text.replace(transaction_category, "")
        transaction_type = "expense"
    else:
        income_category_list = [category for category in data.get_all_category_names(user_id, "income")
                                if category.lower() in text]
        if income_category_list:
            transaction_category = max(income_category_list, key=len)
            text = text.replace(transaction_category, "")
            transaction_type = "income"
        else:
            logging.debug("при вводе транзакции указана неверная категория")
            raise PFBWrongCategory

    # Search for account
    account_list = [account for account in data.get_all_account_names(user_id) if account.lower() in text]
    transaction_account = ""
    if account_list:
        transaction_account = max(account_list, key=len)
        text = text.replace(transaction_account, "")
    else:
        transaction_account = "Наличные"  # считаем этот счет счетом по-умолчанию, далее добавим возможность выбора

    return {'amount': transaction_amount, 'currency': transaction_currency, 'category': transaction_category,
            'type': transaction_type, 'account': transaction_account}


def amount_with_currency_pattern():
    '''This pattern is used to extract amount and currency from text
    (e.g. '123.23usd', '12,4 руб')
    '''
    logging.debug("building transaction pattern")
    currencies = data.get_all_currencies_shortnames()
    if not currencies:
        raise PFBNoCurrencies
    currency_variants = [currency.capitalize() for currency in currencies]
    currency_variants.extend([currency.upper() for currency in currencies])
    currencies.extend(currency_variants)
    pattern = ''.join([r"(^|\s)\d+([.,]\d{1,2})? ?(", "|".join(currencies), r")?($|\s)"])
    return pattern
