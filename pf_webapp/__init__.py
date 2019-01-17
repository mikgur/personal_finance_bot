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
        return render_template("user/login.html")
        """if request.method == "POST":

            if request.form["menu_button"] == "Categories":
                user_id = 10179437
                user_name = "Mikhail"
                return render_template("category/index.html",
                                       active_info="Categories",
                                       user_name=user_name,
                                       categories_list=data_observer.get_all_category_names(user_id)
                                       )
            elif request.form["menu_button"] == "Transactions":
                return render_template("category/index.html", active_info="", categories_list=[])
            else:
                return render_template("category/index.html", active_info="", categories_list=[])
        elif request.method == 'GET':
            return render_template("category/index.html", active_info="", categories_list=[])"""

    return app
