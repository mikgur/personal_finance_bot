from bokeh.embed import components
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user

from pf_model import data_observer
from pf_webapp.report.bokeh_reports import (plot_balance_report,
                                            plot_expense_reports)
from utils import get_current_month, get_last_month

blueprint = Blueprint("report", __name__, url_prefix="/report")


@blueprint.route("/balances")
def balances():
    if not current_user.is_authenticated:
        return redirect(url_for("user.login"))

    user_id = current_user.user_id

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    script, div = components(plot_balance_report(user_id))
    html = render_template(
        "report/balances.html",
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources,
        title="Остатки на счетах",
        current_month=get_current_month()["name"],
        last_month=get_last_month()["name"],
        accounts_list=sorted(data_observer.get_all_account_names(user_id))
    )
    return encode_utf8(html)


@blueprint.route("/expense")
def expense():
    if not current_user.is_authenticated:
        return redirect(url_for("user.login"))

    user_id = current_user.user_id

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    script, div = components(plot_expense_reports(user_id))
    html = render_template(
        "report/expense.html",
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources,
        title="Анализ расходов"
    )
    return encode_utf8(html)
