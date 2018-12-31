import logging

from telegram.ext import (ConversationHandler, Filters, MessageHandler,
                          RegexHandler)

from pf_bot.utils import (clear_user_data, get_keyboard,
                          get_keyboard_from_list, make_re_template_for_menu)
from pf_model import data

action_choices = [
                 "Расходы - Добавить категорию",
                 "Расходы - Удалить категорию",
                 "Доходы - Добавить категорию",
                 "Доходы - Удалить категорию",
                 "Назад"
]


def start(bot, update):
    logging.info("start categories_menu conversation")
    update.message.reply_text("выбери, что именно нужно сделать",
                              reply_markup=get_keyboard("categories_menu", one_time_keyboard=True)
                              )
    return "menu_choice"


def menu_choice(bot, update, user_data):
    logging.info("categories_menu menu_choice")
    user = update.message.from_user
    choice = update.message.text
    if choice == "Назад":
        update.message.reply_text(f"{user.first_name}, слушаю тебя", reply_markup=get_keyboard("main_menu"))
        clear_user_data(user_data, "categories_menu")
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
        clear_user_data(user_data, "categories_menu")
        return ConversationHandler.END


def delete_category(bot, update, user_data):
    logging.info("categories_menu delete_category")
    user = update.message.from_user
    category_name = update.message.text
    #  Something goes wrong and we don't know category_type
    if "delete_category_type" not in user_data:
        logging.debug("delete_category: category_type is not defined!")
        update.message.reply_text("не получается определить тип категории, выбери еще раз желаемое действие",
                                  reply_markup=get_keyboard("main_menu"))
        clear_user_data(user_data, "categories_menu")
        return ConversationHandler.END

    #  User decided to cancel
    if category_name == "Назад":
        clear_user_data(user_data, "categories_menu")
        update.message.reply_text("выбери, что именно нужно сделать",
                                  reply_markup=get_keyboard("categories_menu", one_time_keyboard=True)
                                  )
        return "menu_choice"

    #  Get necessary information and check whether the category_name is correct. In case everythin is ok
    #  ask for confirmation
    categories = data.get_all_category_names(user.id, user_data["delete_category_type"])
    if category_name in categories:
        user_data["delete_category_name"] = category_name
        update.message.reply_text(f"уверен, что хочешь удалить {category_name}?",
                                  reply_markup=get_keyboard("confirmation", one_time_keyboard=True))
        return "confirm_delete_category"
    else:
        update.message.reply_text(f"не могу найти {category_name}, выбери категорию при помощи клавиатуры",
                                  reply_markup=get_keyboard_from_list(categories, one_time_keyboard=True))
        return "delete_category"


def confirm_delete_category(bot, update, user_data):
    logging.info("categories_menu confirm_delete_category")
    user = update.message.from_user
    choice = update.message.text
    #  Lets check whether everything is correct (category_name and category_type)
    if "delete_category_name" in user_data and "delete_category_type" in user_data:
        #  We know category_name and category_type
        category_name = user_data["delete_category_name"]
        category_type = user_data["delete_category_type"]

        #  user confirmed that he want to delete category
        if choice.lower() == "да":
            if data.delete_category(user.id, category_name, category_type):
                reply_text = f"категория {category_name} удалена! Что дальше?"
            else:
                reply_text = f"не получилось удалить категорию {category_name}"
            update.message.reply_text(reply_text, reply_markup=get_keyboard("main_menu"))
            clear_user_data(user_data, "categories_menu")
            return ConversationHandler.END

        #  user cancel
        elif choice.lower() == "нет":
            reply_text = "выберите категорию, которую хотите удалить:"
            categories = data.get_all_category_names(user.id, user_data["delete_category_type"])
            update.message.reply_text(reply_text,
                                      reply_markup=get_keyboard_from_list(categories, one_time_keyboard=True)
                                      )
            return "delete_category"
        #  user reply is neither yes nor no - wrong answer
        else:
            category_name = user_data["delete_category_name"]
            reply_text = f"не понимаю твой ответ. Ты уверен, что хочешь удалить категорию {category_name}?"
            update.message.reply_text(reply_text, reply_markup=get_keyboard("confirmation", one_time_keyboard=True))
            return "confirm_delete_category"
    else:
            update.message.reply_text("не получается определить категорию, выбери еще раз желаемое действие",
                                      reply_markup=get_keyboard("main_menu"))
            clear_user_data(user_data, "categories_menu")
            return ConversationHandler.END


conversation = ConversationHandler(
        entry_points=[
            RegexHandler(make_re_template_for_menu(["Категории"]), start)
        ],
        states={
            "menu_choice": [RegexHandler(make_re_template_for_menu(action_choices), menu_choice, pass_user_data=True)],
            "delete_category": [MessageHandler(Filters.text, delete_category, pass_user_data=True)],
            "confirm_delete_category": [MessageHandler(Filters.text, confirm_delete_category, pass_user_data=True)]
        },
        fallbacks=[]
    )
