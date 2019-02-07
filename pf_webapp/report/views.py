import pandas as pd

from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from bokeh.models import ColumnDataSource
from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user

from pf_model import data_observer
from utils import get_current_month, get_last_month

blueprint = Blueprint("report", __name__, url_prefix="/report")


@blueprint.route("/")
def index():
    if not current_user.is_authenticated:
        return redirect(url_for("user.login"))

    user_id = current_user.user_id

    current_month = get_current_month()
    current_month_data = data_observer.statistics_for_period_by_category(
        user_id, current_month['period']
    )
    df_current = pd.DataFrame(current_month_data,
                              columns=['Amount', 'Category'])
    df_current['Month'] = current_month['name']

    last_month = get_last_month()
    last_month_data = data_observer.statistics_for_period_by_category(
        user_id, last_month['period']
    )
    df_last = pd.DataFrame(last_month_data, columns=['Amount', 'Category'])
    df_last['Month'] = last_month['name']

    source = ColumnDataSource(pd.concat([df_current, df_last]))

    p = figure(x_range=df_current['Category'],
               y_range=(0, df_current['Amount'].max() + 10000),
               plot_height=250,
               title="Затраты в текущем месяце",
               toolbar_location=None, tools="")

    p.vbar(x='Category',
           top='Amount',
           width=0.5,
           legend="Month",
           source=source)

    p.xgrid.grid_line_color = None
    p.legend.orientation = "horizontal"
    p.legend.location = "top_center"

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    script, div = components(p)
    html = render_template(
        'report/index.html',
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources,
    )
    return encode_utf8(html)
