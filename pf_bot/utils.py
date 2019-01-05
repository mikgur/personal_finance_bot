import logging
import re

from telegram import ReplyKeyboardMarkup

from pf_bot.exceptions import PFBNoCurrencies, PFBWrongCategory
from pf_model import data_observer

AMOUNT_PATTERN = r"(^|\s)\d+([.,]\d{1,2})?"


def get_keyboard(context="main_menu", one_time_keyboard=False):
    if context == "main_menu":
        return ReplyKeyboardMarkup([["Ввести доход/расход", "Статистика"],
                                    ["Категории", "Счета"]], resize_keyboard=True)
    elif context == "categories_menu":
        return ReplyKeyboardMarkup([["Расходы - Добавить категорию", "Расходы - Удалить категорию"],
                                    ["Доходы - Добавить категорию", "Доходы - Удалить категорию"],
                                    ["Назад"]], one_time_keyboard=one_time_keyboard, resize_keyboard=True)
    elif context == "confirmation":
        return ReplyKeyboardMarkup([["Да", "Нет"]], one_time_keyboard=one_time_keyboard, resize_keyboard=True)


def get_keyboard_from_list(names, number_of_rows=2, cancel=True, one_time_keyboard=False):
    """
    Function create a keyboard from names of categories/accounts/other list of objects
    """
    keyboard_buttons = []
    buttons = names.copy()
    if cancel:
        buttons.append('Назад')

    for num, name in enumerate(buttons):
        if num % number_of_rows == 0:
            keyboard_buttons.append([])
        keyboard_buttons[-1].append(name)
    return ReplyKeyboardMarkup(keyboard_buttons, one_time_keyboard=one_time_keyboard, resize_keyboard=True)


def make_re_template_for_menu(choices):
    return f"^({')|('.join(choices)})$"


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
    transaction_amount = transaction_amount.replace(",", ".")
    text = text.replace(transaction_amount_currency, "")

    #  Search for category
    expense_category_list = [category for category in data_observer.get_all_category_names(user_id)
                             if category.lower() in text]
    transaction_category = ""
    transaction_type = ""
    if expense_category_list:
        transaction_category = max(expense_category_list, key=len)
        text = text.replace(transaction_category, "")
        transaction_type = "expense"
    else:
        income_category_list = [category for category in data_observer.get_all_category_names(user_id, "income")
                                if category.lower() in text]
        if income_category_list:
            transaction_category = max(income_category_list, key=len)
            text = text.replace(transaction_category, "")
            transaction_type = "income"
        else:
            logging.debug("при вводе транзакции указана неверная категория")
            raise PFBWrongCategory

    # Search for account
    account_list = [account for account in data_observer.get_all_account_names(user_id) if account.lower() in text]
    transaction_account = ""
    if account_list:
        transaction_account = max(account_list, key=len)
        text = text.replace(transaction_account, "")
    else:
        transaction_account = "Наличные"  # считаем этот счет счетом по-умолчанию, далее добавим возможность выбора

    return {"amount": transaction_amount, "currency": transaction_currency, "category": transaction_category,
            "type": transaction_type, "account": transaction_account}


def amount_with_currency_pattern():
    """This pattern is used to extract amount and currency from text
    (e.g. '123.23usd', '12,4 руб')
    """
    logging.debug("building transaction pattern")
    currencies = data_observer.get_all_currencies_shortnames()
    if not currencies:
        raise PFBNoCurrencies
    currency_variants = [currency.capitalize() for currency in currencies]
    currency_variants.extend([currency.upper() for currency in currencies])
    currencies.extend(currency_variants)
    pattern = ''.join([r"(^|\s)\d+([.,]\d{1,2})? ?(", "|".join(currencies), r")?($|\s)"])
    return pattern


def clear_user_data(user_data, conversation="all"):
    if conversation == "all":
        user_data.clear()
    elif conversation == "categories_menu":
        for key in ["delete_category_name", "delete_category_type", "add_category_type"]:
            if key in user_data:
                del user_data[key]
