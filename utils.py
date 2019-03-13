import calendar
import datetime
from random import randint

from telegram import Bot
from telegram.utils.request import Request

import settings
from pf_model import data_observer, data_manipulator


def send_otp(telegram_id):
    code = randint(*settings.CODE_RANGE)
    # Get chat_id for telegram_id from database
    chat_id = data_observer.get_user_chat_id(telegram_id)

    # Save code hash to database
    data_manipulator.set_otp_for_user(telegram_id, code)

    # Send code to telegram user
    request = Request(
        proxy_url=settings.PROXY["proxy_url"],
        urllib3_proxy_kwargs=settings.PROXY["urllib3_proxy_kwargs"]
    )
    bot = Bot(settings.API_KEY, request=request)
    bot.sendMessage(chat_id=chat_id, text=code)


def get_current_month():
    today = datetime.date.today()
    first_day_of_month = datetime.date(today.year, today.month, 1)
    return {"name": calendar.month_name[today.month],
            "period": [first_day_of_month, today]}


def get_last_month():
    today = datetime.date.today()
    first = today.replace(day=1)
    lastMonth = first - datetime.timedelta(days=1)
    first_day = datetime.date(lastMonth.year, lastMonth.month, 1)
    number_of_days = calendar.monthrange(lastMonth.year, lastMonth.month)[1]
    last_day = datetime.date(lastMonth.year, lastMonth.month, number_of_days)
    return {"name": calendar.month_name[last_day.month],
            "period": [first_day, last_day]}


def json_date_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))
