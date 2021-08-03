import pickle
import csv

site_data= pickle.load(open('distance_analysis.pk','rb'))
header=['uo_site_id','Population_Assigned','Average_Drivetime','DT to Proposal','Proposal Number',"Sites Per County in Optimization"]


writer=csv.writer(open('flp_data.csv','w'),delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer.writerow(header)
rows=[]
site_list=[]
for county in site_data.values():
    for k in county:
        for site in county:
            if site['uo_site_id'] not in site_list:
                rows.append([site[val] for val in header ])
                site_list.append( site['uo_site_id'])
            else:
                continue
for row in rows:
    writer.writerow(row)
            
