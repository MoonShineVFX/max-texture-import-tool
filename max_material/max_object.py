# -*- coding: UTF-8 -*-

class MaxObject:
    def __init__(self, data, layer=0):
        self._name = None
        self._data = None
        self._layer = layer

        if len(data.keys()) == 1:
            self._name, self._data = data.items()[0]
        else:
            self._data = data

        if not self.is_color():
            self._log('[{}:{}]'.format(self.get_class(), self._name))

    def _log(self, msg, newline=True):
        msg = msg.rjust(self._layer * 2 + len(msg))
        print(msg)

    def is_color(self):
        return self._name == 'color'

    def get_super_class(self):
        return self._data['max_superclass']

    def get_class(self):
        if self.is_color():
            return 'color'
        return self._data['max_class']

    def get_texture(self):
        # color
        if self.is_color():
            return self._get_end('color', self._data)

        super_class = self.get_super_class()
        this_class = self.get_class()

        # material
        if super_class == 'material':
            # VrayMtl
            if this_class == 'VRayMtl':
                return self._get_texture_from_fields('texmap_diffuse', 'diffuse')

            # VrayBlendMtl
            if this_class == 'VRayBlendMtl':
                return self._get_texture_from_fields('baseMtl')

            # Multimaterial
            if this_class == 'Multimaterial':
                material_list = self._data['materialList']['material_array']
                return self._get_end(
                    'multi',
                    [
                        self._get_texture_from_value(mat)
                        for mat in material_list
                    ]
                )

        # textureMap
        if super_class == 'textureMap':
            # VRayDistanceTex
            if this_class == 'VRayDistanceTex':
                return self._get_texture_from_fields(
                    'texmap_near', 'texmap_far', 'texmap_inside', 'texmap_outside',
                    'near_color', 'far_color', 'inside_color', 'outside_color'
                )

            # Noise
            if this_class == 'Noise':
                return self._get_texture_from_fields(
                    'map1', 'map2', 'color1', 'color2'
                )

            # Dent
            if this_class == 'Dent':
                return self._get_texture_from_fields(
                    'map1', 'map2', 'color1', 'color2'
                )

            # Mix
            if this_class == 'Mix':
                return self._get_end(
                    'mix',
                    {
                        'map1': self._get_texture_from_fields(
                            'map1', 'color1'
                        ),
                        'map2': self._get_texture_from_fields(
                            'map2', 'color2'
                        ),
                        'mask': self._get_texture_from_fields(
                            'mask'
                        )
                    }
                )

            # VRayHDRI
            if this_class == 'VRayHDRI':
                return self._get_end(
                    'hdri',
                    self._data['HDRIMapName']['filename']
                )

            # Bitmap
            if this_class == 'Bitmaptexture':
                return self._get_end('bitmap', self._data['fileName']['filename'])

            # CompositeTexturemap
            if this_class == 'CompositeTexturemap':
                tex = self._data['mapList']['texturemap_array'][0]
                return self._get_texture_from_value(tex)

            # VRayColor
            if this_class == 'VRayColor':
                return self._get_texture_from_fields('color')

        raise ValueError(
            'Unable to get_texture: {} - {}'.format(
                self.get_super_class(),
                self.get_class()
            )
        )

    def _get_texture_from_fields(self, *fields):
        for field in fields:
            field_value = self._data[field]
            if field_value is not None:
                self._log('└ {}'.format(field))
                return self._get_texture_from_value(field_value)
        raise ValueError(
            'Unable to get_texture_from_fields: {} - {} - {}'.format(
                self.get_super_class(),
                self.get_class(),
                fields
            )
        )

    def _get_end(self, map_type, value):
        object = {
            'type': map_type,
            'value': value
        }
        self._log('  <{}>'.format(map_type))
        return object

    def _get_texture_from_value(self, field):
        return MaxObject(field, self._layer + 1).get_texture()