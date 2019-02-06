from io import BytesIO

import pandas as pd
import matplotlib
matplotlib.use("Agg")  # NOQA
import seaborn as sns

from pf_bot.utils import get_keyboard, month_edges, parse_transaction
from pf_model import data_manipulator, data_observer
from pf_model.exceptions import NoCurrencies, WrongCategory
from pf_model.utils import is_existing_user
import utils


def send_otp(bot, update):
    utils.send_otp(update.message.from_user.username)


def start_chat(bot, update):
    user = update.effective_user
    text = f"Привет, {user.first_name},"
    if is_existing_user(user.id):
        text = f"{text} слушаю тебя"
    else:
        text = f"{text} я помогу тебе управлять личными финансами. Для начала \
я заведу тебе несколько стандартных категорий, пару кошельков и вид \
дохода - Зарплата"

        data_manipulator.add_user(user.id, user.first_name, user.username)

        text = f"{text}\n\nТвои категории расходов:"
        for i, category in enumerate(
            sorted(data_observer.get_all_category_names(user.id))
        ):
            text = f"{text}\n{i+1}. {category}"

        text = f"{text}\n\nТвои счета:"
        for i, account in enumerate(
            sorted(data_observer.get_all_account_names(user.id))
        ):
            text = f"{text}\n{i+1}. {account}"

    update.message.reply_text(text, reply_markup=get_keyboard())


def add_transaction(bot, update):
    user = update.message.from_user
    try:
        transaction = parse_transaction(update.message.text, user.id)
        data_manipulator.add_transaction(transaction, user.id)
        update.message.reply_text("Запись сделана!")
    except NoCurrencies:
        update.message.reply_text(
            "В базе данных не найдено ни одной валюты. Нужно добавить хотя бы \
            одну валюту, перед вводом транзакций"
        )
    except WrongCategory:
        update.message.reply_text("Не могу распознать категорию")


def show_statistics(bot, update):
    user = update.message.from_user

    reply_text = "Вот статистика расходов в текущем месяце:\n "
    for expense in data_observer.statistics_for_period_by_category(
        user.id, month_edges()
    ):
        amount = f"{expense[0]:,.0f}".replace(",", " ")
        reply_text = "\n".join([reply_text, f"{expense[1]} - {amount}"])

    reply_text = "\n \n".join(
        [reply_text, f"Твои расходы в прошлом месяце:\n "]
    )
    for expense in data_observer.statistics_for_period_by_category(
        user.id, month_edges(1)
    ):
        amount = f"{expense[0]:,.0f}".replace(",", " ")
        reply_text = "\n".join([reply_text, f"{expense[1]} - {amount}"])

    update.message.reply_text(reply_text)

    #  Send the barplot with statistics
    current_data = data_observer.statistics_for_period_by_category(
        user.id, month_edges()
    )
    df_current = pd.DataFrame(current_data, columns=['Amount', 'Category'])
    df_current['Month'] = 'Current'

    previous_data = data_observer.statistics_for_period_by_category(
        user.id, month_edges(1)
    )
    df_previous = pd.DataFrame(previous_data, columns=['Amount', 'Category'])
    df_previous['Month'] = 'Previous'

    data = pd.concat([df_current, df_previous])
    sns.set_style("darkgrid")
    sns.set_context("notebook", font_scale=1.5)
    sns.set_palette("deep")
    plot = sns.barplot(x="Category", y="Amount", hue="Month", data=data)
    plot.set_xlabel("")
    imgdata = BytesIO()
    plot.figure.savefig(imgdata, format="png")
    plot.clear()
    imgdata.seek(0)
    bot.send_photo(chat_id=update.message.chat_id, photo=imgdata)
