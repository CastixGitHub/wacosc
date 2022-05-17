import liblo


def to_float_with_max(v, m):
    return float(v) / (m - 1)


memoized_touchring = 0.0


def normalize_touchring(v):
    global memoized_touchring  # pylint: disable=global-statement
    if v == 0:
        return memoized_touchring
    if 0 <= v <= 12:
        memoized_touchring = 0.0
        return 0.0
    if 66 <= v <= 71:
        memoized_touchring = 1.0
        return 1.0
    memoized_touchring = to_float_with_max(v - 12, 66 - 12)
    return to_float_with_max(v - 12, 66 - 12)


normalizing_functions = {
    'stylus.x': lambda v: to_float_with_max(v, 31500),
    'stylus.y': lambda v: to_float_with_max(v, 19685),
    'stylus.pressure': lambda v: to_float_with_max(v, 2048),
    'stylus.distance': lambda v: to_float_with_max(v, 64),
    'stylus.tilt_x': lambda v: to_float_with_max(v + 64, 128),
    'stylus.tilt_y': lambda v: to_float_with_max(v + 64, 128),
    'pad.touchring': normalize_touchring,
    'touch.x': lambda v: to_float_with_max(v, 4096),
    'touch.y': lambda v: to_float_with_max(v, 4096),
}


class MagicHandler:
    def __init__(self, osc, kind, key, value):
        self.osc = osc
        self.kind = kind  # eg stylus
        self.key = key  # eg tilx_x
        self.value = value

    def normalize_value(self, value):
        # see issue #3 https://framagit.org/castix/wacosc/-/issues/3
        return normalizing_functions.get(f'{self.kind}.{self.key}', lambda v: v)(value)

    @staticmethod
    def normalized_to_midi(value):
        return value * 128

    def __call__(self, value):
        """Here's where the magic happens"""
        if not isinstance(value, dict):
            value = float(value)  # even for raw
        else:  # multitouch event
            print('multitouch', value)
            return
        try:
            plugin_name = self.value['plugin_name']
            plugin = self.osc.plugin_by_name(plugin_name)
            if plugin is None:
                return
            parameter_name = self.value['parameter_name']
            parameter_id = plugin['ranges']['sad_name'][parameter_name]

            if 'raw' != self.value['expected_value_kind']:
                value = self.normalize_value(value)
            if 'midi' == self.value['expected_value_kind']:
                value = self.normalized_to_midi(value)
        except Exception as e:
            print(str(e))

        liblo.send(
            self.osc.carla_addr_udp,
            f'/Carla/{plugin["_id"]}/set_parameter_value',
            parameter_id,
            value,
        )
