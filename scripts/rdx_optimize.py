#!/usr/bin/env python                                                                                                                                                                   
#from collections import OrderedDict
#import geopandas
#import matplotlib
import osmnx as ox
#from matplotlib.colors import ListedColormap
import numpy
import ortools
from ortools.linear_solver import pywraplp
#import shapely
#from shapely.geometry import Point
#import spaghetti
import sys
import warnings
import pickle
import numpy as np
import argparse
from radxupsite import utils
import os
from multiprocessing import Pool
import atexit
from tqdm import tqdm

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('state', metavar='S', type=str, 
                    help='State')
parser.add_argument('county', metavar='C', type=str,
                    help='County')
parser.add_argument('censusvar', metavar='V', type=str,
                help='Census Variable to Optimize')
parser.add_argument('nsites', metavar='N', type=int,
                help='Number of sites to optimize for')
parser.add_argument('--cores', metavar='C', type=int, default=None,
                help='Number of cores to use when optimizing')
parser.add_argument('--year', metavar='Y', type=str, default='2019',
                help='year to use for census data')

args = parser.parse_args()

county_data_directory=utils.get_county_data_dir(args.state,args.county)

if not os.path.exists(county_data_directory):
    raise Exception('No data available for county',args.county,' please run rdx_getdata.py')



demo_file=utils.get_county_demodata(args.state,args.county,args.year,args.censusvar)
graph_file=utils.get_county_graphdata(args.state,args.county)
poi_file=utils.get_county_poidata(args.state,args.county)
n_sites=args.nsites



poi_points,poi_names,pois=pickle.load(open(poi_file,'rb'))
demo_data=pickle.load(open(demo_file,'rb'))
graph=pickle.load(open(graph_file,'rb'))



pop_data=[]
pop_nodes=[]

print('Preparing Population Nodes')
for inddex,r in tqdm(demo_data.iterrows(),total=len(demo_data)):
    p_center=r['geometry'].centroid.xy
    pop=r['Population']
    pop_nodes.append(ox.nearest_nodes(graph,p_center[0][0],p_center[1][0] ))
    pop_data.append(pop)

print('Preparing Proposal Nodes')
poi_nodes=[ox.nearest_nodes(graph,p[0],p[1] ) for p in tqdm(poi_points)]

def get_connection(args):
    pop_i,pop_n,poi_i,poi_n=args
    try:
        route=ox.shortest_path(graph,pop_n,poi_n,weight='travel_time')
        distance=np.sum(ox.utils_graph.get_route_edge_attributes(graph, route, 'travel_time'))*pop_data[pop_i]
        return pop_i,poi_i,distance
    except:
#        print(args)
        return pop_i,poi_i,None
                    


if __name__=='__main__':
    p=Pool(processes=args.cores)
    atexit.register(p.close)
    map_list=[]

    for pop_i,pop_n in tqdm(enumerate(pop_nodes)):
        for poi_i,poi_n in enumerate(poi_nodes):
            map_list.append((pop_i,pop_n,poi_i,poi_n))
    print('Calculating Distances')

    
    out_data=list(tqdm(p.imap(get_connection,map_list),total=len(map_list)))

    connection=np.ones((len(pop_nodes),len(poi_nodes)))
    bad_path=[]

    
    for pop_i,poi_i,distance in out_data:
        if distance != None:
            connection[pop_i,poi_i]=distance
        else:
            bad_path.append((pop_i,poi_i))




    print('Optimizing')

    solver_instance = pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING
    #solver_instance = pywraplp.Solver.GUROBI_MIXED_INTEGER_PROGRAMMING

    #solver_instance = pywraplp.Solver.GLPK_MIXED_INTEGER_PROGRAMMING
    #solver_instance = pywraplp.Solver.CPLEX_MIXED_INTEGER_PROGRAMMING

    model = pywraplp.Solver(args.county, solver_instance)
    model.set_time_limit(60*10*100)

    fac_vars = {j: model.IntVar(0, 1, "y[%i]" % (j)) for j,n in enumerate(poi_nodes)}
    cli_vars = {
                    (i, j): model.IntVar(0, 1, "x[%i,%i]" % (i, j))
                    for i,_ in enumerate(pop_nodes)
                    for j,_ in enumerate(poi_nodes)
                }



 






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
    colors=['r','g','b','m']*200


    for i,node in enumerate(pop_nodes):
       s=poi_nodes[site_selections[i]]
       route=ox.shortest_path(graph,node,s,weight='travel_time')
       route_colors.append(  colors[site_index.index(site_selections[i])]   )
       route_list.append(route)

    site_nodes=[poi_nodes[i] for i in site_index]    

    opt_file=utils.get_county_optdata(args.state,args.county,args.year,args.censusvar,n_sites)

    with open(opt_file,'wb') as out_file:
        pickle.dump([route_list,route_colors,site_nodes,site_index],out_file)

    print('Optimization Finished')





 
