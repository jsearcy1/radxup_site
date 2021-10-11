import pickle
import csv

site_data= pickle.load(open('distance_analysis.pk','rb'))
header=['UO Site ID','Population_Assigned','Average_Drivetime','DT to Proposal','Proposal Number',"Sites Per County in Optimization","County"]


writer=csv.writer(open('flp_data.csv','w'),delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer.writerow(header)
rows=[]
site_list=[]
for county in site_data.values():
    for k in county:
        for site in county:
            if site['UO Site ID'] not in site_list:
                rows.append([site[val] for val in header ])
                site_list.append( site['UO Site ID'])
            else:
                continue
for row in rows:
    writer.writerow(row)
            
