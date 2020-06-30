from max_material import MaxMaterialDecoder
import json
import os


os.environ['mi_debug'] = 'true'
test_path = 'c:/users/moonshine/Desktop/demo/ShanghaiCity.v69.cleanup.json'

decoder = MaxMaterialDecoder(test_path)
data = decoder.get_texture()

print('textures are:')
print(json.dumps(data, indent=4, sort_keys=True))
