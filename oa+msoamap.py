
import geopandas as gpd
import pandas as pd
from p_tqdm import p_map
import tqdm,os
import numpy as np 
import shapely
import warnings
from shapely.errors import ShapelyDeprecationWarning
warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning) 

generate=True
presimplify = False

if generate:
    areas = gpd.read_file('zip://data/Output_Areas__December_2011__Boundaries_EW_BGC.zip')
    areas.set_index('OA11CD',inplace=True)

    msoa = gpd.read_file('data/msoa.geojson')
    lsoa = gpd.read_file('data/lsoa.geojson')
    oa = gpd.read_file('data/oa.geojson')
    
    msoa['k'] = 2
    lsoa['k'] = 1
    oa['k'] = 0

    msoa['id'] = msoa.msoa11cd
    lsoa['id'] = lsoa.lsoa11cd
    oa['id'] = oa.OA11CD

    oa.append(lsoa)['id k geometry'.split()].append(msoa)['id k geometry'.split()].to_file('data/centroids.geojson',driver='GeoJSON')

    areas.index.name='oa'
    areas.reset_index(inplace=True)

    areas['geometry oa'.split()].to_file('data/geodraw.geojson',driver='GeoJSON')

# -------------
    mapping = pd.read_csv('data/lookup.csv',index_col=0)

    mmap = mapping.groupby('msoa').apply(lambda x: x.lsoa.values)
    lmap = mapping.groupby('lsoa').apply(lambda x: x.oa.values)

    mlook = msoa[['geometry','id']]
    mlook['children'] = ['-'.join(set(mmap.loc[x])) for x in mlook.id]

    llook = lsoa[['geometry','id']]
    llook['children'] = ['-'.join(set(lmap.loc[x])) for x in llook.id]

    # lookups = mlook.append(llook)
    # lookups.to_file('data/encoding_lookups.geojson',driver='GeoJSON')

    mlook.to_file('data/emsoa.geojson',driver='GeoJSON')
    llook.to_file('data/elsoa.geojson',driver='GeoJSON')


import sys 
sys.exit()



import os 



args = '--reverse --detect-shared-borders --reorder --attribution="ONS Visual 2022 Dan Ellis"  -z15 -Z9 --progress-interval=5 --no-tile-size-limit'

tileset = "./geodraw_tileset"
# Error {message: 'Unimplemented type: 3'} : use --no-tile-compression
cmd = f'tippecanoe {args} --no-tile-compression --output-to-directory="{tileset}" --read-parallel --force data/geodraw.geojson' #  centroids.geojson
# --exclude-all --read-parallel

print('go go go ')
os.system(f'rm -rf ./{tileset}/')

os.system(cmd)


#  sepearte tileset for encoding
print('centroid tileset')
cmd = f'tippecanoe --attribution="ONS Visual 2022 Dan Ellis"  -z13 -Z7 --progress-interval=5 --no-tile-size-limit  --output-to-directory="{tileset}/encoding" --force data/emsoa.geojson data/elsoa.geojson' # 
os.system(cmd)




# print tileset info
import json

data = json.loads(open(tileset+'/metadata.json', 'r').read())
info =json.loads(data['json'])
print('----------------')
for layer in info['vector_layers']:
    print(layer)




print('''nested''')
data = json.loads(open(tileset+'/encoding'+'/metadata.json', 'r').read())
info =json.loads(data['json'])
print('----------------')
for layer in info['vector_layers']:
    print(layer)
j




# -----------------
import glob,re,json,os

f = glob.glob(tileset+'/encoding/*/*/*.pbf')
zxy = re.compile(r'(\d+)[/\.]')


def pbf2clean(fl):
    z,x,y  = zxy.findall(fl)

    items = json.loads(os.popen(f'tippecanoe-decode {fl} {z} {x} {y}').read())
    data = {}
    for layer in items['features']:
        name = layer['properties']['layer'][1:]
        it = [[x['properties']['id'],x['properties']['children'].split('-')] for x in layer['features']]
        data[name] = it

    json.dump(data,open(fl.replace('pbf','json'),'w'))


p_map(pbf2clean,f)



'''




def longest_common(x):
        arr = np.array(x)
        arr.sort()
        result = ""
        # Compare the first and the last string character
        # by character.
        for i in range(len(arr[0])):
            #  If the characters match, append the character to
            #  the result.
            if arr[0][i] == arr[-1][i]:
                result += arr[0][i]
            # Else, stop the comparison
            else:
                break

        return result

    # mapping = pd.read_csv('PCD11_OA11_LSOA11_MSOA11_LAD11_EW_LU_aligned_v2.csv',index_col=0)
    # mapping['split'] = [i.split()[0] for i in mapping.PCD8]
    # mapping.groupby('LAD11NM').apply(lambda x:set(x.split) ).to_json('postcodemap.json')

    # revmap = dict(zip(mapping.OA11CD,mapping.MSOA11CD))


# os.system('tippecanoe-json-tool --extract=msoa -e=lad geodraw_pre.geojson ')
# args = '--coalesce --reverse --detect-shared-borders --reorder --attribution="ONS Visual 2022 Dan Ellis"  -zg --progress-interval=5 --no-tile-size-limit --use-attribute-for-id=oa'
# --name="OA mapping" --clip-bounding-box=-7.57216793459,49.959999905,1.68153079591,58.6350001085 --no-feature-limit --no-tile-size-limit


    def populate(x):
        try:return revmap[x]
        except:return np.nan

    areas['msoanm'] = areas.index.map(populate)

    
    
    areas.sort_values(by=['LAD11CD','msoanm','oa'],inplace=True)
    
    areas['lad']= pd.Categorical(areas.LAD11CD).codes
    areas['msoa'] = pd.Categorical(areas.msoanm).codes
    areas['oacat']= pd.Categorical(areas.oa).codes
    # areas.set_index('oa',inplace=True) 



    if presimplify:
        print('simplifying')
        import topojson as tp
        import shapely
        import warnings
        from shapely.errors import ShapelyDeprecationWarning
        warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning) 

        areas = tp.Topology(areas, toposimplify=4 ,prevent_oversimplify=True).to_gdf()

    print('writing to file')
    areas.to_file('complete.geojson',driver='GeoJSON')

    areas['geometry oa'.split()].to_file('geodraw.geojson',driver='GeoJSON')

'''
