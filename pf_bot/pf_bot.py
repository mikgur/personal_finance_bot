import logging

from telegram.ext import (CommandHandler, Filters,
                          MessageHandler, Updater)

import settings
from pf_bot import utils
from pf_bot import handlers
from pf_bot.handlers import categories_menu


def run_bot():
    my_bot = Updater(settings.API_KEY,
                     request_kwargs=settings.PROXY)

    dp = my_bot.dispatcher

    dp.add_handler(CommandHandler("start", handlers.start_chat))
    # If message contains amount in a correct format (e.g. '100,23', '50.23', '50.2')
    # Will try to parse and add a transaction
    dp.add_handler(MessageHandler(Filters.regex(utils.AMOUNT_PATTERN), handlers.add_transaction))
    dp.add_handler(categories_menu.conversation)
    my_bot.start_polling()
    logging.debug("pf_bot started...")
    my_bot.idle()
