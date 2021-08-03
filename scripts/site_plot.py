import pickle
import pandas
from urllib.request import urlopen
import json
import numpy as np
import osmnx as ox
import argparse
import os
import pandas as pd
#df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
#                   dtype={"fips": str})

import plotly.express as px
import plotly.graph_objects as go
from radxupsite import utils
import sys

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



site_data= pickle.load(open('distance_analysis.pk','rb'))


lines=[]
lon=[]
lat=[]


for county in site_data:
    graph_file=utils.get_county_graphdata('oregon',county)
    graph=pickle.load(open(graph_file,'rb'))
    points=[]
    for site in site_data[county]:
        for route in site['routes']:
            _p=node_list_to_path(graph,route)
            vals=list(reversed(_p))+_p
            points+=vals
        lines.append(points)
        lon.append(float(site['long']))
        lat.append(float(site['lat']))

demo_data=pd.DataFrame()
demo_data['latitude']=lat
demo_data['longitude']=lon

        
fig = px.scatter_mapbox(demo_data, lat="latitude", lon='longitude',height=800)
cdict={'r':'red','g':'green','b':'blue','m':'magenta','c':'cyan','y':'yellow'}






for l in lines:
    fig.add_trace(go.Scattermapbox(
        name = "Path",
        mode = "markers",
        lon = [p[0] for p in l],
        lat = [p[1] for p in l],
        marker = {'size': 4},
        line = dict(width = 3, color = 'red')))
_count=0

#for i,d in demo_data.iterrows():
#    print(i)
#    _x,_y=d['geometry'].exterior.xy
#    fig.add_trace(go.Scattermapbox(
#        lon=list(_x),
#        lat=list(_y),
#        fill="toself",
#        marker=dict(size=0,color=cdict[route_colors[_count]],marker_opacity=0.25)
#        ))
#    _count+=1
    
# print(site_nodes)
# for sn in site_nodes:
#     fig.add_trace(
#         go.Scattermapbox(
#             name = "Source",
#             mode = "markers",
#             lon =[graph.nodes[sn]['x']],
#             lat = [graph.nodes[sn]['y']],
#             marker = {'size': 16, 'color':"seagreen"}))


    
fig.update_layout(mapbox_style="open-street-map")

html_fname="site.html"
fig.write_html(html_fname)

print(html_fname,' Generated')
