import censusdata
import geopandas as gpd

#states = censusdata.geographies(censusdata.censusgeo([('state', '41'),'county','*']), 'acs5', 2019)


oregon_data = censusdata.download('acs5', 2019,censusdata.censusgeo([('state', '41'),('county','*'),('block group','*')]),['B03002_012E'])
oregon_maps=gpd.read_file("census_maps/cb_2019_41_bg_500k.shp")


assert(len(oregon_data)==len(oregon_maps)) 

lookup_dict={}
for i in range(len(oregon_data)):
    tract=oregon_data.index[i].geo[2][1]
    block_group=oregon_data.index[i].geo[3][1]
    lookup_dict[(tract,block_group)]=i

data=[]
for i in range(len(oregon_maps)):
    pop=lookup_dict[(oregon_maps['TRACTCE'][i],oregon_maps['BLKGRPCE'][i])]
    data.append(pop)

oregon_maps['Hispanic']=data
oregon_maps.to_pickle('oregon_data.pk')
oregon_data.to_pickle('oregon_census_data.pk')


