from geopy.geocoders import Nominatim
from openpyxl import Workbook,load_workbook
import sys
import datetime
import time
import pickle

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

def get_address_string(d):
   return d['Address']+', '+d['City']+', OR'


rate_limit=5 #Seconds between request
assert rate_limit > 1 #OSM request requirment

data=read_xlsx(sys.argv[1])
address_strings=[get_address_string(d) for d in data]

geolocator = Nominatim(user_agent="rds_ax68In1lp")
out_data=[]
for index,a in enumerate(address_strings):


    location = geolocator.geocode(a)
    out_data.append((data[index],location))
    print(location,a)
    time.sleep(rate_limit)
    


pickle.dump(out_data,open('location_data.pk','wb'))
    

    
#print((location.latitude, location.longitude))
#print(location.raw)
