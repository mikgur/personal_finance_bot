from flask import Blueprint, render_template

from pf_webapp.user.forms import LoginForm, RegistrationForm

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