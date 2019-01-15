from flask import Flask, render_template, request

from pf_model import data_observer


def create_app():
    app = Flask(__name__)

    @app.route("/", methods=["GET", "POST"])
    def index():
        print(request.method)
        if request.method == "POST":

            if request.form["menu_button"] == "Categories":
                user_id = 10179437
                user_name = "Mikhail"
                return render_template("index.html",
                                       active_info="Categories",
                                       user_name=user_name,
                                       categories_list=data_observer.get_all_category_names(user_id)
                                       )
            elif request.form["menu_button"] == "Transactions":
                return render_template("index.html", active_info="", categories_list=[])
            else:
                return render_template("index.html", active_info="", categories_list=[])
        elif request.method == 'GET':
            return render_template("index.html", active_info="", categories_list=[])

    return app
