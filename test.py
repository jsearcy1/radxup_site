import multiprocessing as mp
import numpy as np
import osmnx as ox
from openpyxl import Workbook,load_workbook
from utils import read_xlsx
import matplotlib.pyplot as plt

demo_dict=read_xlsx('OR_Hispanic_Counts_ZipCode_Sorted.xlsx')

data=[]
zipcodes=[]
for v in demo_dict:
    data.append(v['Hispanic'])
    zipcodes.append(v['ZipCode'])


zcode= ox.geocode_to_gdf(zipcodes)
ox.project_gdf(zcode).plot()
     
    
for z,d in zip(zipcodes,data):
     if z=='Oregon':continue
     print(z,d)
      
plt.show()
oijpoij



G = ox.graph_from_place(place, network_type='drive')

ox.config(use_cache=True, log_console=True)
ox.__version__

place = 'Piedmont, California, USA'



# convert projected graph to edges geodataframe
gdf_edges = ox.graph_to_gdfs(ox.project_graph(G), nodes=False)

# list of lats and lngs
lngs = gdf_edges.head().centroid.map(lambda x: x.coords[0][0])
lats = gdf_edges.head().centroid.map(lambda x: x.coords[0][1])

# the lat, lng at the spatial center of the graph
lng, lat = gdf_edges.unary_union.centroid.coords[0]
center_point = lat, lng



# find the nearest node to some point
center_node = ox.get_nearest_node(G, center_point)


# find the nearest nodes to a set of points
# optionally specify `method` use use a kdtree or balltree index
nearest_nodes = ox.get_nearest_nodes(G, lngs, lats, method='kdtree')

# find the nearest edge to some point
nearest_edge = ox.get_nearest_edge(G, center_point)

# find the nearest edges to some set of points
# optionally specify `method` use use a kdtree or balltree index
nearest_edges = ox.get_nearest_edges(G, lngs, lats)



# find the shortest path (by distance) between these nodes then plot it
orig = list(G)[0]
dest = list(G)[120]
route = ox.shortest_path(G, orig, dest, weight='length')
fig, ax = ox.plot_graph_route(G, route, route_color='y', route_linewidth=6, node_size=0)

