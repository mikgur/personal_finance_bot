from flask import (Blueprint, redirect,
                   url_for)
from flask_login import current_user
import dash_core_components as dcc
import dash_html_components as html

import pf_webapp

blueprint = Blueprint("report", __name__, url_prefix="/report")


@blueprint.route("/")
def index():
    if not current_user.is_authenticated:
        return redirect(url_for("user.login"))
    pf_webapp.dash_app.layout = html.Div(children=[
        html.H1(children='Hello Dash'),

        html.Div(children='''
            Dash: A web application framework for Python.
        '''),

        dcc.Graph(
            id='example-graph',
            figure={
                'data': [
                    {'x': [1, 2, 3], 'y': [4, 1, 2],
                     'type': 'bar', 'name': 'SF'},
                    {'x': [1, 2, 3], 'y': [2, 4, 5],
                     'type': 'bar', 'name': u'Montréal'},
                ],
                'layout': {
                    'title': 'Dash Data Visualization'
                }
            }
        )
    ])
    return pf_webapp.dash_app.index()
