import csv
from radxupsite import utils
from shapely.geometry import Point
import osmnx as ox
import pickle
import numpy as np
import pandas as pd
import pdb
site_data={}
time_cutoff=45*60 #3/4 Hour  

def load_data(county,var=None):
     county_data_directory=utils.get_county_data_dir('oregon',county)
     demo_file=utils.get_county_demodata('oregon',county)
     graph_file=utils.get_county_graphdata('oregon',county)
     poi_file=utils.get_county_poidata('oregon',county)

     poi_points,poi_names,pois=pickle.load(open(poi_file,'rb'))
     demo_data=pickle.load(open(demo_file,'rb'))
     graph=pickle.load(open(graph_file,'rb'))
    
     return graph,demo_data,poi_points,poi_names,pois


def get_local_pop_and_drive_time(county,lattitude,longitude,time_cutoff=45*60):
     graph,demo_data,poi_points,poi_names,pois=load_data(county)     

     site_node=ox.get_nearest_node(graph,(lattitude,longitude))
     
     pop_nodes=[]
     pop_data=[]
     for index,r in demo_data.iterrows():
          p_center=r['geometry'].centroid.xy
          pop=r['Population']
          pop_nodes.append(ox.get_nearest_node(graph,(p_center[1][0],p_center[0][0]) ))
          pop_data.append(pop)

     total_time=0
     population=0
     routes=[]
     for pop_i,pop_n in enumerate(pop_nodes):
         route=ox.shortest_path(graph,pop_n,site_node,weight='travel_time')
         time=np.sum(ox.utils_graph.get_route_edge_attributes(graph, route, 'travel_time'))
         routes.append(route)
         if time < time_cutoff:              
              population+=pop_data[pop_i]
              total_time+=pop_data[pop_i]*time
     if population !=0:
          avg_time=total_time/population
     else:
          avg_time='N/A'
          ox.plot_graph_routes(graph,routes)

     return population,avg_time




def get_overlap_matrix(county,locations,time_cutoff=45*60):
     graph,demo_data,poi_points,poi_names,pois=load_data(county)     
     n_loc=len(locations)
     print(locations)
     site_nodes=[ox.get_nearest_node(graph,(lattitude,longitude))
                 for (lattitude,longitude) in locations]

     pop_nodes=[]
     pop_data=[]
     p_location=[]
     for index,r in demo_data.iterrows():
          p_center=r['geometry'].centroid.xy
          pop=r['Population']
          pop_nodes.append(ox.get_nearest_node(graph,(p_center[1][0],p_center[0][0]) ))
          pop_data.append(pop)
          

     pop_matrix=np.zeros((n_loc,len(pop_nodes)))     
     time_matrix=np.zeros((n_loc,len(pop_nodes)))
     

     total_time=0
     population=0
     routes=[]
     for pop_i,pop_n in enumerate(pop_nodes):
         for loc_i in range(n_loc):
               route=ox.shortest_path(graph,pop_n,site_nodes[loc_i],weight='travel_time')
               time=np.sum(ox.utils_graph.get_route_edge_attributes(graph, route, 'travel_time'))
               pop_matrix[loc_i,pop_i]+=pop_data[pop_i]
               time_matrix[loc_i,pop_i]+=time
         
     #pdb.set_trace()
     return demo_data,time_matrix



