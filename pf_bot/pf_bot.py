import logging

from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

import settings
from pf_bot import utils
from pf_bot.handlers import add_transaction, start_chat


def run_bot():
    my_bot = Updater(settings.API_KEY,
                     request_kwargs=settings.PROXY)

    dp = my_bot.dispatcher
    dp.add_handler(CommandHandler("start", start_chat))
    # If message contains amount in a correct format (e.g. '100,23', '50.23', '50.2')
    # Will try to parse and add a transaction
    dp.add_handler(MessageHandler(Filters.regex(utils.AMOUNT_PATTERN), add_transaction))
    my_bot.start_polling()
    logging.debug("pf_bot started...")
    my_bot.idle()
