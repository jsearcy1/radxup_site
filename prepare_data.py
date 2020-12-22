import multiprocessing as mp
import pickle
import numpy as np
import osmnx as ox
from openpyxl import Workbook,load_workbook
from utils import read_xlsx
import matplotlib.pyplot as plt
import time
import censusgeocode as cg
from uszipcode import SearchEngine
from hyperopt import hp,fmin,tpe
import pymongo
from hyperopt.mongoexp import MongoTrials
from shapely.geometry.point import Point
from shapely.geometry.polygon import Polygon
import sys

county=sys.argv[1]#'Josephine County'
demo_dict=read_xlsx('Oregon Census Block GeoCoded Data.xlsx')
search=SearchEngine(simple_zipcode=True)

if True:
    graph=ox.graph_from_place(county+', Oregon',network_type='drive')
    graph = ox.add_edge_speeds(graph)
    graph = ox.add_edge_travel_times(graph)
    
    pickle.dump(graph,open(county+'_Graph.pk','wb'))


    
if True:
    points=[]
    names=[]
    pois=[]
    for am in ['parking',
               'school',
               'college',
               'social_facility',
               'conference_centre',
               'marketplace',
               'place_of_worship','park']:
        if am =='park':
            df=ox.pois_from_place(county+', Oregon',tags={'leisure':'park'})
        else:
            df=ox.pois_from_place(county+', Oregon',tags={'amenity':am})
        if len(df)==0:continue
        for index,r in df.iterrows():
            geo=r['geometry']
            if type(geo)==Point:
                point=np.squeeze(geo.xy)
            elif type(geo)==Polygon:
                point=np.mean(np.squeeze(geo.exterior.coords.xy),axis=-1)
            else:
                continue
            points.append(point)
            names.append(r.name)
            pois.append(r)

        

    pickle.dump([points,names,pois],open(county+'_POIS.pk','wb'))




for v in demo_dict:
    result = search.by_coordinates(float(v['latitude']),float(v['longitude']),radius=100,returns=1)
    v['ZipCode']=result[0]
    

data=[]
zipcodes=[]
pos=[]
pop_nodes=[]
for v in demo_dict:
    if v['ZipCode'].county != county:continue

    if float(v['B03002e12']) > 0:    
        data.append(float(v['B03002e12']))
        point=(float(v['latitude']),float(v['longitude']))
        pos.append(point)
        pop_nodes.append(ox.get_nearest_node(graph, point))


if 40338501 in pop_nodes: #this is a bad node
    pop_nodes.remove(40338501)
    
print(len(pop_nodes))
pickle.dump([graph,data,pop_nodes],open(county+'_optimization_inputs.pk','wb'))


routes=[]
for p in pop_nodes:
    routes.append(ox.shortest_path(graph,p,pop_nodes[3]))
ox.plot_graph(graph)
ox.plot_graph_routes(graph,routes)
