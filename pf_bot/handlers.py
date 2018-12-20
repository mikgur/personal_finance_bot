import logging

from pf_model import data


def start_chat(bot, update, user_data):
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
