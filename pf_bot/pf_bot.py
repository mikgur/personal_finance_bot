import logging

from telegram.ext import (
    CommandHandler, Filters, MessageHandler, RegexHandler, Updater
)

import settings
from pf_bot import handlers
from pf_bot.handlers import categories_menu
from pf_bot.utils import AMOUNT_PATTERN, main_menu, make_re_template_for_menu


def run_bot():
    my_bot = Updater(settings.API_KEY, request_kwargs=settings.PROXY)

    dp = my_bot.dispatcher

    dp.add_handler(CommandHandler("start", handlers.start_chat))
    dp.add_handler(CommandHandler("send_otp", handlers.send_otp))
    # If message contains amount in a correct format (e.g. '100,23',
    # '50.23', '50.2') - Will try to parse and add a transaction
    dp.add_handler(
        MessageHandler(
            Filters.regex(AMOUNT_PATTERN), handlers.add_transaction
        )
    )
    dp.add_handler(categories_menu.conversation)
    dp.add_handler(
        RegexHandler(
            make_re_template_for_menu(main_menu.statistics),
            handlers.show_statistics
        )
    )
    my_bot.start_polling()
    logging.info("pf_bot started...")
    my_bot.idle()
