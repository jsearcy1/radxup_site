
import csv
from radxupsite import utils
from shapely.geometry import Point
import osmnx as ox
import pickle
import numpy as np
import pandas as pd
site_data={}
time_cutoff=45*60 #3/4 Hour  


with open('output_data.csv', newline='') as csvfile:
     reader = csv.DictReader(csvfile)
     for row in reader:
         if row['UO Site ID']=='JO5':
              row['County']='Jackson'

         if row['County'] =="":
              print('Ahhhh',row)
              continue          
         if row['County'].strip() not in site_data:
             site_data[row['County'].strip()]=[]
         site_data[row['County'].strip()].append(row)
print(sum([len(i) for i in site_data.values()]))
         
proposal_data=pd.read_excel('site_prop_loc.xlsx')

for county in site_data:
    
    county_data_directory=utils.get_county_data_dir('oregon',county)
    demo_file=utils.get_county_demodata('oregon',county)
    graph_file=utils.get_county_graphdata('oregon',county)
    poi_file=utils.get_county_poidata('oregon',county)

    poi_points,poi_names,pois=pickle.load(open(poi_file,'rb'))
    demo_data=pickle.load(open(demo_file,'rb'))
    graph=pickle.load(open(graph_file,'rb'))
#    ox.plot_graph(graph)
    
    county_proposals=[(i,p) for i,p in proposal_data.iterrows() if p['County'] ==county ]             
    n_site_proposals=set([ p['Sites Per County in Optimization'] for i,p in county_proposals])    

    site_nodes=[ox.get_nearest_node(graph,(float(p['lat']),float(p['long']))) for p in site_data[county] ]

    
    if len(n_site_proposals) ==1:
         n_sites=list(n_site_proposals)[0]
    elif len(n_site_proposals)==0:
         n_sites=0
    else:
         _sites=[i for i in n_site_proposals if  i-len(site_nodes) > 0]
         if _sites ==[]:
              n_sites=max(n_site_proposals)
         else:
              n_sites=min(_sites)

         
    proposal_nodes=[(ox.get_nearest_node(graph,(float(p['Lattitude']),float(p['Longitude']))),i) for i,p in proposal_data.iterrows()
                    if p['County'] ==county and p['Sites Per County in Optimization']==n_sites]

    
    best_site=[]

    for index,s in enumerate(site_nodes):
         if n_sites !=0:
              route=[(ox.shortest_path(graph,s,p,weight='travel_time'),i) for p,i in proposal_nodes]
              print("Routes",len(route),len(proposal_nodes))
              td,i=min([(np.sum(ox.utils_graph.get_route_edge_attributes(graph, r, 'travel_time')),i) for r,i in route])
             # ox.plot_graph_route(graph,route[i])
              site_data[county][index]["DT to Proposal"]=td
              site_data[county][index]["Proposal Number"]=proposal_data.iloc[i]['Site Proposal Number']
              site_data[county][index]["Sites Per County in Optimization"]=proposal_data.iloc[i]["Sites Per County in Optimization"]

         else:
              site_data[county][index]["DT to Proposal"]='None'
              site_data[county][index]["Proposal Number"]='None'
              site_data[county][index]["Sites Per County in Optimization"]='None'
    
    

    pop_nodes=[]
    pop_data=[]
    for inddex,r in demo_data.iterrows():
         p_center=r['geometry'].centroid.xy
         pop=r['Population']
         pop_nodes.append(ox.get_nearest_node(graph,(p_center[1][0],p_center[0][0]) ))
         pop_data.append(pop)

    site_index=[]
    best_times=[]
    site_routes=[]
    for pop_i,pop_n in enumerate(pop_nodes):
         times=[]
         pop=[]
         routes=[]
         for site_n in site_nodes:
              route=ox.shortest_path(graph,pop_n,site_n,weight='travel_time')
              td=np.sum(ox.utils_graph.get_route_edge_attributes(graph, route, 'travel_time'))
              times.append(td)
              routes.append(route)
         site_is=[(i,v) for i,v in enumerate(times) if v < time_cutoff]
         site_index.append(site_is)
         site_routes.append([routes[i[0]] for i in site_is])
         
    for pop_i,pop_n in enumerate(pop_nodes):
          for index,(si,time) in enumerate(site_index[pop_i]):          
              if 'Population_Assigned' not in site_data[county][si]:
                   site_data[county][si]['Population_Assigned']=0
                   site_data[county][si]['Average_Drivetime']=0
                   site_data[county][si]['routes']=[]

              site_data[county][si]['Population_Assigned']+=pop_data[pop_i]
              site_data[county][si]['Average_Drivetime']+=time*pop_data[pop_i]             
              site_data[county][si]['routes'].append(site_routes[pop_i][index])
          
    for s in site_data[county]:
          # print(s)
          # if  s['UO Site ID'] == 'MC3':
          #      match=[m for m in site_data[county] if m['UO Site ID']=='DE1'][0] 
          #      s['Population_Assigned']=match['Population_Assigned']
          #      s['Average_Drivetime']=match['Average_Drivetime']

          # if  s['UO Site ID'] == 'MC1':
          #      match=[m for m in site_data[county] if m['UO Site ID']=='LI1'][0] 
          #      s['Population_Assigned']=match['Population_Assigned']
          #      s['Average_Drivetime']=match['Average_Drivetime']

               
          if 'Population_Assigned' not in s:
               s['Population_Assigned']=0
               s['Average_Drivetime']=0
          else:         
               s['Average_Drivetime']=s['Average_Drivetime']/s['Population_Assigned']
               print(s['Average_Drivetime'],s['Population_Assigned'])
               print(s)
          
 
pickle.dump(site_data,open('distance_analysis.pk','wb'))
