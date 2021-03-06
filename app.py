import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_auth
#from pandas_datareader import data as web
#from datetime import datetime as dt
import flask
#import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import plotly
import wfdb
import plotly.tools as tls



server = flask.Flask('app')
server.secret_key = os.environ.get('secret_key', 'secret')


# Keep this out of source code repository - save in a file or a database
#VALID_USERNAME_PASSWORD_PAIRS = [
#    ['iurii', 'iurii']
#]


#app = dash.Dash('app', server=server)

#app = dash.Dash('auth', server=server)
#auth = dash_auth.BasicAuth(
#    app,
#    VALID_USERNAME_PASSWORD_PAIRS
#)



APP_NAME = 'Dash  App'
APP_URL = 'https://ecg-vis.herokuapp.com/'

app = dash.Dash('app', server=server)
auth = dash_auth.PlotlyAuth(
    app,
    APP_NAME,
    'private',
    APP_URL
)


app.scripts.config.serve_locally = False
dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-basic-latest.min.js'





app.layout = html.Div([
	html.H2('Welcome to the app'),
    html.H4('You are successfully authorized'),
    html.H1('MIT-BIH Arrhythmia'),
    dcc.Dropdown(
        id='my-dropdown',
        options=[
            {'label': 'Subject 100', 'value': 'aami3a'},
            {'label': 'Subject 101', 'value': 'aami3b'},
            {'label': 'Subject 102', 'value': 'aami3c'}
#			{'label': 'Subject 103', 'value': '103'},
#			{'label': 'Subject 104', 'value': '104'}
        ],
        value='aami3a'
    ),
    dcc.Graph(id='my-graph')
], className="container")

@app.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value')])
def update_graph(selected_dropdown_value):

	record = wfdb.rdsamp(os.path.realpath('.') + '/sampledata/' + selected_dropdown_value, sampto = 3500)
#	annotation = wfdb.rdann(os.path.realpath('.') + '/sampledata/' + selected_dropdown_value, 'atr', sampto = 3500)
#	annotation = annotation, 
	return tls.mpl_to_plotly(wfdb.plotrec(record, title='Record ' + selected_dropdown_value + ' from ANSI/AAMI EC13 Database', timeunits = 'seconds', figsize = (15,7), returnfig = True, ecggrids = 'all'))



app.scripts.config.serve_locally = True
app.css.append_css({
    'external_url': (
	'https://cdn.rawgit.com/plotly/dash-app-stylesheets/96e31642502632e86727652cf0ed65160a57497f/dash-hello-world.css'
    )
})


if __name__ == '__main__':
    app.run_server()