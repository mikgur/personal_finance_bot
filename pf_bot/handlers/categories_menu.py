import logging

from telegram.ext import (ConversationHandler, Filters, MessageHandler,
                          RegexHandler)

from pf_bot.utils import (get_keyboard, get_keyboard_from_list,
                          make_re_template_for_menu)
from pf_model import data

action_choices = [
                 "Расходы - Добавить категорию",
                 "Расходы - Удалить категорию",
                 "Доходы - Добавить категорию",
                 "Доходы - Удалить категорию",
                 "Назад"
]


def start(bot, update):
    logging.debug("start categories_menu conversation")
    update.message.reply_text("выбери, что именно нужно сделать",
                              reply_markup=get_keyboard("categories_menu", one_time_keyboard=True)
                              )
    return "menu_choice"


def menu_choice(bot, update, user_data):
    logging.debug("categories_menu menu_choice")
    user = update.message.from_user
    choice = update.message.text
    if choice == "Назад":
        update.message.reply_text(f"{user.first_name}, слушаю тебя", reply_markup=get_keyboard("main_menu"))
        return ConversationHandler.END

    category_type, action = choice.split(" - ")
    user_data["delete_category_type"] = category_type
    categories = data.get_all_category_names(user.id, category_type)
    if action == "Удалить категорию":
        reply_text = "выберите категорию, которую хотите удалить:"
        update.message.reply_text(reply_text, reply_markup=get_keyboard_from_list(categories, one_time_keyboard=True))
        return "delete_category"
    elif action == "Добавить категорию":
        update.message.reply_text("какое название будет у новой категории?")
        return ConversationHandler.END


def delete_category(bot, update, user_data):
    user = update.message.from_user
    category_name = update.message.text
    if "delete_category_type" not in user_data:
        logging.debug("delete_category: category_type is not defined!")
        update.message.reply_text("не получается определить тип категории, выбери еще раз желаемое действие",
                                  reply_markup=get_keyboard("main_menu"))
        return ConversationHandler.END

    categories = data.get_all_category_names(user.id, user_data["delete_category_type"])
    if category_name in categories:
        print(f'Пробуем удалить категорию {category_name}')
        update.message.reply_text(f"категория {category_name} удалена", reply_markup=get_keyboard("main_menu"))
        del user_data["delete_category_type"]
        return ConversationHandler.END
    elif category_name == "Назад":
        del user_data["delete_category_type"]
        update.message.reply_text("выбери, что именно нужно сделать",
                                  reply_markup=get_keyboard("categories_menu", one_time_keyboard=True)
                                  )
        return "menu_choice"
    else:
        update.message.reply_text(f"не могу найти {category_name}, выбери категорию при помощи клавиатуры",
                                  reply_markup=get_keyboard_from_list(categories, one_time_keyboard=True))
        return "delete_category"


conversation = ConversationHandler(
        entry_points=[
            RegexHandler(make_re_template_for_menu(["Категории"]), start)
        ],
        states={
            "menu_choice": [RegexHandler(make_re_template_for_menu(action_choices), menu_choice, pass_user_data=True)],
            "delete_category": [MessageHandler(Filters.text, delete_category, pass_user_data=True)]
        },
        fallbacks=[]
    )
