import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_auth
import flask
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import plotly
import wfdb
import plotly.tools as tls
import numpy as np
import sys

def increments(x):
	result = []
	for i in range(len(x) - 1):
		result.append(x[i+1] - x[i])
	return result

server = flask.Flask('app')
server.secret_key = os.environ.get('secret_key', 'secret')


# Keep this out of source code repository - save in a file or a database
#VALID_USERNAME_PASSWORD_PAIRS = [
#    ['iurii', 'iurii']
#]


app = dash.Dash('app', server=server)

#app = dash.Dash('auth', server=server)
#auth = dash_auth.BasicAuth(
#    app,
#    VALID_USERNAME_PASSWORD_PAIRS


app.scripts.config.serve_locally = False
dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-basic-latest.min.js'





app.layout = html.Div([
	html.H2('Welcome to the app'),
    html.H5('You are successfully authorized'),
    html.H1('MIT-BIH Arrhythmia Database'),
    dcc.Dropdown(
        id='my-dropdown',
        options=[
            {'label': 'Subject 1', 'value': '223'},
            {'label': 'Subject 2', 'value': '230'},
            {'label': 'Subject 3', 'value': '234'}
        ],
        value='223'
    ),
    dcc.Graph(id='my-graph')
], className="container")

@app.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value')])
def update_graph(selected_dropdown_value):

	record = wfdb.rdsamp(os.path.realpath('.') + '/sampledata/' + selected_dropdown_value, sampto = 1024) #2^10
	
	d_signal = record.adc()[:,0]
	print(d_signal, file=sys.stderr)
	
	peak_indices_detect = wfdb.processing.gqrs_detect(d_signal, fs=record.fs, adcgain=record.adcgain[0], adczero=record.adczero[0], threshold=1.0)
	print(peak_indices_detect, file=sys.stderr)
	
	min_bpm = 20
	max_bpm = 230
	min_gap = record.fs*60/min_bpm
	max_gap = record.fs*60/max_bpm
	peak_indices = wfdb.processing.correct_peaks(d_signal, peak_indices=peak_indices_detect, min_gap=min_gap, max_gap=max_gap, smooth_window=150)
	print(peak_indices, file=sys.stderr)
	
	sample = np.asarray(increments(sorted(peak_indices)), dtype=float)
	mean = round(np.mean(sample), 2)
	sd = round(np.std(sample), 3)
	return tls.mpl_to_plotly(wfdb.plotrec(record, title='Record ' + selected_dropdown_value + ' from ANSI/AAMI EC13 Database (Mean = ' + str(mean) + ' ms, SD = ' + str(sd) + ' ms)', timeunits = 'seconds', figsize = (15,7), returnfig = True, ecggrids = 'all'))



app.scripts.config.serve_locally = True
app.css.append_css({
    'external_url': (
	'https://cdn.rawgit.com/plotly/dash-app-stylesheets/96e31642502632e86727652cf0ed65160a57497f/dash-hello-world.css'
    )
})


if __name__ == '__main__':
    app.run_server()