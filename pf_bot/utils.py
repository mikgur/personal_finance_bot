import calendar
import datetime
import logging
import re
from collections import namedtuple

from telegram import ReplyKeyboardMarkup

from pf_model import data_observer
from pf_model.exceptions import NoCurrencies, WrongCategory

AMOUNT_PATTERN = r"(^|\s)\d+([.,]\d{1,2})?"

Confirmation = namedtuple("Confirmation", "yes no")
confirmation = Confirmation("Да", "Нет")

MainMenu = namedtuple("MainManu", "input statistics categories accounts")
main_menu = MainMenu("Ввести доход/расход", "Статистика", "Категории", "Счета")


def get_keyboard(context="main_menu", one_time_keyboard=False):
    if context == "main_menu":
        return get_keyboard_from_list(list(main_menu), cancel=False)
    elif context == "confirmation":
        return ReplyKeyboardMarkup(
            [list(confirmation)],
            one_time_keyboard=one_time_keyboard,
            resize_keyboard=True
        )


def get_keyboard_from_list(
    names, number_of_rows=2, cancel=True, one_time_keyboard=False
):
    """
    Function create a keyboard from names of categories/accounts/other
    list of objects
    """
    keyboard_buttons = []
    buttons = names.copy()
    if cancel:
        buttons.append('Назад')

    for num, name in enumerate(buttons):
        if num % number_of_rows == 0:
            keyboard_buttons.append([])
        keyboard_buttons[-1].append(name)
    return ReplyKeyboardMarkup(
        keyboard_buttons,
        one_time_keyboard=one_time_keyboard,
        resize_keyboard=True
    )


def make_re_template_for_menu(choices):
    """
    Function create a regex for a list of menu choices.
    e.g. for a list of choices = ["option1", "option2", "option3"]
    resulting regex will only accept "option1" or "option2" or "option3"
    """
    return f"^({')|('.join(choices)})$"


def month_edges(month_relative_positions=0):
    """ return edges of month which is month_relative_position
        earlier then current:
        month_edges(0) in Jan 2019 will return [01.01.2019, 31.01.2019]
        month_edges(1) in Jan 2019 will return [01.12.2018, 31.12.2018]
        month_edges(12) in Jan 2019 will return [01.01.2018, 31.01.2018]
    """
    today = datetime.datetime.today()
    year = today.year - month_relative_positions // 12
    if today.month > month_relative_positions % 12:
        month = today.month - month_relative_positions % 12
    else:
        year -= 1
        month = 12 + (today.month - month_relative_positions % 12)

    _, num_days = calendar.monthrange(year, month)
    first_day = datetime.date(year=year, month=month, day=1)
    last_day = datetime.date(year=year, month=month, day=num_days)
    return [first_day, last_day]


def parse_transaction(line, user_id):
    text = line.lower()
    try:
        #  Search for transaction amount and currency
        amount_mo = re.search(amount_with_currency_pattern(), text)
        transaction_amount_currency = amount_mo.group().strip()
    except NoCurrencies:
        logging.error("There are no currencies in database")
        raise

    transaction_amount = re.search(
        AMOUNT_PATTERN, transaction_amount_currency
    ).group()
    transaction_currency = transaction_amount_currency.replace(
        transaction_amount, ""
    ).strip()
    transaction_amount = transaction_amount.replace(",", ".")
    text = text.replace(transaction_amount_currency, "")

    #  Search for category
    expense_category_list = [
        category for category in data_observer.get_all_category_names(user_id)
        if category.lower() in text
    ]
    transaction_category = ""
    transaction_type = ""
    if expense_category_list:
        transaction_category = max(expense_category_list, key=len)
        text = text.replace(transaction_category, "")
        transaction_type = "expense"
    else:
        income_category_list = [
            category for category in data_observer.
            get_all_category_names(user_id, "income")
            if category.lower() in text
        ]
        if income_category_list:
            transaction_category = max(income_category_list, key=len)
            text = text.replace(transaction_category, "")
            transaction_type = "income"
        else:
            logging.debug("при вводе транзакции указана неверная категория")
            raise WrongCategory

    # Search for account
    account_list = [
        account for account in data_observer.get_all_account_names(user_id)
        if account.lower() in text
    ]
    transaction_account = ""
    if account_list:
        transaction_account = max(account_list, key=len)
        text = text.replace(transaction_account, "")
    else:
        # считаем этот счет счетом по-умолчанию,
        # далее добавим возможность выбора"
        transaction_account = "Наличные"

    return {
        "amount": transaction_amount,
        "currency": transaction_currency,
        "category": transaction_category,
        "type": transaction_type,
        "account": transaction_account
    }


def amount_with_currency_pattern():
    """This pattern is used to extract amount and currency from text
    (e.g. '123.23usd', '12,4 руб')
    """
    logging.debug("building transaction pattern")
    currencies = data_observer.get_all_currency_shortnames()
    if not currencies:
        raise NoCurrencies
    currency_variants = [currency.capitalize() for currency in currencies]
    currency_variants.extend([currency.upper() for currency in currencies])
    currencies.extend(currency_variants)
    pattern = ''.join(
        [r"(^|\s)\d+([.,]\d{1,2})? ?(", "|".join(currencies), r")?($|\s)"]
    )
    return pattern


def clear_user_data(user_data, conversation="all"):
    if conversation == "all":
        user_data.clear()
    elif conversation == "categories_menu":
        for key in [
            "delete_category_name", "delete_category_type", "add_category_type"
        ]:
            if key in user_data:
                del user_data[key]
