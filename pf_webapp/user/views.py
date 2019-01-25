from flask import Blueprint, render_template, request

from pf_model.exceptions import UserNotFoundOrMultipleUsers
from pf_webapp.user.forms import LoginForm, RegistrationForm
from utils import send_otc

blueprint = Blueprint("user", __name__, url_prefix="/user")


@blueprint.route("/login")
def login():
    login_form = LoginForm()
    return render_template("user/login.html", form=login_form)


@blueprint.route("/process-login", methods=["POST"])
def process_login():
    return "Success"


@blueprint.route("/register")
def register():
    registration_form = RegistrationForm()
    return render_template("user/register.html", form=registration_form)


@blueprint.route("/process-reg", methods=["POST"])
def process_reg():
    return "Success"


@blueprint.route("/request-otc", methods=["POST"])
def request_otc():
    try:
        send_otc(request.get_json())
    except UserNotFoundOrMultipleUsers:
        return "Wrong_telegram_id"
    return "Success"
