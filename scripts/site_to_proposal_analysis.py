import csv
from radxupsite import utils
from shapely.geometry import Point
import osmnx as ox
import pickle
import numpy as np
import pandas as pd
from distances import get_local_pop_and_drive_time,get_overlap_matrix





site_data={}
time_cutoff=45*60 #1 Hour  

         
proposal_data=pd.read_excel('Site Proposal locations.xlsx',sheet_name=1)
site_data=pd.read_csv('site_geoid_20210830.csv')
site_loc_dict={}
for index,site in site_data.iterrows():
    site_loc_dict[site['UO Site ID']]=(float(site['lat']),float(site['long']))
    
if False:
    for index,proposal in proposal_data.iterrows():
        if proposal["Replaced Site ID"] in site_loc_dict:
            site_location=site_loc_dict[proposal["Replaced Site ID"]]

            graph_file=utils.get_county_graphdata('oregon',proposal['County'])
            graph=pickle.load(open(graph_file,'rb'))    
            proposal_node=ox.get_nearest_node(graph,(float(proposal['Lattitude']),float(proposal['Longitude'])))
            site_node=ox.get_nearest_node(graph,site_location)
            route=ox.shortest_path(graph,site_node,proposal_node,weight='travel_time')
            travel_time=np.sum(ox.utils_graph.get_route_edge_attributes(graph, route, 'travel_time'))
            print(travel_time,proposal["Replaced Site ID"])

        print('Proposal estimates')

if False:
    for index,proposal in proposal_data.iterrows():
        pop,avg_time=get_local_pop_and_drive_time(proposal['County'],
                                float(proposal['Lattitude']),
                                 float(proposal['Longitude']),time_cutoff)
        id_str= str(proposal["Site Proposal Number"]) + proposal["County"] + str(proposal["Sites Per County in Optimization"])                                                               

        print(id_str,pop,avg_time)


if False:

    for index,site in site_data.iterrows():
        pop,avg_time=get_local_pop_and_drive_time(site['County'].strip(),
                                     float(site['lat']),
                                     float(site['long']),time_cutoff)
        id_str= str(site["UO Site ID"])
        print(id_str,pop,avg_time)

if False:
    county='Marion'

    info=[(s['UO Site ID'],(s['lat'],s['long'])) for i,s in site_data.iterrows() if s['County'].strip()==county]
    sites,locations=zip(*info)
    demod,act_m=get_overlap_matrix(county,locations,time_cutoff=45*60)

    
    info=[(s['UO Site ID'],(s['lat'],s['long'])) for i,s in proposal_data.iterrows() if s['County'].strip()==county and s['Sites Per County in Optimization']==5]
    prop_sites,prop_locations=zip(*info)
    demod,prop_m=get_overlap_matrix(county,prop_locations,time_cutoff=45*60)

    pdb.set_trace()

    loc_dict={}
    for i,s in site_data.iterrows():
        loc_dict[s['UO Site ID']]=(s['lat'],s['long'])
        
    replacement_sites=[p['Replaced Site ID'] for i,p in proposal_data.iterrows()
                      if p['Replaced Site ID'] !='' and not np.isnan(p)]

    
#    line_lats=[]
#    line_longs=[]
#    for i,p in proposal_data.iterrows():
#        if p['Replaced Site ID'] in p
    

    
    df=pd.DataFrame({'lat':[i[0] for i in locations],
                     'lon':[i[1] for i in locations],
                     'site':sites
                     }  )

    
if True:
    import plotly.express as px

#    fig = px.scatter_mapbox(site_data,
#                            lat="lat", lon="long", hover_name="UO Site ID",
#                            color_discrete_sequence=["green"], zoom=3, height=300)
#    fig.update_layout(mapbox_style="carto-positron")
#    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
#    fig.show()

    demo_file=utils.get_county_demodata('oregon','Marion')
    demo_data=pickle.load(open(demo_file,'rb'))
        
    dlong,dlat=zip(*[d['geometry'].centroid.xy for i,d in demo_data.iterrows()])
    dlat=np.squeeze(dlat)
    dlong=np.squeeze(dlong)
    
    
    fig = px.scatter_mapbox(proposal_data,
                            lat="Lattitude", lon="Longitude", hover_name="Name",
                            color_discrete_sequence=["green"])

    fig.add_scattermapbox(lat=site_data["lat"], lon=site_data["long"], hovertext=site_data["UO Site ID"],marker_color='blue')

    bc=[d.boundary.xy for d in demo_data['geometry']]
    fig.add_choroplethmapbox(locations=bc)

    
    fig.add_scattermapbox(lat=dlat, lon=dlong, hovertext=["Population Site"]*len(dlat),marker_color='red')


    fig.update_layout(mapbox_style="carto-positron")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()

    
    
