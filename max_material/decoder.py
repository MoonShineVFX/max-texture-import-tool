import json
from .max_object import MaxObject


class MaxMaterialDecoder:
    def __init__(self, path):
        self._path = path
        self._data = None
        self._load_file()

    def _load_file(self):
        with open(self._path, 'r') as f:
            self._data = json.load(f)

    def get_texture(self):
        texture_dict = {}
        for material_name, material_data in self._data.items():
            material = MaxObject({material_name: material_data})
            texture_dict[material_name] = material.get_texture()

        return texture_dict
