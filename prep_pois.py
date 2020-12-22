import pickle
import numpy as np
from shapely.geometry.point import Point
from shapely.geometry.polygon import Polygon


pois=pickle.load(open('Marion County_POIS.pk','rb'))

poi=[]
points=[]
for df in pois:
    for index,r in df.iterrows():
        geo=r['geometry']
        if type(geo)==Point:
            point=geo.xy
        elif type(geo)==Polygon:
            point=np.mean(geo.exterior.coords.xy,axis=0)
        else:
            continue
        print(len(points))
        points.append(point)
        names.append(r.name)


