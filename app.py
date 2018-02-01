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
import base64
import io

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
	dcc.Upload(
		id='upload-dat',
		children=html.Div([
			'Drag and Drop or ',
			html.A('Select DAT File')
		]),
		style={
			'width': '100%',
			'height': '60px',
			'lineHeight': '60px',
			'borderWidth': '1px',
			'borderStyle': 'dashed',
			'borderRadius': '5px',
			'textAlign': 'center',
			'margin': '10px'
		},
		multiple=False
	),
	dcc.Upload(
		id='upload-hea',
		children=html.Div([
			'Drag and Drop or ',
			html.A('Select HEA File')
		]),
		style={
			'width': '100%',
			'height': '60px',
			'lineHeight': '60px',
			'borderWidth': '1px',
			'borderStyle': 'dashed',
			'borderRadius': '5px',
			'textAlign': 'center',
			'margin': '10px'
		},
		multiple=False
	),
	dcc.Graph(id='my-graph')
], className="container")

@app.callback(Output('my-graph', 'figure'), [Input('upload-dat', 'contents'), Input('upload-hea', 'contents')])
def update_graph(upload_dat, upload_hea):
	
	record_dat = io.StringIO(base64.b64decode(upload_dat))
	record_hea = io.StringIO(base64.b64decode(upload_hea))
	
	record = wfdb.rdsamp(record_dat, record_hea, sampto = 1024) #2^10
	
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
	return tls.mpl_to_plotly(wfdb.plotrec(record, title='Record ' + selected_dropdown_value + ' from MIT-BIH Arrhythmia Database (Mean = ' + str(mean) + ' ms, SD = ' + str(sd) + ' ms)', timeunits = 'seconds', figsize = (15,7), returnfig = True, ecggrids = 'all'))



app.scripts.config.serve_locally = True
app.css.append_css({
    'external_url': (
	'https://cdn.rawgit.com/plotly/dash-app-stylesheets/96e31642502632e86727652cf0ed65160a57497f/dash-hello-world.css'
    )
})


if __name__ == '__main__':
    app.run_server()