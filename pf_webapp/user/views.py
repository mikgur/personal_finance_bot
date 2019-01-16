from flask import Blueprint, render_template


blueprint = Blueprint("user", __name__, url_prefix="/user")

@blueprint.route("/login")
def login():
    return render_template("user/login.html")
