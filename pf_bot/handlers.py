import logging

import pf_bot.utils as utils
from pf_bot.exceptions import PFBNoCurrencies, PFBWrongCategory
from pf_model import data


def start_chat(bot, update):
    logging.debug("start_chat")
    user = update.message.from_user
    text = f"Привет, {user.first_name},"
    if data.is_existing_user(user.id):
        text = f"{text} слушаю тебя"
    else:
        text = f"{text} я помогу тебе управлять личными финансами. \
Для начала я заведу тебе несколько стандартных категорий, пару кошельков и вид дохода - Зарплата"
        data.add_user(user.id, user.first_name)

        text = f"{text}\n\nТвои категории расходов:"
        for i, category in enumerate(sorted(data.get_all_category_names(user.id))):
            text = f"{text}\n{i+1}. {category}"

        text = f"{text}\n\nТвои счета:"
        for i, account in enumerate(sorted(data.get_all_account_names(user.id))):
            text = f"{text}\n{i+1}. {account}"

    update.message.reply_text(text)


def add_transaction(bot, update):
    user = update.message.from_user
    try:
        transaction = utils.parse_transaction(update.message.text, user.id)
        data.add_transaction(transaction, user.id)
        update.message.reply_text("Запись сделана!")
    except PFBNoCurrencies:
        update.message.reply_text("В базе данных не найдено ни одной валюты. Нужно добавить хотя бы одну валюту, \
перед вводом транзакций")
    except PFBWrongCategory:
        update.message.reply_text("Не могу распознать категорию")
