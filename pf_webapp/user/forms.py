from flask_wtf import FlaskForm
from sqlalchemy.orm import sessionmaker
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo, ValidationError

from pf_model.data_observer import get_all_telegram_id
from pf_model.exceptions import UserNotFoundOrMultipleUsers
from pf_model.model import User, db


class LoginForm(FlaskForm):
    telegram_id = StringField(
        "telegram id",
        validators=[DataRequired()],
        render_kw={"class": "form-control"}
    )
    password = PasswordField(
        "Пароль",
        validators=[DataRequired()],
        render_kw={"class": "form-control"}
    )
    remember_me = BooleanField(
        "Запомнить меня",
        default=True,
        render_kw={"class": "form-check-input"}
    )
    submit = SubmitField("Войти", render_kw={"class": "btn btn-primary"})


class RegistrationForm(FlaskForm):
    telegram_id = StringField(
        "telegram id",
        validators=[DataRequired()],
        render_kw={"class": "form-control"}
    )
    bot_code = StringField(
        "Одноразовый код",
        validators=[DataRequired()],
        render_kw={"class": "form-control"}
    )
    password = PasswordField(
        "Пароль",
        validators=[DataRequired()],
        render_kw={"class": "form-control"}
    )
    password2 = PasswordField(
        "Повторите пароль",
        validators=[DataRequired(), EqualTo("password")],
        render_kw={"class": "form-control"}
    )
    submit = SubmitField(
        "Зарегистрироваться", render_kw={"class": "btn btn-primary"}
    )

    def validate_telegram_id(self, telegram_id):
        if telegram_id.data not in get_all_telegram_id():
            raise ValidationError(
                "Сначала вам необходимо вызвать команду /start у телеграм бота"
            )

    def validate_bot_code(self, bot_code):
        Session = sessionmaker(bind=db)
        session = Session()
        try:
            user = session.query(User).filter(
                User.telegram_id == self.telegram_id.data
            ).one()
        except UserNotFoundOrMultipleUsers:
            raise ValidationError("Указан неверный telegram id")
        if not user.check_otp(bot_code.data):
            raise ValidationError(
                "Введен неверный one-time code, повторите ввод, или получите у \
                бота новый"
            )
