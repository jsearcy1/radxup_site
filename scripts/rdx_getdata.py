#!/usr/bin/env python
import argparse
from radxupsite import utils
import pkg_resources
import os
import wget
import osmnx as ox
import censusdata
import geopandas as gpd
from zipfile import ZipFile
import pickle
from shapely.geometry.point import Point
from shapely.geometry.polygon import Polygon
import numpy as np

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('state', metavar='S', type=str, 
                    help='State')
parser.add_argument('county', metavar='C', type=str,
                    help='County')
parser.add_argument('censusvar', metavar='V', type=str,
                    help='Census Population Variable i.e. B03002_012E')
parser.add_argument('--year', metavar='year', type=int, default=2019,
                    help='Year used for census data')


args = parser.parse_args()
state_name,state_code=utils.lookup_statecode(args.state,args.year)
county_name,county_code=utils.lookup_countycode(state_code,args.county,args.year)

county_data_directory=utils.get_county_data_dir(state_name,county_name)
state_data_directory=utils.get_state_data_dir(state_name)

demo_directory=utils.get_county_demodir(state_name,county_name,args.year,args.censusvar)
demo_file=utils.get_county_demodata(state_name,county_name,args.year,args.censusvar)


if not os.path.exists(county_data_directory):
    os.makedirs(county_data_directory)

if not os.path.exists(state_data_directory):
    os.makedirs(state_data_directory)

if not os.path.exists(demo_directory):
    os.makedirs(demo_directory)


if os.path.exists(demo_file):
    print('Found Demographic Data:',demo_file,'\n Continuing')
else:  

    map_fname=utils.get_state_blkgrp_fname(state_code,args.year)
    map_file=os.path.join(state_data_directory,map_fname)

    shp_fname=utils.get_state_blkgrp_shp(state_code,args.year)

    if not os.path.exists(map_file):
        print('No GIS data found Attempting to download Block Group GIS data')
        url=utils.get_blkgrp_map_link(state_code,args.year)
        print(url)
        wget.download(url,out=map_file)
    
        zf=ZipFile(map_file)
        zf.extractall( path=state_data_directory+'/blkgrp/', pwd=None)
    else:
        print(map_file)
        print('Using Existing state GIS data')
     
    map_data=gpd.read_file(state_data_directory+'/blkgrp/'+shp_fname)

    print('Requesting Census Data')
    population_data = censusdata.download('acs5', args.year,censusdata.censusgeo([('state', state_code) ,('county',county_code),('block group','*')]),[args.censusvar])
    
    lookup_dict={}
    for i in range(len(population_data)):
        tract=population_data.index[i].geo[2][1]
        block_group=population_data.index[i].geo[3][1]
        lookup_dict[(tract,block_group,county_code)]=i
    data=[]
    selections=[]
    for i in range(len(map_data)):
        key=(map_data['TRACTCE'][i],map_data['BLKGRPCE'][i],map_data['COUNTYFP'][i])
        if key in lookup_dict:
            index=lookup_dict[key]
            pop=population_data.iloc[index][args.censusvar]
            if pop==0:
                continue
            selections.append(i)
            data.append(pop)
            
    geo_df=(map_data.iloc[selections]).copy()
    assert(len(geo_df)==sum(population_data[args.censusvar]!=0))
    geo_df['Population']=data
    geo_df.to_pickle(demo_file)



graph_file=utils.get_county_graphdata(state_name,county_name)

if not os.path.exists(graph_file):
    print('Downloading Street Graph')
    graph=ox.graph_from_place(county_name,network_type='drive',buffer_dist=50000)
    graph = ox.add_edge_speeds(graph)
    graph = ox.add_edge_travel_times(graph)
    with open(graph_file,'wb') as out_file:
        pickle.dump(graph,out_file)
else:
    print('Street Graph Found Continuing')
        

poi_file=utils.get_county_poidata(state_name,county_name)

if not os.path.exists(poi_file):
    print('Downloading Points of Interest')
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
            df=ox.geometries_from_place(county_name,tags={'leisure':'park'})
        else:
            df=ox.geometries_from_place(county_name,tags={'amenity':am})
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
    with open(poi_file,'wb') as out_file:
        pickle.dump([points,names,pois],out_file)
else:
    print('Points of Interest Data Found')

print('Finished')

        
