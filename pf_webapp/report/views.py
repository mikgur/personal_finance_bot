from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user


from bokeh.embed import server_document
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from bokeh.server.server import Server
from bokeh.themes import Theme
from tornado.ioloop import IOLoop

from bokeh.sampledata.sea_surface_temperature import sea_surface_temperature


blueprint = Blueprint("report", __name__, url_prefix="/report")


@blueprint.route("/")
def index():
    if not current_user.is_authenticated:
        return redirect(url_for("user.login"))
    script = server_document('http://localhost:5006/bkapp')
    return render_template("report/index.html",
                           script=script, template="Flask")


def modify_doc(doc):
    df = sea_surface_temperature.copy()
    source = ColumnDataSource(data=df)

    plot = figure(x_axis_type='datetime', y_range=(0, 25),
                  y_axis_label='Temperature (Celsius)',
                  title="Sea Surface Temperature at 43.18, -70.43")
    plot.line('time', 'temperature', source=source)

    def callback(attr, old, new):
        if new == 0:
            data = df
        else:
            data = df.rolling('{0}D'.format(new)).mean()
        source.data = ColumnDataSource(data=data).data

    slider = Slider(start=0, end=30,
                    value=0, step=1, title="Smoothing by N Days")
    slider.on_change('value', callback)

    doc.add_root(column(slider, plot))

    doc.theme = Theme(filename="pf_webapp/report/theme.yaml")


def bk_worker():
    # Can't pass num_procs > 1 in this configuration. If you need to run
    # multiple processes, see e.g. flask_gunicorn_embed.py
    server = Server({'/bkapp': modify_doc}, io_loop=IOLoop(),
                    allow_websocket_origin=["*"])
    # allow_websocket_origin=["localhost:8000"]
    server.start()
    server.io_loop.start()

from threading import Thread  # NOQA
Thread(target=bk_worker).start()
