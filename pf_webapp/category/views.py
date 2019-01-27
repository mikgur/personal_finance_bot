import json

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user

from pf_model import data_manipulator, data_observer
from pf_model.exceptions import CategoryAlreadyExist

blueprint = Blueprint("category", __name__, url_prefix="/category")


@blueprint.route("/", methods=["POST", "GET"])
def index():
    if not current_user.is_authenticated:
        return redirect(url_for("user.login"))
    user_id = current_user.user_id
    user_name = current_user.user_name
    return render_template(
        "category/index.html",
        active_info="Categories",
        user_name=user_name,
        categories_list=sorted(data_observer.get_all_category_names(user_id))
    )


@blueprint.route("/delete_category", methods=["POST"])
def delete_category():
    if not current_user.is_authenticated:
        return redirect(url_for("user.login"))
    user_id = current_user.user_id
    category_to_delete = request.get_json()
    result = data_manipulator.delete_category(
        user_id, category_to_delete, "expense"
    )
    return "success" if result else "failure"


@blueprint.route("/add_new_category", methods=["POST"])
def add_new_category():
    if not current_user.is_authenticated:
        return redirect(url_for("user.login"))
    user_id = current_user.user_id
    new_category = request.get_json()
    try:
        result = data_manipulator.add_category(
            new_category, user_id, "expense"
        )
    except CategoryAlreadyExist:
        return "already_exist"
    return "success" if result else "failure"


@blueprint.route("/rename_category", methods=["POST"])
def rename_category():
    if not current_user.is_authenticated:
        return redirect(url_for("user.login"))
    user_id = current_user.user_id
    category = request.get_json()
    try:
        data_manipulator.rename_category(
            user_id, category["new"], category["old"], "expense"
        )
    except CategoryAlreadyExist:
        return "already_exist"
    except Exception:
        return "failure"
    return "success"


@blueprint.route("/update")
def update():
    if not current_user.is_authenticated:
        return redirect(url_for("user.login"))
    user_id = current_user.user_id
    categories_list = sorted(data_observer.get_all_category_names(user_id))
    return json.dumps(categories_list)
