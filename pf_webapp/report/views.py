import pandas as pd

from bokeh.embed import components
from bokeh.layouts import column
from bokeh.models import Legend
from bokeh.palettes import Category20
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.transform import dodge
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

    categories = pd.concat([df_current, df_last])['Category'].unique()
    max_amount = max(df_current['Amount'].max(), df_last['Amount'].max())
    cats = figure(x_range=categories,
                  y_range=(0, max_amount + 10000),
                  plot_height=250,
                  plot_width=1000,
                  title="Затраты в текущем месяце",
                  toolbar_location=None,
                  tooltips=[("Сумма", "@Amount")],
                  tools="")

    cats.vbar(x=dodge('Category', -0.15, range=cats.x_range),
              top='Amount',
              width=0.2,
              legend=current_month['name'],
              color="#718dbf",
              source=ColumnDataSource(df_current))

    cats.vbar(x=dodge('Category', 0.15, range=cats.x_range),
              top='Amount',
              width=0.2,
              legend=last_month['name'],
              color="#e84d60",
              source=ColumnDataSource(df_last))

    cats.xgrid.grid_line_color = None
    cats.legend.orientation = "vertical"
    cats.legend.location = "top_right"

    trends_current = plot_trends(user_id, current_month, max_amount)
    trends_last = plot_trends(user_id, last_month, max_amount)

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    script, div = components(column(cats, trends_current, trends_last))
    html = render_template(
        'report/index.html',
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources,
    )
    return encode_utf8(html)


def plot_trends(user_id, period, max_amount):
    trends = data_observer.get_categories_trends(
        user_id=user_id,
        period=period["period"]
    )

    trend_figure = figure(plot_height=250,
                          plot_width=1000,
                          x_axis_type="datetime",
                          y_range=(0, max_amount + 10000),
                          title=f"Распределение затрат в {period['name']}"
                          )
    lines = []
    for i, trend in enumerate(trends):
        trends[trend].loc[period["period"][1]] = trends[trend].iloc[-1]
        lines.append(trend_figure.step(trends[trend].index,
                                       trends[trend]['amount'],
                                       line_width=2,
                                       mode="center",
                                       color=Category20[20][i % 20]
                                       ))

    legend_items = [(trend, [line]) for (trend, line) in zip(trends, lines)]
    legend = Legend(items=legend_items, location=(0, 0))

    trend_figure.add_layout(legend, 'right')

    return trend_figure
