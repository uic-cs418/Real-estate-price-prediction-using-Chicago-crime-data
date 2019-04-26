import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import json
import plotly.plotly as py
import plotly.graph_objs as graph_objs
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import csv

mapbox_access_token = "pk.eyJ1IjoiamFja3AiLCJhIjoidGpzN0lXVSJ9.7YK6eRwUNFwd3ODZff6JvA"

#Dict map betwen neighborhood and community
name_map = {'hanson park': 'belmont cragin', 
            'edgebrook': 'forest glen', 
            'old edgebrook': 'forest glen',
            'south edgebrook': 'forest glen',
            'sauganash': 'forest glen',
            'wildwood': 'forest glen',
            'belmont gardens': 'hermosa',
            'kelvyn park': 'hermosa',
            'lakeview': 'lake view',
            'the loop': 'loop',
            'new east side': 'loop',
            'south loop': 'loop',
            'dearborn park': 'near south side',
            "printer's row": 'near south side',
            'south loop nss': 'near south side',
            'prairie district': 'near south side',
            'little italy': 'near west side',
            'tri-taylor': 'near west side',
            'horner park': 'north center',
            'roscoe village': 'north center',
            'schorsch forest view': 'ohare',
            'south lawndale / little village': 'south lawndale',
            'brainerd': 'washington heights',
            'longwood manor': 'washington heights',
            'princeton park': 'washington heights',
            'east village': 'west town',
            'noble square': 'west town',
            'polish downtown': 'west town',
            'pulaski park': 'west town',
            'smith park': 'west town',
            'ukrainian village': 'west town',
            'wicker park': 'west town'}

with open('chicago_communities.geojson') as f:
    geo = f.read()
    geojson = json.loads(geo)

longs = []
lats = []
for k in range(len(geojson['features'])):
    neighborhood_coords = np.array(geojson['features'][k]['geometry']['coordinates'][0][0])
    m, M = neighborhood_coords[:, 0].min(), neighborhood_coords[:, 0].max()
    longs.append(0.5 * (m + M))
    m, M = neighborhood_coords[:, 1].min(), neighborhood_coords[:, 1].max()
    lats.append(0.5 * (m + M))

names = [geojson['features'][k]['properties']['community'].lower() for k in range(len(geojson['features']))]

# data = graph_objs.Data([
#     graph_objs.Scattermapbox(
#         lat=lats,
#         lon=longs,
#         mode='markers',
#         text=names,
#         marker=dict(size=5, color='rgb(0,0,255)'),
#         hoverinfo='text'
#     )
# ])

#Read in real estate file
realestate = []
with open('ppsf.csv', encoding='utf-16') as re_file:
    next(re_file)
    reader = csv.reader(re_file, delimiter='\t')

    for row in reader:
        realestate.append(row)

#Get list of time on slider
ticks = realestate[0][1:]

#Duplicate neighborhood 'south loop' because it belongs to both 'loop' and 'near south side'
southloop = []
for row in realestate:
    if row[0].replace('Chicago, IL - ', '').lower() == 'south loop':
        southloop = row.copy()
        break
southloop[0] = 'south loop nss'
realestate.append(southloop)

#Lowercase community names
for row in realestate:
    row[0] = row[0].replace('Chicago, IL - ', '').lower()

#Transform neighborhood name to community name
for row in realestate:
    if row[0] in name_map.keys():
        row[0] = name_map[row[0]]

#Get all community names from real estate file
communities = []
for row in realestate[1:]:
    communities.append(row[0])

#Get communities that exist both in real estate file and in geojson file
duplicate = list(set(communities).intersection(names))
duplicate.sort()

#Get headers
headers = realestate[0]
headers[0] = 'Community'

#Create data frame
re_df = pd.DataFrame(columns=headers)
for row in realestate[1:]:
    if row[0] in duplicate:
        re_df = re_df.append(pd.DataFrame([row], columns=headers), ignore_index=True)

#Cast price into float
for i in range(1, len(headers)):
    re_df[headers[i]] = pd.to_numeric(re_df[headers[i]])

#Group by neighborhood and get average price
re_df = re_df.groupby('Community', as_index=False).agg('mean')

#Get communities from geojson that in duplicate
features = []
for feature in geojson['features']:
    if feature['properties']['community'].lower() in duplicate:
        features.append(feature)

#Create geojson file that features only communities in duplicate
geo = {'type': 'FeatureCollection', 'features': features}

