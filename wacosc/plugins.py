"""WacOsc plugins.py - exposes ranges dictionary."""
from sys import stderr
from os import getenv
import lilv

# first of all we load all the lv2 plugins on the system
# in order to determine default, minimum and max of all parameters
ranges = {}
if not getenv('SKIP_LILV', None):
    w = lilv.World()
    w.load_all()
    for pl in w.get_all_plugins():
        ranges[str(pl.get_name())] = {
            str(pl.get_port(n).get_name()):
            [float(v) for v in pl.get_port(n).get_range() if v is not None and v.is_float()]
            for n in range(pl.get_num_ports())
        }


# sadness is due to difference between lv2 "parameter id" and carla parameter id.
ranges.setdefault('Noize Mak3r', {})['sad_name'] = {
    'osc1tune': 20,
    'osc1finetune': 22,
    'osc1waveform': 24,
    'osc2tune': 21,
    'osc2finetune': 23,
    'osc2waveform': 25,
    'oscmastertune': 19,
    'transpose': 41,
    'osc2fm': 37,
    'volume': 2,
}

ranges.setdefault('rkr NoiseGate', {})['sad_name'] = {
    'Lowpass Filter': 5,
    'Highpass Filter': 6,
}

# honestly, lv2 says it's "dRowAudio: Distortion Shaper" but carla prefers '.' instead for some reason...
ranges.setdefault('dRowAudio. Distortion Shaper', {})['sad_name'] = {
    'x1': 5,
    'y1': 6,
    'x2': 7,
    'y2': 8,
}


if __name__ == '__main__':
    from sys import argv
    import json
    if len(argv) > 1:
        try:
            printing = ranges[argv[1]]
        except KeyError:
            print(argv[1],  'not found', file=stderr)
            printing = {}
    else:
        printing = ranges
    print(json.dumps(printing, indent=4))
