import logging

from pf_bot.utils import get_keyboard, parse_transaction
from pf_bot.exceptions import PFBNoCurrencies, PFBWrongCategory
from pf_model import data_manipulator
from pf_model.utils import is_existing_user


def start_chat(bot, update):
    logging.debug("start_chat")
    user = update.message.from_user
    text = f"Привет, {user.first_name},"
    if is_existing_user(user.id):
        text = f"{text} слушаю тебя"
    else:
        text = f"{text} я помогу тебе управлять личными финансами. \
Для начала я заведу тебе несколько стандартных категорий, пару кошельков и вид дохода - Зарплата"
        data_manipulator.add_user(user.id, user.first_name)

        text = f"{text}\n\nТвои категории расходов:"
        for i, category in enumerate(sorted(data_manipulator.get_all_category_names(user.id))):
            text = f"{text}\n{i+1}. {category}"

        text = f"{text}\n\nТвои счета:"
        for i, account in enumerate(sorted(data_manipulator.get_all_account_names(user.id))):
            text = f"{text}\n{i+1}. {account}"

    update.message.reply_text(text, reply_markup=get_keyboard())


def add_transaction(bot, update):
    user = update.message.from_user
    try:
        transaction = parse_transaction(update.message.text, user.id)
        data_manipulator.add_transaction(transaction, user.id)
        update.message.reply_text("Запись сделана!")
    except PFBNoCurrencies:
        update.message.reply_text("В базе данных не найдено ни одной валюты. Нужно добавить хотя бы одну валюту, \
перед вводом транзакций")
    except PFBWrongCategory:
        update.message.reply_text("Не могу распознать категорию")
