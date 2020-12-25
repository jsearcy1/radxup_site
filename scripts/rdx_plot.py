from utils import read_xlsx
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



parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('state', metavar='S', type=str, 
                    help='State')
parser.add_argument('county', metavar='C', type=str,
                    help='County')
parser.add_argument('nsites', metavar='N', type=int,
                    help='Number of sites to optimize for')

args = parser.parse_args()

county_data_directory=utils.get_county_data_dir(args.state,args.county)

if not os.path.exists(county_data_directory):
    raise Exception('No data available for county',args.county,' please run rdx_getdata.py')






parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('state', metavar='S', type=str, 
                    help='State')
parser.add_argument('county', metavar='C', type=str,
                    help='County')
parser.add_argument('nsites', metavar='N', type=int,
                    help='Number of sites to optimize for')

args = parser.parse_args()

county_data_directory=utils.get_county_data_dir(args.state,args.county)

if not os.path.exists(county_data_directory):
    raise Exception('No data available for county',args.county,' please run rdx_getdata.py')


demo_file=utils.get_county_demodata(args.state,args.county)
graph_file=utils.get_county_graphdata(args.state,args.county)
poi_file=utils.get_county_poidata(args.state,args.county)
n_sites=args.nsites



poi_points,poi_names,pois=pickle.load(open(poi_file,'rb'))
demo_data=pickle.load(open(demo_file,'rb'))
graph=pickle.load(open(graph_file,'rb'))
opt_file=utils.get_county_optdata(args.state,args.county,n_sites)

routes,route_colors,site_nodes,site_index=pickle.load(open(opt_file,'rb'))


l=0
for i,r in enumerate(routes):
    l+=np.sum(
    ox.utils_graph.get_route_edge_attributes(graph, r, 'travel_time'))*demo_data.iloc[i]['Population']
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


lon=[]
lat=[]

for i,d in demo_data.iterrows():
    _lon,_lat=d['geometry'].centroid.xy
    lon.append(_lon[0])
    lat.append(_lat[0])
demo_data['latitude']=lat
demo_data['longitude']=lon

fig = px.scatter_mapbox(demo_data, lat="latitude", lon='longitude',
                        size="Population",height=800)
cdict={'r':'red','g':'green','b':'blue','m':'magenta','c':'cyan','y':'yellow'}






for l,c in zip(lines,route_colors):
    fig.add_trace(go.Scattermapbox(
        name = "Path",
        mode = "lines",
        lon = [p[0] for p in l],
        lat = [p[1] for p in l],
        marker = {'size': 4},
        line = dict(width = 4, color = cdict[c])))
_count=0
for i,d in demo_data.iterrows():
    print(i)
    _x,_y=d['geometry'].exterior.xy
    fig.add_trace(go.Scattermapbox(lon=list(_x), lat=list(_y), fill="toself",marker=dict(color=cdict[route_colors[_count]])))
    _count+=1
    
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

html_fname=utils.get_county_htmldata(args.state,args.county,n_sites)
fig.write_html(html_fname)

print(html_fname,' Generated')
