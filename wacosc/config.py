def to_float_with_max(v, m):
    return float(v) / (m - 1)


def closest(_l, n):
    return _l[min(range(len(_l)), key=lambda i: abs(_l[i] - n))]


def by_float_steps(v, count, _max):
    return closest(
        [i * 1 / (count - 1) for i in range(count)],
        to_float_with_max(v, _max),
    )


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


stylus = {
    'prefix': 'stylus',
    'x': {
        'plugin_name': 'Noize Mak3r',
        'parameter_name': 'osc1tune',
        'fn': lambda v: to_float_with_max(v, 31500),
    },
    'tilt_x': {
        'plugin_name': 'Noize Mak3r',
        'parameter_name': 'oscmastertune',
        'fn': lambda v: to_float_with_max(v + 64, 128)
    },
    'y': {
        'plugin_name': 'Noize Mak3r',
        'parameter_name': 'osc2tune',
        'fn': lambda v: to_float_with_max(v, 19685),
    },
    'tilt_y': {
        'plugin_name': 'Noize Mak3r',
        'parameter_name': 'transpose',
        'fn': lambda v: to_float_with_max(v + 64, 128),
    },
    'distance': {
        'plugin_name': 'Noize Mak3r',
        'parameter_name': 'osc2waveform',
        'fn': lambda v: by_float_steps(v, count=5, _max=64),
    },
    'pressure': {
        'plugin_name': 'Noize Mak3r',
        'parameter_name': 'osc1waveform',
        'fn': lambda v: by_float_steps(v, count=3, _max=2048)
    },
}
pad = {
    'prefix': 'pad',
    'touchring': {
        'plugin_name': 'Noize Mak3r',
        'parameter_name': 'osc2fm',
        'fn': normalize_touchring,
    }
}

touch = {
    'prefix': 'touch',
    'x': {
        'plugin_name': 'rkr NoiseGate',
        'parameter_name': 'Lowpass Filter',
        'fn': lambda v: to_float_with_max(v, 4096),
    },
    'y': {
        'plugin_name': 'rkr NoiseGate',
        'parameter_name': 'Highpass Filter',
        'fn': lambda v: to_float_with_max(v, 4096),
    },
    '0': {
        'x': {
            'plugin_name': 'dRowAudio. Distortion Shaper',
            'parameter_name': 'x1',
            'fn': lambda v: to_float_with_max(v, 4096),
        },
        'y': {
            'plugin_name': 'dRowAudio. Distortion Shaper',
            'parameter_name': 'y1',
            'fn': lambda v: abs(to_float_with_max(v, 4096) - 1),
        },
    },
    '1': {
        'x': {
            'plugin_name': 'dRowAudio. Distortion Shaper',
            'parameter_name': 'x2',
            'fn': lambda v: to_float_with_max(v, 4096),
        },
        'y': {
            'plugin_name': 'dRowAudio. Distortion Shaper',
            'parameter_name': 'y2',
            'fn': lambda v: abs(to_float_with_max(v, 4096) - 1),
        },
    },
}
