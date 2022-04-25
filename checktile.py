import mapbox_vector_tile
import glob


tileset = 'geodraw_tileset'
# tileset = '../LSOA'
f = glob.glob(tileset+'/*/*/*.pbf')

# with open(f[0], 'rb') as f:
#     data = f.read()

# decoded_data = mapbox_vector_tile.decode(data)
# # with open('out.txt', 'w') as f:
# #     f.write(repr(decoded_data))

# print('decoded')
# print(decoded_data)

import json

data = json.loads(open(tileset+'/metadata.json', 'r').read())
info =json.loads(data['json'])

print(info['vector_layers'])
