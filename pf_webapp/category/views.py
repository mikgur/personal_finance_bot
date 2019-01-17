from flask import Blueprint, render_template

from pf_model import data_observer

blueprint = Blueprint("category", __name__, url_prefix="/category")


@blueprint.route("/", methods=["POST", "GET"])
def index():
    user_id = 10179437
    user_name = "Mikhail"
    return render_template("category/index.html",
                           active_info="Categories",
                           user_name=user_name,
                           categories_list=data_observer.get_all_category_names(user_id)
                           )


@blueprint.route("/changebtn")
def changebtn():
    return "success"
