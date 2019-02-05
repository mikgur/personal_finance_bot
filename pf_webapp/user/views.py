from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from sqlalchemy.orm import sessionmaker

from pf_model.exceptions import UserNotFoundOrMultipleUsers
from pf_model.model import User, db
from pf_webapp.user.forms import LoginForm, RegistrationForm
from utils import send_otp

blueprint = Blueprint("user", __name__, url_prefix="/user")


@blueprint.route("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('category.index'))
    login_form = LoginForm()
    return render_template("user/login.html", form=login_form)


@blueprint.route("/process-login", methods=["POST"])
def process_login():
    form = LoginForm()

    if form.validate_on_submit():
        Session = sessionmaker(bind=db)
        session = Session()
        user = session.query(User).filter(
            User.telegram_id == form.telegram_id.data
        ).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for("category.index"))
    flash('Неправильный логин или пароль')
    return redirect(url_for('user.login'))


@blueprint.route("/register")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('category.index'))
    registration_form = RegistrationForm()
    return render_template("user/register.html", form=registration_form)


@blueprint.route("/process-reg", methods=["POST"])
def process_reg():
    form = RegistrationForm()

    if form.validate_on_submit():
        Session = sessionmaker(bind=db)
        session = Session()
        try:
            user = session.query(User).filter(
                User.telegram_id == form.telegram_id.data
            ).one()
        except UserNotFoundOrMultipleUsers:
            return "Wrong_telegram_id"
        user.otp = ""
        user.set_password(form.password.data)
        session.commit()
        return redirect(url_for('user.login'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(
                    f"Ошибка в поле {getattr(form, field).label.text}: {error}"
                )
        return redirect(url_for('user.register'))


@blueprint.route("/request-otp", methods=["POST"])
def request_otp():
    try:
        send_otp(request.get_json())
    except UserNotFoundOrMultipleUsers:
        return "Wrong_telegram_id"
    return "Success"


@blueprint.route("/logout")
def logout():
    logout_user()
    flash('Вы успешно разлогинились')
    return redirect(url_for('user.login'))
