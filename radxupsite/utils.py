import os
import censusdata
import pkg_resources
import pickle
from openpyxl import Workbook,load_workbook


def get_state_blkgrp_fname(state_code,year):
    return 'cb_'+str(year)+'_'+state_code+'_bg_500k.zip'

def get_state_blkgrp_shp(state_code,year):
    return 'cb_'+str(year)+'_'+state_code+'_bg_500k.shp'

def get_blkgrp_map_link(state_code,year):
    fname=get_state_blkgrp_fname(state_code,year)
    return 'https://www2.census.gov/geo/tiger/GENZ'+str(year)+'/shp/'+fname

def get_county_shortname(county):
    search=county.lower().find('county')
    if search == -1:
        return county.lower()
    else:
        return county[:search-1].lower()
    
def get_county_data_dir(state,county):
    _county=get_county_shortname(county)
    _state=state.lower()
    fname=pkg_resources.resource_filename(__name__, "data/"+_state+'/'+_county+'/')
    return fname

def get_county_demodir(state,county,year,census_var):
    _dir=os.path.join(get_county_data_dir(state,county),str(year),census_var)
    return _dir


def get_county_demodata(state,county,year,census_var):
    _dir=get_county_demodir(state,county,year,census_var)
    fname=_dir+'/demographics.pk'
    return fname
 
def get_county_optdata(state,county,year,censusvar,n_sites):
    _dir=get_county_data_dir(state,county)
    fname=_dir+'opt_'+'_'.join([year,censusvar,str(n_sites)])+'.pk'
    return fname

def get_county_htmldata(state,county,n_sites):
    _dir=get_county_data_dir(state,county)
    fname=_dir+'map_'+str(n_sites)+'.html'
    return fname


def get_county_graphdata(state,county):
    _dir=get_county_data_dir(state,county)
    fname=_dir+'graph.pk'
    return fname

def get_county_poidata(state,county):
    _dir=get_county_data_dir(state,county)
    fname=_dir+'poi.pk'
    return fname





def get_state_data_dir(state):
    _state=state.lower()
    fname=pkg_resources.resource_filename(__name__, "data/"+_state+'/')
    return fname



def search_censusdata(search_str,search_data):
    "Searches geographie names for a string and returns the associated census code"
    matchs=[]
    for i,s in enumerate(search_data):
        if search_str.lower() in s.lower():
            matchs.append(s)
    if len(matchs)==0:
        raise Exception(search_str+' No Search Value Found Options:\n'+'\n'.join(search_data.keys()) )
    elif len(matchs)!=1:
        raise Exception(search_str+' Mulitple Search Found Options:\n'+'\n'.join(search_data.keys()) )
    return matchs[0]
    

def lookup_statecode(search_str, year):
    """A function to find the census code a name from a search string of a state and a given year"""
    search_data=censusdata.geographies(censusdata.censusgeo([('state', '*')]), 'acs5', year)
    match=search_censusdata(search_str,search_data)
    state_code=search_data[match].geo[0][1]
    return match,state_code


def lookup_countycode(state_code,search_str,year):
    """A function to find the name and census code from the full name of a county and a given a state and year"""
    search_data=censusdata.geographies(censusdata.censusgeo([('state', state_code),('county','*')]), 'acs5', year)
    match=search_censusdata(search_str,search_data)
    county_code=search_data[match].geo[1][1]
    return match,county_code

def get_cell_value(cell):
    """Returuns string from openpyxl cell in proper format for esp              
       converts datetime to yyyy-mm-dd                                          
       converts None to ''                                                      
    """

    if cell.value==None:return ''
    elif type(cell.value) == datetime:
        return cell.value.strftime("%Y-%m-%d")
    else:
        return str(cell.value)

def read_xlsx(in_file,data=None):                                               
    """                                                                         
    This function reads an excel file it returns a list of each row as a dictio\
nary                                                                            
     with keys equal to the excel headers and values equal to string formated c\
ell contents                                                                    
    """                                                                         
    if data == None:
        data=[]
    workbook = load_workbook(filename=in_file)
    sheet = workbook.active
    header=None
    for xrow in sheet.rows:
        row=[get_cell_value(i) for i in xrow]
        if all([v=='' for v in row]):
            continue #drop blanck lines                                         
        if header == None:
            header=row
        else:
            assert(len(row)==len(header))
            data_dict={}
            for key,val in zip(header,row):
                data_dict[key.strip()]=val.replace("\n"," ")
            data.append(data_dict)

    return data

