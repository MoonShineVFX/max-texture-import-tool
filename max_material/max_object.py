# -*- coding: UTF-8 -*-
import json
import os


IN_MULTI = False


class MaxObject:
    def __init__(self, data, layer=0):
        self._name = None
        self._data = None
        self._layer = layer

        self._is_debug = os.getenv('mi_debug', False) == 'true'

        if len(data.keys()) == 1:
            self._name, self._data = data.items()[0]
        else:
            self._data = data

        self._log(u'[{}:{}]'.format(self.get_class(), self._name))

    def _log(self, msg):
        if self._is_debug:
            msg = msg.rjust(self._layer * 2 + len(msg))
            print(msg)

    @staticmethod
    def is_color(value):
        if not isinstance(value, dict):
            return False
        return len(value.keys()) == 1 and 'color' in value

    def get_super_class(self):
        return self._data['max_superclass']

    def get_class(self):
        return self._data['max_class']

    def get_texture(self):
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
                global IN_MULTI

                if IN_MULTI:
                    return self._get_texture_from_value(
                        self._data['materialList']['material_array'][0]
                    )
                else:
                    IN_MULTI = True

                idx_list = []
                for d in self._data['materialIDList']['int_array']:
                    idx = d['int'] - 1
                    idx_list.append(idx)

                mat_list = [None] * (max(idx_list) + 1)
                material_list = self._data['materialList']['material_array']
                for idx, mat in zip(idx_list, material_list):
                    mat_list[idx] = self._get_texture_from_value(mat)

                IN_MULTI = False

                return self._get_end(
                    'multi',
                    mat_list
                )

            # Standardmaterial
            if this_class == 'Standardmaterial':
                bool_array = self._data['mapEnables']['boolean_array']
                if bool_array[1]['boolean']:
                    return self._get_texture_from_value(self._data['maps']['texturemap_array'][0])
                if 'diffuse' in self._data:
                    return self._get_texture_from_fields('diffuse')
                return None

            # Blend
            if this_class == 'Blend':
                return self._get_texture_from_fields('map1', 'map2')

            # VRay2SidedMtl
            if this_class == 'VRay2SidedMtl':
                return self._get_texture_from_fields('frontMtl', 'backMtl')

            # VRayLightMtl
            if this_class == 'VRayLightMtl':
                return self._get_texture_from_fields('texmap', 'color')

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
                return self._get_texture_from_fields(
                    'map1', 'color1'
                )

            # VRayHDRI
            if this_class == 'VRayHDRI':
                return self._get_end(
                    'texture',
                    self._data['HDRIMapName']['filename']
                )

            # Bitmap
            if this_class == 'Bitmaptexture':
                return self._get_end(
                    'texture',
                    self._data['fileName']['filename']
                )

            # CompositeTexturemap
            if this_class == 'CompositeTexturemap':
                tex = self._data['mapList']['texturemap_array'][0]
                return self._get_texture_from_value(tex)

            # VRayColor
            if this_class == 'VRayColor':
                return self._get_texture_from_fields('color')

            # Color_Correction
            if this_class == 'Color_Correction':
                return self._get_texture_from_fields('map', 'color')

            # VRayCompTex
            if this_class == 'VRayCompTex':
                return self._get_texture_from_fields('sourceA')

            # VRayEdgesTex
            if this_class == 'VRayEdgesTex':
                return self._get_texture_from_fields('edgesColor')

            # Bricks
            if this_class == 'Bricks':
                return self._get_texture_from_fields('Brick_Color')

            # Stucco
            if this_class == 'Stucco':
                return self._get_texture_from_fields('map1', 'map2', 'color1', 'color2')

            # falloff
            if this_class == 'falloff':
                return self._get_texture_from_fields('map1', 'map2', 'color1', 'color2')

            # RGB_Tint
            if this_class == 'RGB_Tint':
                return self._get_texture_from_fields('map1')

            # VRayDirt
            if this_class == 'VRayDirt':
                return self._get_texture_from_fields('unoccluded_color')


        self._debug_value(self._data)
        raise ValueError(
            u'Unable to get_texture: {} - {} - {}'.format(
                self.get_super_class(),
                self.get_class(),
                self._name
            ).encode('utf-8')
        )

    def _get_texture_from_fields(self, *fields):
        for field in fields:
            field_value = self._data[field]
            if field_value is not None:
                self._log('└ {}'.format(field))
                return self._get_texture_from_value(field_value)
        raise ValueError(
            u'Unable to get_texture_from_fields: {} - {} - {} - {}'.format(
                self.get_super_class(),
                self.get_class(),
                self._name,
                fields
            ).encode('utf-8')
        )

    def _get_end(self, map_type, value):
        if map_type != 'multi':
            value = self.convert_houdini_value(map_type, value)
        object = {
            'class': self.get_class(),
            'type': map_type,
            'value': value
        }
        self._log('  <{}>'.format(map_type))
        return object

    def _get_texture_from_value(self, field):
        if self.is_color(field):
            return self._get_end('color', field['color'])
        return MaxObject(field, self._layer + 1).get_texture()

    @staticmethod
    def convert_houdini_value(map_type, value):
        if map_type == 'texture':
            return json.dumps({
                'basecolor_useTexture': 1,
                'basecolor_texture': value
            })
        elif map_type == 'color':
            return json.dumps({
                'basecolorr': value['r'] / 255,
                'basecolorg': value['g'] / 255,
                'basecolorb': value['b'] / 255,
            })

        raise ValueError('Invalid Map Type')

    def _debug_value(self, value):
        print('-------------------debug-------------------')
        print(json.dumps(value, indent=4))
