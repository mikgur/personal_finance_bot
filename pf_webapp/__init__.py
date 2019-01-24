from flask import Flask, render_template

from pf_webapp.category.views import blueprint as category_blueprint
from pf_webapp.user.views import blueprint as user_blueprint


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile("config.py")

    app.register_blueprint(category_blueprint)
    app.register_blueprint(user_blueprint)

    @app.route("/", methods=["GET", "POST"])
    def index():
        return render_template("category/index.html")

    return app
