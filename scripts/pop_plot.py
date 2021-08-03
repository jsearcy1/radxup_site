import pickle
import pandas
from urllib.request import urlopen
import json
import numpy as np
import osmnx as ox
import argparse
import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
#Df._csv("https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
#                   dtype={"fips": str})

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from radxupsite import utils
import sys

map_data=gpd.read_file('/home/jsearcy/radxup_clean/radxupsite/data/oregon/blkgrp/cb_2019_41_bg_500k.shp')
zipcode_data=gpd.read_file('/home/jsearcy/radxup_clean/scripts/zipcodes/cb_2018_us_zcta510_500k.shp')



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
s_lon=[]
s_lat=[]



for county in ['Jackson']:
    graph_file=utils.get_county_graphdata('oregon',county)
    graph=pickle.load(open(graph_file,'rb'))
    points=[]
    geo_matches={}
    bg_matches={}
    zip_matches={}    
    for site in site_data[county]:
        matches=[]
        for route in site['routes']:
            _p=node_list_to_path(graph,route)
            if _p==[]: continue
            for pc in (_p[0],_p[-1]):
                p=Point(*pc)
                matches+=set([i for i,v in map_data.iterrows() if v.geometry.contains(p)] )
            geo_matches[site['uo_site_id']]=matches
            
            vals=list(reversed(_p))+_p
            points+=vals
        print(matches)
        lines.append(points)
        s_lon.append(float(site['long']))
        s_lat.append(float(site['lat']))
        p=Point(float(site['long']),float(site['lat']))
        bg_matches[site['uo_site_id']]=[list(set([i for i,v in map_data.iterrows() if v.geometry.contains(p)]))[0]]
        zip_matches[site['uo_site_id']]=[list(set([i for i,v in zipcode_data.iterrows() if v.geometry.contains(p)]))[0]]
        

demo_data=pd.DataFrame()
demo_data['latitude']=s_lat
demo_data['longitude']=s_lon

        
#fig = px.scatter_mapbox(demo_data, lat="latitude", lon='longitude',height=800)
#cdict={'r':'red','g':'green','b':'blue','m':'magenta','c':'cyan','y':'yellow'}
new_df=None
for i,site in enumerate(geo_matches):
#   s_lat.append(site['lat'])
#   s_long.append(site['long'])
   _tdf=map_data.iloc[geo_matches[site]]
   _tdf['Color']=i
   if type(new_df)==type(None):
       new_df=_tdf
   else:
       new_df=new_df.append(_tdf)
   print(new_df.shape)

map_data['Color'] = np.random.randint(1, 6, map_data.shape[0])
pscale=150
ms=8
cpoint=dict(lat=42.348, lon=-122.849)
fig =px.choropleth_mapbox(new_df, geojson=new_df.geometry, color="Color",
                          locations=new_df.index,
                          mapbox_style='carto-positron',
                          opacity=0.5
                   )

fig.add_trace(
    go.Scattermapbox(
    name = "Source",
    mode = "markers",
    lon =s_lon,
    lat = s_lat,
        marker = {'size': ms, 'color':"seagreen"}),row=1,col=1)


    
#fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(
        geo = dict(
            projection_scale=pscale, #this is kind of like zoom
            center=cpoint, # this will center on the point
        ))

html_fname="pop.html"
fig.write_html(html_fname)

del fig,new_df
new_df=None
for i,site in enumerate(bg_matches):
 
   _tdf=map_data.iloc[bg_matches[site]]
   print(_tdf)
   _tdf['Color']=i
   if type(new_df)==type(None):
       new_df=_tdf
   else:
       new_df=new_df.append(_tdf)
   print(new_df.shape)



fig =px.choropleth_mapbox(new_df, geojson=new_df.geometry, color="Color",
                          locations=new_df.index,
                          mapbox_style='carto-positron',
                          opacity=0.5
                   )

fig.add_trace(
    go.Scattermapbox(
    name = "Source",
    mode = "markers",
    lon =s_lon,
    lat = s_lat,
        marker = {'size': ms, 'color':"seagreen"}),row=1,col=1)



#fig.update_layout(mapbox_style="open-street-map")                                                                                               
fig.update_layout(
        geo = dict(
            projection_scale=pscale, #this is kind of like zoom                                                                                      
            center=cpoint, # this will center on the point                                                              
        ))

html_fname="pop_bg.html"
fig.write_html(html_fname)
   
print(html_fname,' Generated')

del fig,new_df
new_df=None
for i,site in enumerate(zip_matches):
 
   _tdf=zipcode_data.iloc[zip_matches[site]]
   print(_tdf)
   _tdf['Color']=i
   if type(new_df)==type(None):
       new_df=_tdf
   else:
       new_df=new_df.append(_tdf)
   print(new_df.shape)
fig =px.choropleth_mapbox(new_df, geojson=new_df.geometry, color="Color",
                          locations=new_df.index,
                          mapbox_style='carto-positron',
                          opacity=0.5
                   )

fig.add_trace(
    go.Scattermapbox(
    name = "Source",
    mode = "markers",
    lon =s_lon,
    lat = s_lat,
        marker = {'size': ms, 'color':"seagreen"}),row=1,col=1)




#fig.update_layout(mapbox_style="open-street-map")                                                                                               
fig.update_layout(
        geo = dict(
            projection_scale=pscale, #this is kind of like zoom                                                                                      
            center=cpoint, # this will center on the point                                                              
        ))

html_fname="pop_zip.html"
fig.write_html(html_fname)
   
print(html_fname,' Generated')
