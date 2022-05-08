import lilv

# first of all we load all the lv2 plugins on the system
# in order to determine default, minimum and max of all parameters
w = lilv.World()
w.load_all()
ranges = {}
for pl in w.get_all_plugins():
    ranges[str(pl.get_name())] = {
        str(pl.get_port(n).get_name()):
        [float(v) for v in pl.get_port(n).get_range() if v is not None and v.is_float()]
        for n in range(pl.get_num_ports())
    }


# sadness is due to difference between lv2 "parameter id" and carla parameter id.
ranges['Noize Mak3r']['sad_name'] = {
    'osc1tune': 20,
    'osc1finetune': 22,
    'osc2tune': 21,
    'osc2finetune': 23,
}
