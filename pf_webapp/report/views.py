from bokeh.embed import components
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user

from pf_webapp.report.bokeh_reports import plot_reports

blueprint = Blueprint("report", __name__, url_prefix="/report")


@blueprint.route("/")
def index():
    if not current_user.is_authenticated:
        return redirect(url_for("user.login"))

    user_id = current_user.user_id

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    script, div = components(plot_reports(user_id))
    html = render_template(
        'report/index.html',
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources,
    )
    return encode_utf8(html)
