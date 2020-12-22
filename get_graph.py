import multiprocessing as mp
import numpy as np
import osmnx as ox
from openpyxl import Workbook,load_workbook
from utils import read_xlsx
import matplotlib.pyplot as plt
import pickle

jg=ox.graph_from_place('Josephine County',network_type='drive')
jg = ox.add_edge_speeds(jg)
jg = ox.add_edge_travel_times(jg)
pickle.dump(jg,open('Josephine_County_Graph.pk','wb'))
ox.plot_graph(jg)
