import datetime

from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user

from pf_model import data_observer

blueprint = Blueprint("transaction", __name__, url_prefix="/transaction")


@blueprint.route("/", methods=["POST", "GET"])
def index():
    if not current_user.is_authenticated:
        return redirect(url_for("user.login"))
    user_id = current_user.user_id
    title = "Расходы"
    today = datetime.date.today()
    first_day_of_month = datetime.date(today.year, today.month, 1)
    period = (first_day_of_month, today)
    transactions = data_observer.get_list_of_transactions(user_id,
                                                          period=period
                                                          )
    return render_template(
        "transaction/index.html",
        title=title,
        transaction_list=transactions,
        period=period
    )
