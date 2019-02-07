import logging

import dash
import dash_html_components as html
from flask import Flask, render_template
from flask_login import LoginManager
from sqlalchemy.orm import sessionmaker

from pf_model.model import User, db
from pf_webapp.account.views import blueprint as account_blueprint
from pf_webapp.category.views import blueprint as category_blueprint
from pf_webapp.report.views import blueprint as report_blueprint
from pf_webapp.transaction.views import blueprint as transaction_blueprint
from pf_webapp.user.views import blueprint as user_blueprint


logging.basicConfig(
    format='%(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='pf_webapp.log'
)
logging.debug("Starting pf_webapp")


def create_apps():
    app = Flask(__name__)
    app.config.from_pyfile("config.py")

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'user.login'

    @login_manager.user_loader
    def load_user(user_id):
        Session = sessionmaker(bind=db)
        session = Session()
        return session.query(User).filter(User.id == user_id).one()

    app.register_blueprint(account_blueprint)
    app.register_blueprint(category_blueprint)
    app.register_blueprint(report_blueprint)
    app.register_blueprint(transaction_blueprint)
    app.register_blueprint(user_blueprint)

    @app.route("/", methods=["GET", "POST"])
    def index():
        return render_template("category/index.html")

    # creating a Dash app
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    dash_app = dash.Dash(__name__, server=app,
                         external_stylesheets=external_stylesheets,
                         url_base_pathname='/dash/')

    dash_app.layout = html.H1(children='Hello Dash')

    return app, dash_app


app, dash_app = create_apps()
