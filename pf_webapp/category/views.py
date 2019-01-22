import json

from flask import Blueprint, render_template, request

from pf_model import data_observer, data_manipulator
from pf_bot.exceptions import PFBCategoryAlreadyExist

blueprint = Blueprint("category", __name__, url_prefix="/category")


@blueprint.route("/", methods=["POST", "GET"])
def index():
    user_id = 10179437
    user_name = "Mikhail"
    return render_template("category/index.html",
                           active_info="Categories",
                           user_name=user_name,
                           categories_list=sorted(data_observer.get_all_category_names(user_id))
                           )


@blueprint.route("/delete_category", methods=["POST"])
def delete_category():
    user_id = 10179437
    category_to_delete = request.get_json()
    result = data_manipulator.delete_category(user_id, category_to_delete, "expense")
    return "success" if result else "failure"


@blueprint.route("/add_new_category", methods=["POST"])
def add_new_category():
    user_id = 10179437
    new_category = request.get_json()
    try:
        result = data_manipulator.add_category(new_category, user_id, "expense")
    except PFBCategoryAlreadyExist:
        return "already_exist"
    return "success" if result else "failure"


@blueprint.route("/rename_category", methods=["POST"])
def rename_category():
    user_id = 10179437
    category = request.get_json()
    try:
        data_manipulator.rename_category(user_id, category["new"], category["old"], "expense")
    except PFBCategoryAlreadyExist:
        return "already_exist"
    except Exception:
        return "failure"
    return "success"


@blueprint.route("/update")
def update():
    user_id = 10179437
    categories_list = sorted(data_observer.get_all_category_names(user_id))
    return json.dumps(categories_list)
