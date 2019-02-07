import json

from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user

from pf_model import data_manipulator, data_observer
from utils import get_current_month

blueprint = Blueprint("transaction", __name__, url_prefix="/transaction")


@blueprint.route("/", methods=["POST", "GET"])
def index():
    if not current_user.is_authenticated:
        return redirect(url_for("user.login"))
    user_id = current_user.user_id
    title = "Транзакции - Расходы"
    period = get_current_month()

    transactions = data_observer.get_list_of_transactions(
        user_id,
        period=period["period"]
    )
    return render_template(
        "transaction/index.html",
        title=title,
        transaction_list=sorted(transactions,
                                key=lambda tr: tr['date'],
                                reverse=True),
        period=period["period"]
    )


@blueprint.route("/update", methods=["POST"])
def update():
    if not current_user.is_authenticated:
        return redirect(url_for("user.login"))
    user_id = current_user.user_id

    filters = request.get_json()

    if filters:
        pass

    transactions = data_observer.get_list_of_transactions(user_id,
                                                          period=filters
                                                          )
    return json.dumps(sorted(transactions, 
                             key=lambda tr: tr['date'],
                             reverse=True))


@blueprint.route("/delete_transaction", methods=["POST"])
def delete_transaction():
    if not current_user.is_authenticated:
        return redirect(url_for("user.login"))
    user_id = current_user.user_id
    transaction = request.get_json()
    result = data_manipulator.delete_transaction(user_id, transaction)
    return "success" if result else "failure"
