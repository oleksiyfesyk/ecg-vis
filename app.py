# Import required libraries
import os
from random import randint

import plotly.plotly as py
from plotly.graph_objs import *

import flask
import dash
from dash.dependencies import Input, Output, State, Event
import dash_core_components as dcc
import dash_html_components as html

# From upload example
import dash_table_experiments as dt
import pandas as pd
import io


# Setup the app
# Make sure not to change this file name or the variable names below,
# the template is configured to execute 'server' on 'app.py'
server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, server=server)


# Put your Dash code here

app.layout = html.Div([
    html.H1('Dash'),
    dcc.Upload(id='upload'),
    dt.DataTable(
        id='datatable',
        rows=[{}]
    ),
], className="container")

@app.callback(
    Output('datatable', 'rows'),
    [Input('upload', 'contents')])
def update_figure(content):
    if not content:
        return []
    dff = pd.read_csv(io.StringIO(content))
    return dff.to_dict('records')

app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})


# Run the Dash app
if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)