#Calculate centers of communities as well as get names
geo_longs = []
geo_lats = []
geo_names = []
for k in range(len(geo['features'])):
    neighborhood_coords = np.array(geo['features'][k]['geometry']['coordinates'][0][0])
    m, M = neighborhood_coords[:, 0].min(), neighborhood_coords[:, 0].max()
    geo_longs.append(0.5 * (m + M))
    m, M = neighborhood_coords[:, 1].min(), neighborhood_coords[:, 1].max()
    geo_lats.append(0.5 * (m + M))
    geo_names.append(geo['features'][k]['properties']['community'])

#graph_objs.Layout
layout = dict(
    height=550,
    autosize=True,
    hovermode='closest',
    margin = dict(r=50, l=0, t=0, b=0),
    mapbox=dict(
        layers=[
            dict(
                sourcetype = 'geojson',
                source = geojson,
                type = 'fill',
                color = 'rgba(163,22,19,0.2)'
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
    #Header of the page
    html.Div(
        html.H1(children='Chicago Real Estate and Crime'),
        style={'margin': '20px'}
    ),

    #Slider
    html.Div([
        html.P('Drag the slider to pick a month between Feb 2012 and Mar 2019'),
        dcc.Slider(
            id='month-slider',
            min=0,
            max=len(ticks)-1,
            value=len(ticks)-1,
            step=1,
            marks={i: ticks[i] for i in range(0,len(ticks),9)}
        )
    ],
    style={'width': '55%', 'display': 'inline-block', 'margin': '20px 50px'}
    ),

    html.Div([
        html.H5(id='heatmap-title', style={'margin': '20px 50px'}),

        dcc.Graph(
            id='realestate-heatmap',
            figure=dict(
                data=graph_objs.Data([
                    graph_objs.Scattermapbox(
                        lat=geo_lats,
                        lon=geo_longs,
                        mode='markers',
                        text=geo_names,
                        marker=dict(size=5, color='white', opacity=0.5),
                        hoverinfo='text'
                    )
                ]),
                # data=dict(
                #     lat=lats,
                #     lon=longs,
                #     text=geo_names,
                #     type='scattermapbox',
                #     # mode='markers',
                #     hoverinfo='text',
                #     marker=dict(size=5, color='white', opacity=0)
                # ),
                layout=dict(
                    height=550,
                    autosize=True,
                    hovermode='closest',
                    margin = dict(r=50, l=0, t=0, b=0),
                    mapbox=dict(
                        layers=[],
                        accesstoken=mapbox_access_token,
                        style='light',
                        bearing=0,
                        center=dict(
                            lat=41.845,
                            lon=-87.6231
                        ),
                        pitch=0,
                        zoom=9,
                    )
                )
            ),
            style={'width': '49%', 'display': 'inline-block', 'margin': '5px 50px'}
        ) 
    ])
])

#Get max price and min price
prices = []
for c in re_df['Community'].values:
    prices = prices + list(re_df[re_df['Community']==c].values[0][1:])
max_price = max(prices)
min_price = min(prices)


#Function to get color from price
def getColor(p):
    viridis = plt.get_cmap('viridis', 256)
    w = max_price - min_price
    val = (p - min_price)/w
    if val == 1:
        return 'rgba' + str(viridis(val - 0.000001))
    else:
        return 'rgba' + str(viridis(val))

@app.callback([Output('heatmap-title', 'children'),
            Output('realestate-heatmap', 'figure')],
            [Input('month-slider', 'value')])
def update_month_slider(input):

    data=graph_objs.Data([
        graph_objs.Scattermapbox(
            lat=geo_lats,
            lon=geo_longs,
            mode='markers',
            text=geo_names,
            marker=dict(size=5, color='white', opacity=0.5),
            hoverinfo='text'
        )
    ])

    # data = [dict(
    #     lat=geo_lats,
    #     longs=geo_longs,
    #     text=geo_names,
    #     # mode='markers',
    #     type='scattermapbox',
    #     hoverinfo='text',
    #     marker=dict(size=8, color='white', opacity=0)
    # )]

    layout=dict(
        height=550,
        autosize=True,
        hovermode='closest',
        margin = dict(r=50, l=0, t=0, b=0),
        mapbox=dict(
            layers=[],
            accesstoken=mapbox_access_token,
            style='light',
            bearing=0,
            center=dict(
                lat=41.845,
                lon=-87.6231
            ),
            pitch=0,
            zoom=9,
        )
    )

    for feature in geo['features']:
        layer = dict(
            sourcetype='geojson',
            source=feature,
            type='fill',
            color=getColor(re_df.loc[re_df['Community']==feature['properties']['community'].lower(),ticks[input]].values[0])
        )
        layout['mapbox']['layers'].append(layer)

    fig = dict(data=data, layout=layout)

    return ('Chicago Real Estate in ' + ticks[input]), fig

if __name__ == '__main__':
    app.run_server(debug=True)