from collections import OrderedDict
import geopandas
import libpysal
from libpysal import cg, examples
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import osmnx as ox
from matplotlib.colors import ListedColormap

import numpy
import ortools
from ortools.linear_solver import pywraplp
import seaborn
import shapely
from shapely.geometry import Point
import spaghetti
import sys
import warnings
import pickle
import numpy as np

county=sys.argv[1] #'Josephine County'                                                                                             
n_sites=4



poi_points,poi_names,pois=pickle.load(open(county+'_POIS.pk','rb'))

graph,data,pop_nodes=pickle.load(open(county+'_optimization_inputs.pk','rb'))

poi_nodes=[ox.get_nearest_node(graph,(p[1],p[0]) ) for p in poi_points]





solver_instance = pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING
#solver_instance = pywraplp.Solver.GUROBI_MIXED_INTEGER_PROGRAMMING

#solver_instance = pywraplp.Solver.GLPK_MIXED_INTEGER_PROGRAMMING
#solver_instance = pywraplp.Solver.CPLEX_MIXED_INTEGER_PROGRAMMING

model = pywraplp.Solver(county, solver_instance)
model.set_time_limit(60*10*100)

fac_vars = {j: model.IntVar(0, 1, "y[%i]" % (j)) for j,n in enumerate(poi_nodes)}
cli_vars = {
                (i, j): model.IntVar(0, 1, "x[%i,%i]" % (i, j))
                for i,_ in enumerate(pop_nodes)
                for j,_ in enumerate(poi_nodes)
            }

 
connection=np.ones((len(pop_nodes),len(poi_nodes)))
bad_path=[]

for pop_i,pop_n in enumerate(pop_nodes):
    for poi_i,poi_n in enumerate(poi_nodes):

        try:
            route=ox.shortest_path(graph,pop_n,poi_n,weight='travel_time')
            distance=np.sum(ox.utils_graph.get_route_edge_attributes(graph, route, 'travel_time'))*data[pop_i]
            connection[pop_i,poi_i]=distance
                    
        except:
            bad_path.append((pop_i,poi_i))
            print(bad_path[-1])




obj = [
    connection[i, j]*cli_vars[i,j]
    for i,_ in enumerate(pop_nodes)
    for j,_ in enumerate(poi_nodes)
]



for i in range(len(pop_nodes)):
    model.Add(model.Sum([cli_vars[i, j] for j in range(len(poi_nodes))]) == 1)

model.Add(model.Sum([fac_vars[j] for j in range(len(poi_nodes))]) == n_sites)
        
for i in range(len(pop_nodes)):
    for j in range(len(poi_nodes)):
        model.Add(fac_vars[j] - cli_vars[i, j] >= 0)

for i,j in bad_path:
    model.Add(cli_vars[i,j]==0)


model.Minimize(model.Sum(obj))

model.Solve()


site_index=[i for i,v in fac_vars.items() if v.solution_value() != 0]

site_selections=[]
for i in range(len(pop_nodes)):
    site_selections.append(np.argmax( [cli_vars[i,n].solution_value() for n in range(len(poi_nodes)) ] ) )


route_list=[]
route_colors=[]
colors=['r','g','b','m']*2


for i,node in enumerate(pop_nodes):
   s=poi_nodes[site_selections[i]]
   route=ox.shortest_path(graph,node,s,weight='travel_time')
   route_colors.append(  colors[site_index.index(site_selections[i])]   )
   route_list.append(route)
 
site_nodes=[poi_nodes[i] for i in site_index]    

pickle.dump([route_list,route_colors,site_nodes,site_index],open('flp_g_data_'+county+'_'+str(n_sites)+'_.pk','wb'))



fig, ax = ox.plot_graph_routes(graph, routes=route_list, route_colors=route_colors,
                               route_linewidth=6, node_size=0)







