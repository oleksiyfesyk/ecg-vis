import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import pandas as pd
import io

app = dash.Dash()

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


if __name__ == '__main__':
    app.run_server(debug=True)

