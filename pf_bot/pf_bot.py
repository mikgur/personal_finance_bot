import logging

from telegram.ext import Updater, CommandHandler

from pf_bot.handlers import start_chat
import settings


def run_bot():
    my_bot = Updater(settings.API_KEY,
                     request_kwargs=settings.PROXY)

    dp = my_bot.dispatcher
    dp.add_handler(CommandHandler("start", start_chat, pass_user_data=True))
    my_bot.start_polling()
    logging.debug("pf_bot started...")
    my_bot.idle()
