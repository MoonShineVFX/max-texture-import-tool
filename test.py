from max_material import MaxMaterialDecoder
import json


test_path = 'import/ShanghaiCity.tower.v001.json'
decoder = MaxMaterialDecoder(test_path)
data = decoder.get_texture()

print(json.dumps(data, indent=4, sort_keys=True))
