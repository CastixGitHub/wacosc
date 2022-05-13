import liblo


TOUCHRING_MODE = 'rotated'


class MagicHandler:
    def __init__(self, osc, kind, key, value):
        self.osc = osc
        self.kind = kind  # eg stylus
        self.key = key  # eg tilx_x
        self.value = value

    def normalize_value(self, value):
        # see issue #3 https://framagit.org/castix/wacosc/-/issues/3
        if self.kind == 'stylus':
            if self.key == 'x':
                return float(value) / 31500
            elif self.key == 'y':
                return float(value) / 19685
            elif self.key == 'pressure':
                return float(value) / 2047
            elif self.key == 'distance':
                return float(value) / 63
            elif self.key in ('tilt_x', 'tilt_y'):
                return float(value + 64) / 127
        # elif self.kind == 'pad':
        #     # TODO: I didn't write the rotated values and I don't mind do math to guess them
        #     # and i don't mind creating the straight mode right now
        #     if self.key == 'touchring':
        #         if TOUCHRING_MODE == 'rotated':
        #             if value == 0:
        #                 return memoized_touchring
        #             elif 56 <= value <= 65:
        #                 return 0.0
        #             elif 47 <= value <= 55:
        #                 return 1.0
        #             elif
        elif self.kind == 'touch':
            return float(value) / 4095
        return value

    @staticmethod
    def normalized_to_midi(value):
        return value * 128

    def __call__(self, value):
        """Here's where the magic happens"""
        value = self.normalize_value(value)

        plugin_name = self.value['plugin_name']
        plugin = self.osc.plugin_by_name(plugin_name)
        parameter_name = self.value['parameter_name']
        parameter_id = plugin['sad_name'][parameter_name]

        liblo.send(
            self.osc.carla_addr_udp,
            f'/Carla/{plugin["_id"]}/set_parameter_value',
            parameter_id,
            value,
        )
