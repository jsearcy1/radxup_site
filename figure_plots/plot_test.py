import dash
import dash_core_components as dcc
import dash_html_components as html
from utils import read_xlsx
import pickle
import pandas
from urllib.request import urlopen
import json
import numpy as np
import osmnx as ox

import pandas as pd
#df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
#                   dtype={"fips": str})

import plotly.express as px
import plotly.graph_objects as go
import sys

county=sys.argv[1]
n_sites=sys.argv[2]



routes,route_colors,site_nodes,site_index=pickle.load(open('../flp_g_data_'+county+'_'+str(n_sites)+'_.pk','rb'))
graph,data,pop_nodes=pickle.load(open('../'+county+'_optimization_inputs.pk','rb'))
poi_points,poi_names,pois=pickle.load(open('../'+county+'_POIS.pk','rb'))

l=0
for i,r in enumerate(routes):
    l+=np.sum(
    ox.utils_graph.get_route_edge_attributes(graph, r, 'travel_time'))*data[i]
print('loss',l)


for i in site_index:
    print(i)
    print(pois[i])

def node_list_to_path(G, node_list):
    edge_nodes = list(zip(node_list[:-1], node_list[1:]))
    lines = []
    for u, v in edge_nodes:
        # if there are parallel edges, select the shortest in length
        try:data = min(G.get_edge_data(u, v).values(), 
                       key=lambda x: x['length'])        # if it has a geometry attrib
        except:
            print(u,v)
            continue
        
        if 'geometry' in data:
            # add them to the list of lines to plot
            xs, ys = data['geometry'].xy
            lines+=list(zip(xs, ys))
        else:
            # if it doesn't have a geometry attribute,
            # then the edge is a straight line from node to node
            x1 = G.nodes[u]['x']
            y1 = G.nodes[u]['y']
            x2 = G.nodes[v]['x']
            y2 = G.nodes[v]['y']
            line = [(x1, y1), (x2, y2)]
            lines+=line
    return lines

lines=[node_list_to_path(graph,r) for r in routes]


df=pandas.read_excel('../Oregon Census Block GeoCoded Data.xlsx')

df['ratio']=df['B03002e12']#/df['B03002e1']



fig = px.scatter_mapbox(df.dropna(), lat="latitude", lon='longitude',
                        size="ratio",height=800)
cdict={'r':'red','g':'green','b':'blue','m':'magenta','c':'cyan','y':'yellow'}


for l,c in zip(lines,route_colors):
    fig.add_trace(go.Scattermapbox(
        name = "Path",
        mode = "lines",
        lon = [p[0] for p in l],
        lat = [p[1] for p in l],
        marker = {'size': 4},
        line = dict(width = 4, color = cdict[c])))

print(site_nodes)
for sn in site_nodes:
    fig.add_trace(
        go.Scattermapbox(
            name = "Source",
            mode = "markers",
            lon =[graph.nodes[sn]['x']],
            lat = [graph.nodes[sn]['y']],
            marker = {'size': 16, 'color':"seagreen"}))
    
fig.update_layout(mapbox_style="open-street-map")

fig.write_html(county+"_"+str(n_sites)+'_map.html')

app = dash.Dash()
app.layout = html.Div([
    dcc.Graph(figure=fig)
])

app.run_server(host='0.0.0.0',debug=True, use_reloader=False)  # Turn off reloader if inside Jupyter

