import pickle
import csv
from radxupsite import utils
import geopandas as gpd
from shapely.geometry import Point, Polygon

data=pickle.load(open('location_data.pk','rb'))

ldict={
    'MO1':(45.84796991501075, -119.68768076195019),
    'JO3':(42.328480,-123.338110),
    'DO2':(43.388830,-123.333230),
    'DO4':(43.154140,-123.388368),
    'JA1':(42.348418,-122.848955),
    'JA6':(42.191285074459834,-122.70028379016684),
    'MA1':(45.10423508535685,-122.89400147332191),
    'JE2':(44.45996129235466, -121.64909858932194),
    'JO5':(42.30604272018632, -123.20115384914189),
    'MC5':(45.45678454845073, -123.80674319651472)
}

map_data=gpd.read_file('/home/jsearcy/radxup_clean/radxupsite/data/oregon/blkgrp/cb_2019_41_bg_500k.shp')


with open('output_data.csv', 'w', newline='') as csvfile:
    cenfnames=['STATEFP','COUNTYFP','TRACTCE','BLKGRPCE','GEOID']
    site_vars=['UO Site ID','lat','long','inOSM','County','Zipcode']
    fieldnames = site_vars+cenfnames
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for d,l in data:
        if d['UO Site ID'] == '': continue
        new_d={}


        if l != None:
            d['lat']=l.latitude
            d['long']=l.longitude
            d['inOSM']='1'
        else:
            print(d['Address'],d['City'])
            lat,longi=ldict[d['UO Site ID']]
            d['lat']=lat
            d['long']=longi
            d['inOSM']='0'
        p=Point(d['long'],d['lat'])
        matches=[i for i,v in map_data.iterrows() if v.geometry.contains(p)]
        assert(len(matches))==1

        blkgroup=map_data.iloc[matches[0]]
        for key in cenfnames:
            new_d[key]=blkgroup[key]
        for key in site_vars:
            new_d[key]=d[key]
        
        
            
        writer.writerow(new_d)
