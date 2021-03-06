import json

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user

from pf_model import data_manipulator, data_observer
from pf_model.exceptions import ObjectAlreadyExist
from utils import json_date_serial

blueprint = Blueprint("account", __name__, url_prefix="/account")


@blueprint.route("/", methods=["POST", "GET"])
def index():
    if not current_user.is_authenticated:
        return redirect(url_for("user.login"))
    user_id = current_user.user_id
    return render_template(
        "account/index.html",
        accounts_list=sorted(data_observer.get_all_account_names(user_id))
    )


@blueprint.route("/add_new_account", methods=["POST"])
def add_new_account():
    if not current_user.is_authenticated:
        return redirect(url_for("user.login"))
    user_id = current_user.user_id
    new_account = request.get_json()
    try:
        result = data_manipulator.add_account(
            new_account['name'], user_id, new_account['currency'],
            new_account['initial_balance']
        )
    except ObjectAlreadyExist:
        return "already_exist"
    return "success" if result else "failure"


@blueprint.route("/delete_account", methods=["POST"])
def delete_account():
    if not current_user.is_authenticated:
        return redirect(url_for("user.login"))
    user_id = current_user.user_id
    account_to_delete = request.get_json()
    result = data_manipulator.delete_account(user_id, account_to_delete)
    return "success" if result else "failure"


@blueprint.route("/edit_account", methods=["POST"])
def edit_account():
    if not current_user.is_authenticated:
        return redirect(url_for("user.login"))
    user_id = current_user.user_id
    account = request.get_json()
    try:
        data_manipulator.edit_account(user_id, account["new"], account["old"])
    except ObjectAlreadyExist:
        return "already_exist"
    except Exception:
        return "failure"
    return "success"


@blueprint.route("/get_currencies")
def get_currencies():
    return json.dumps(data_observer.get_all_currency_shortnames())


@blueprint.route("/update")
def update():
    if not current_user.is_authenticated:
        return redirect(url_for("user.login"))
    user_id = current_user.user_id
    accounts_list = sorted(data_observer.get_all_account_names(user_id))
    return json.dumps(accounts_list, default=json_date_serial)
