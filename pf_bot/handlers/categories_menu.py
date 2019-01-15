import logging
from collections import namedtuple

from telegram.ext import (ConversationHandler, Filters, MessageHandler,
                          RegexHandler)

from pf_bot.exceptions import PFBCategoryAlreadyExist, PFBCategoryTypeNotInUserData
from pf_bot.utils import (clear_user_data, get_keyboard,
                          get_keyboard_from_list, make_re_template_for_menu)
from pf_model import data_manipulator, data_observer

Menu = namedtuple("Menu", ["expense_add", "expense_remove", "income_add", "income_remove", "back"])
action_choices = Menu("Расходы – Добавить категорию",
                      "Расходы – Удалить категорию",
                      "Доходы – Добавить категорию",
                      "Доходы – Удалить категорию",
                      "Назад")


def start(bot, update):
    update.message.reply_text("выбери, что именно нужно сделать",
                              reply_markup=get_keyboard_from_list(list(action_choices),
                                                                  cancel=False,
                                                                  one_time_keyboard=True)
                              )
    return "menu_choice"


def menu_choice(bot, update, user_data):
    clear_user_data(user_data, "categories_menu")
    user = update.message.from_user
    choice = update.message.text
    if choice == action_choices.back:
        update.message.reply_text(f"{user.first_name}, слушаю тебя", reply_markup=get_keyboard("main_menu"))
        clear_user_data(user_data, "categories_menu")
        return ConversationHandler.END

    category_type = "income" if choice in [action_choices.income_add, action_choices.income_remove] else "expense"
    action = "add" if choice in [action_choices.income_add, action_choices.expense_add] else "remove"

    categories = data_observer.get_all_category_names(user.id, category_type)
    if action == "remove":
        user_data["delete_category_type"] = category_type
        reply_text = "выберите категорию, которую хотите удалить:"
        update.message.reply_text(reply_text, reply_markup=get_keyboard_from_list(categories, one_time_keyboard=True))
        return "delete_category"
    elif action == "add":
        user_data["add_category_type"] = category_type
        update.message.reply_text("какое название будет у новой категории?")
        return "add_category"


def add_category(bot, update, user_data):
    user = update.message.from_user
    new_category = update.message.text.capitalize()

    try:
        if "add_category_type" not in user_data:
            raise PFBCategoryTypeNotInUserData
        category_added = data_manipulator.add_category(new_category, user.id, user_data["add_category_type"])

    except PFBCategoryTypeNotInUserData:
        logging.debug("add_category: category_type is not defined!")
        update.message.reply_text("не получается определить тип категории, выбери еще раз желаемое действие",
                                  reply_markup=get_keyboard("main_menu"))
        clear_user_data(user_data, "categories_menu")
        return ConversationHandler.END

    except PFBCategoryAlreadyExist:
        reply_text = "Такая категория уже существует, кстати, вот список всех категорий, которые у тебя есть:"

        for i, category in enumerate(sorted(data_observer.get_all_category_names(user.id,
                                                                                 user_data["add_category_type"],
                                                                                 status="active"))):
            reply_text = f"{reply_text}\n{i+1}. {category}"

        reply_text = f"{reply_text}\n Введи другое название"
        update.message.reply_text(reply_text)
        return "add_category"

    if category_added:
        reply_text = f"Категория {new_category} добавлена!"
    else:
        reply_text = f"Не получилось добавить категорию {new_category}"
    update.message.reply_text(reply_text, reply_markup=get_keyboard("main_menu"))
    clear_user_data(user_data, "categories_menu")
    return ConversationHandler.END


def delete_category(bot, update, user_data):
    user = update.message.from_user
    category_name = update.message.text
    #  Something goes wrong and we don't know category_type
    if "delete_category_type" not in user_data:
        logging.info("category_type is not defined!")
        update.message.reply_text("не получается определить тип категории, выбери еще раз желаемое действие",
                                  reply_markup=get_keyboard("main_menu"))
        clear_user_data(user_data, "categories_menu")
        return ConversationHandler.END

    #  User decided to cancel
    if category_name == action_choices.back:
        clear_user_data(user_data, "categories_menu")
        update.message.reply_text("выбери, что именно нужно сделать",
                                  reply_markup=get_keyboard_from_list(list(action_choices),
                                                                      cancel=False,
                                                                      one_time_keyboard=True)
                                  )
        return "menu_choice"

    #  Get necessary information and check whether the category_name is correct. In case everythin is ok
    #  ask for confirmation
    categories = data_observer.get_all_category_names(user.id, user_data["delete_category_type"])
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
    user = update.message.from_user
    choice = update.message.text
    #  Lets check whether everything is correct (category_name and category_type)
    if "delete_category_name" in user_data and "delete_category_type" in user_data:
        #  We know category_name and category_type
        category_name = user_data["delete_category_name"]
        category_type = user_data["delete_category_type"]

        #  user confirmed that he want to delete category
        if choice.lower() == confirmation.yes.lower():
            if data_manipulator.delete_category(user.id, category_name, category_type):
                logging.info(f"category {category_name} deleted")
                reply_text = f"категория {category_name} удалена! Что дальше?"
            else:
                logging.info(f"couldn't delete category {category_name}")
                reply_text = f"не получилось удалить категорию {category_name}"
            update.message.reply_text(reply_text, reply_markup=get_keyboard("main_menu"))
            clear_user_data(user_data, "categories_menu")
            return ConversationHandler.END

        #  user cancel
        elif choice.lower() == confirmation.no.lower():
            reply_text = "выберите категорию, которую хотите удалить:"
            categories = data_observer.get_all_category_names(user.id, user_data["delete_category_type"])
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
            logging.info("delete_category_type is not in user_data")
            update.message.reply_text("не получается определить категорию, выбери еще раз желаемое действие",
                                      reply_markup=get_keyboard("main_menu"))
            clear_user_data(user_data, "categories_menu")
            return ConversationHandler.END


conversation = ConversationHandler(
        entry_points=[
            RegexHandler(make_re_template_for_menu([main_menu.categories]), start)
        ],
        states={
            "menu_choice": [RegexHandler(make_re_template_for_menu(list(action_choices)),
                                         menu_choice,
                                         pass_user_data=True)
                            ],
            "delete_category": [MessageHandler(Filters.text, delete_category, pass_user_data=True)],
            "confirm_delete_category": [MessageHandler(Filters.text, confirm_delete_category, pass_user_data=True)],
            "add_category": [MessageHandler(Filters.text, add_category, pass_user_data=True)]
        },
        fallbacks=[]
    )
