import csv
import os
from openpyxl import Workbook,load_workbook
from datetime import datetime

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
    This function reads an excel file it returns a list of each row as a dictionary                                                                        
     with keys equal to the excel headers and values equal to string formated cell contents                                                                
    """

    if data == None:
        data=[]

    workbook = load_workbook(filename=in_file)
    sheet = workbook.active
    header=None
    creation_time=datetime.fromtimestamp(os.path.getctime(in_file))


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
            data_dict['_ctime']=creation_time
            data.append(data_dict)

    return data

