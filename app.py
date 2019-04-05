import dash
import dash_core_components as dcc
import dash_html_components as html
import json
import plotly.plotly as py
import plotly.graph_objs as graph_objs

mapbox_access_token = "pk.eyJ1IjoiamFja3AiLCJhIjoidGpzN0lXVSJ9.7YK6eRwUNFwd3ODZff6JvA"

with open('chiNeighborhood.geojson') as f:
    geo = f.read()
    geojson = json.loads(geo)

data = graph_objs.Data([
    graph_objs.Scattermapbox(
        lat=[],
        lon=[],
        mode='markers',
    )
])

layout = graph_objs.Layout(
    height=600,
    autosize=True,
    hovermode='closest',
    mapbox=dict(
        layers=[
            dict(
                sourcetype = 'geojson',
                source = geojson,
                type = 'fill',
                color = 'rgba(163,22,19,0.8)'
            )
        ],
        accesstoken=mapbox_access_token,
        bearing=0,
        center=dict(
            lat=41.845,
            lon=-87.6231
        ),
        pitch=0,
        zoom=9,
        style='light'
    ),
)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': data,
            'layout': layout
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)