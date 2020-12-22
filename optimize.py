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
from hyperopt import hp,fmin,tpe,Trials,STATUS_OK
import pymongo
from hyperopt.mongoexp import MongoTrials
import sys

county=sys.argv[1] #'Josephine County'

n_sites=int(sys.argv[2])


poi_points,poi_names,pois=pickle.load(open(county+'_POIS.pk','rb'))

graph,data,pop_nodes=pickle.load(open(county+'_optimization_inputs.pk','rb'))

poi_nodes=[ox.get_nearest_node(graph,(p[1],p[0]) ) for p in poi_points]
print(len(poi_nodes))




gl=list(graph)

site_nodes=np.random.choice(gl,3)

itime=time.time()

gpos=[(graph.nodes[n]['y'],graph.nodes[n]['x']) for n in graph.nodes]

lon_min=min([p[1] for p in gpos])
lon_max=max([p[1] for p in gpos])
lat_min=min([p[0] for p in gpos])
lat_max=max([p[0] for p in gpos])


hp_space={}
for i in range(n_sites):

    hp_space['lat_'+str(i)]= hp.uniform('lat_'+str(i),lat_min,lat_max)
    hp_space['lon_'+str(i)]= hp.uniform('lon_'+str(i),lon_min,lon_max)



def d_time(args):


    
    site_indexs=[np.argmin([ (args['lat_'+str(i)]-lat)**2 + (args['lon_'+str(i)]-lon)**2 for lon,lat in poi_points ]  )
            for i in range(n_sites)]
    print(site_indexs)
    site_nodes=[poi_nodes[i] for i in site_indexs]

    
    site_pop=np.zeros(len(site_nodes))
    paths=[]
    times=[]
    bad_nodes=[]
 
    for weight,pop_center in zip(data,pop_nodes):
         for s_i,site in enumerate(site_nodes):
            try:route=ox.shortest_path(graph,pop_center,site,weight='travel_time')
            except:
                bad_nodes.append(pop_center)
                paths.append((np.inf,s_i))
                continue
            paths.append((np.sum(
                ox.utils_graph.get_route_edge_attributes(graph, route, 'travel_time'))*weight,s_i))
         #print(min(paths))
         best_time,best_site=min(paths)
       #  if np.isinf(best_time):
       #      print('bad node',pop_center)
         #print(best_time,best_site)
         site_pop[best_site]+=weight
         times.append(best_time)
         paths=[]
    #print(site_pop,np.max(site_pop),np.min(site_pop))

    loss=np.sum(times)/np.sum(data)/60.+np.std(site_pop)/np.sum(data)
    print(loss)
    
    return      {'loss': loss, 'status': STATUS_OK, 'poi_index':site_indexs }  #Not sure what to put as 14 here
 

trials = MongoTrials('mongo://localhost:1234/zip_db/jobs', exp_key=county.replace(' ','_')+'_pois_'+str(n_sites))
#trials= Trials()

res=fmin(d_time,hp_space, algo=tpe.suggest,max_evals=100000,trials=trials)








#pop_nodes=[ox.get_nearest_node(graph, _point) for _point in pos]
site_nodes=[ox.get_nearest_node(graph,(res['lat_'+str(i)],res['lon_'+str(i)]) ) for i in range(n_sites)]
colors=['r','g','b','m']*2

route_list=[]
route_colors=[]
for p in pop_nodes:
    _tlist=[]
    for s in site_nodes:
        route=ox.shortest_path(graph,p,s,weight='travel_time')
        time=np.sum(ox.utils_graph.get_route_edge_attributes(graph, route, 'travel_time'))
        _tlist.append((time,route,s))
    _tlist.sort()
    best_time,best_route,best_site=_tlist[0]
    route_list.append(best_route)
    route_colors.append(  colors[site_nodes.index(best_site)]   )

fig, ax = ox.plot_graph_routes(graph, routes=route_list, route_colors=route_colors,
                               route_linewidth=6, node_size=0)
    
# zcode= ox.geocode_to_gdf(zipcodes,1)
# ox.project_gdf(zcode).plot()
     
    
# for z,d in zip(zipcodes,data):
#      if z=='Oregon':continue
#      print(z,d)
      
# plt.show()
# oijpoij



# G = ox.graph_from_place(place, network_type='drive')

# ox.config(use_cache=True, log_console=True)
# ox.__version__

# place = 'Piedmont, California, USA'



# # convert projected graph to edges geodataframe
# gdf_edges = ox.graph_to_gdfs(ox.project_graph(G), nodes=False)

# # list of lats and lngs
# lngs = gdf_edges.head().centroid.map(lambda x: x.coords[0][0])
# lats = gdf_edges.head().centroid.map(lambda x: x.coords[0][1])

# # the lat, lng at the spatial center of the graph
# lng, lat = gdf_edges.unary_union.centroid.coords[0]
# center_point = lat, lng



# # find the nearest node to some point
# center_node = ox.get_nearest_node(G, center_point)


# # find the nearest nodes to a set of points
# # optionally specify `method` use use a kdtree or balltree index
# nearest_nodes = ox.get_nearest_nodes(G, lngs, lats, method='kdtree')

# # find the nearest edge to some point
# nearest_edge = ox.get_nearest_edge(G, center_point)

# # find the nearest edges to some set of points
# # optionally specify `method` use use a kdtree or balltree index
# nearest_edges = ox.get_nearest_edges(G, lngs, lats)



# # find the shortest path (by distance) between these nodes then plot it
# orig = list(G)[0]
# dest = list(G)[120]
# route = ox.shortest_path(G, orig, dest, weight='length')
# fig, ax = ox.plot_graph_route(G, route, route_color='y', route_linewidth=6, node_size=0)

