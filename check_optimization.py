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
import pickle
import sys
county=sys.argv[1]#sy'Josephine County'
n_sites=int(sys.argv[2])



graph,data,pop_nodes=pickle.load(open(county+'_optimization_inputs.pk','rb'))
poi_points,poi_names,pois=pickle.load(open(county+'_POIS.pk','rb'))
poi_nodes=[ox.get_nearest_node(graph,(p[1],p[0]) ) for p in poi_points]


trials = MongoTrials('mongo://localhost:1234/zip_db/jobs', exp_key=county.replace(' ','_')+'_pois_'+str(n_sites))
res=trials.best_trial['misc']['vals']
site_index= trials.best_trial['result']['poi_index']


if False:
    fig, axs = plt.subplots(n_sites, 1,figsize=(5,n_sites*5))    
    for i in range(n_sites):

        lat=[v['vals']['lat_'+str(i)][0] for index,v in  enumerate(trials.miscs) if 'loss' in trials.results[index] ],
        lon=[v['vals']['lon_'+str(i)][0] for index,v in  enumerate(trials.miscs) if 'loss' in trials.results[index] ],
        col=[ v['loss'] for v in trials.results if 'loss' in v]
        axs[i].scatter(lon,lat,c= col )
        axs[i].set_title(str(i))
    plt.show()



site_nodes=[poi_nodes[i] for i in site_index]
site_pop=np.zeros(len(site_nodes))
colors=['r','g','b','m','c','y']*2

route_list=[]
route_colors=[]
for p_i,p in enumerate(pop_nodes):
    _tlist=[]
    for s_i,s in enumerate(site_nodes):
        route=ox.shortest_path(graph,p,s,weight='travel_time')
        time=np.sum(ox.utils_graph.get_route_edge_attributes(graph, route, 'travel_time'))
        _tlist.append((time,route,s,s_i))
    _tlist.sort()
    best_time,best_route,best_site,best_site_index=_tlist[0]
    route_list.append(best_route)
    route_colors.append(  colors[best_site_index]   )
    site_pop[best_site_index]+=data[p_i]
fig, ax = ox.plot_graph_routes(graph, routes=route_list, route_colors=route_colors,
                               route_linewidth=6, node_size=0)

pickle.dump([route_list,route_colors,site_nodes,site_index],open('plot_data_'+county+'_'+str(n_sites)+'_.pk','wb'))
print(site_pop)
