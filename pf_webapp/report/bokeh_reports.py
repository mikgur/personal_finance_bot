import pandas as pd
from bokeh.layouts import column
from bokeh.models import (ColumnDataSource, DatetimeTickFormatter, Legend,
                          NumeralTickFormatter, Range1d)
from bokeh.models.layouts import Spacer
from bokeh.palettes import Category20
from bokeh.plotting import figure
from bokeh.transform import dodge

from pf_model import data_observer
from utils import get_current_month, get_last_month


def plot_balance_report(user_id):
    current_month = get_current_month()
    current_month_trends = data_observer.get_balances_trends(
        user_id,
        current_month["period"])
    current_title = f"Изменение остатков {current_month['name']}"

    last_month = get_last_month()
    last_month_trends = data_observer.get_balances_trends(
        user_id,
        last_month["period"])
    last_title = f"Изменение остатков {last_month['name']}"

    current_month_figure = make_trends_figure(current_month_trends,
                                              current_title,
                                              current_month)
    last_month_figure = make_trends_figure(last_month_trends,
                                           last_title,
                                           last_month)
    vertical_space = round(current_month_figure.plot_height * 0.1)
    return column(
                  current_month_figure,
                  Spacer(height=vertical_space),
                  last_month_figure
                  )


def plot_expense_reports(user_id):
    cats_plot = plot_categories(user_id)
    trends_current_plot = plot_expense_trends(
                            user_id,
                            get_current_month()
                            )
    trends_last_plot = plot_expense_trends(
                            user_id,
                            get_last_month()
                            )
    vertical_space = round(cats_plot.plot_height * 0.2)
    return column(cats_plot,
                  Spacer(height=vertical_space),
                  trends_current_plot,
                  Spacer(height=vertical_space),
                  trends_last_plot,
                  Spacer(height=vertical_space)
                  )


def plot_categories(user_id):
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
    cats_plot = figure(x_range=categories,
                       y_range=(0, max_amount + 10000),
                       plot_height=250,
                       plot_width=1000,
                       title="Затраты в текущем месяце",
                       toolbar_location=None,
                       tooltips=[("Сумма", "@Amount")],
                       tools="")

    cats_plot.vbar(x=dodge('Category', -0.15, range=cats_plot.x_range),
                   top='Amount',
                   width=0.2,
                   legend=current_month['name'],
                   color="#718dbf",
                   source=ColumnDataSource(df_current))

    cats_plot.vbar(x=dodge('Category', 0.15, range=cats_plot.x_range),
                   top='Amount',
                   width=0.2,
                   legend=last_month['name'],
                   color="#e84d60",
                   source=ColumnDataSource(df_last))

    cats_plot.xgrid.grid_line_color = None
    cats_plot.yaxis[0].formatter = NumeralTickFormatter(format="0,0[.]00")
    cats_plot.legend.orientation = "vertical"
    cats_plot.legend.location = "top_right"
    return cats_plot


def plot_expense_trends(user_id, period):
    trends = data_observer.get_categories_trends(
        user_id=user_id,
        period=period["period"]
    )
    return make_trends_figure(trends,
                              f"Распределение затрат в {period['name']}",
                              period)


def make_trends_figure(trends, title, period):
    trend_figure = figure(plot_height=500,
                          plot_width=1000,
                          x_axis_type="datetime",
                          x_range=(period["period"][0], period["period"][1]),
                          title=title,
                          toolbar_location=None,
                          )
    lines = []
    max_value = 0
    for i, trend in enumerate(trends):
        data_source = trends[trend]
        if max_value < data_source['amount'].max():
            max_value = data_source['amount'].max()
        lines.append(trend_figure.step(data_source.index,
                                       data_source['amount'],
                                       line_width=2,
                                       mode="after",
                                       color=Category20[20][i % 20],
                                       ))

    trend_figure.y_range = Range1d(0, max_value * 1.1)
    trend_figure.xaxis[0].formatter = DatetimeTickFormatter(days=['%d %b'])
    trend_figure.yaxis[0].formatter = NumeralTickFormatter(format="0,0[.]00")

    legend_items = [(trend, [line]) for (trend, line) in zip(trends, lines)]
    legend = Legend(items=legend_items, location=(0, 0))

    trend_figure.add_layout(legend, 'right')
    return trend_figure
