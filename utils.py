from random import randint

from telegram import Bot
from telegram.utils.request import Request

import settings
from pf_model import data_observer, data_manipulator


def send_otc(telegram_id):
    code = randint(*settings.CODE_RANGE)
    # Get chat_id for telegram_id from database
    chat_id = data_observer.get_user_chat_id(telegram_id)

    # Save code hash to database
    data_manipulator.set_otc_for_user(telegram_id, code)

    # Send code to telegram user
    request = Request(
        proxy_url=settings.PROXY["proxy_url"],
        urllib3_proxy_kwargs=settings.PROXY["urllib3_proxy_kwargs"]
    )
    bot = Bot(settings.API_KEY, request=request)
    bot.sendMessage(chat_id=chat_id, text=code)
