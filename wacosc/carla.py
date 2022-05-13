"""WacOsc carla.py - where handlers are defined."""
from wacosc.plugins import ranges
from wacosc.config import stylus, pad, touch
import liblo
import atexit


# Carla callback opcodes
# https://github.com/falkTX/Carla/blob/2a6a7de04f75daf242ae9d8c99b349ea7dc6ff7f/source/backend/CarlaBackend.h
ENGINE_CALLBACK_PLUGIN_ADDED = 1
ENGINE_CALLBACK_PLUGIN_REMOVED = 2
ENGINE_CALLBACK_PARAMETER_VALUE_CHANGED = 5


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


# based on https://github.com/wvengen/lpx-controller/blob/561b5db81d0a9136d529e4262016345a255d95e8/sequencer.py that was
# based on https://github.com/dsacre/mididings/blob/master/mididings/extra/osc.py
class OSCInterface:
    plugins = {}

    def __new__(cls, stylus, pad, touch):
        obj = super().__new__(cls)
        for key, value in stylus.items():
            setattr(obj, f'on_stylus_{key}', MagicHandler(obj, 'stylus', key, value))
        for key, value in pad.items():
            setattr(obj, f'on_pad_{key}', MagicHandler(obj, 'pad', key, value))
        for key, value in touch.items():
            setattr(obj, f'on_touch_{key}', MagicHandler(obj, 'touch', key, value))
        return obj

    def __init__(self, carla_port=22752, listen_port=22755):  # TODO find free listen port
        self.carla_addr_tcp = liblo.Address('127.0.0.1', carla_port, proto=liblo.TCP)
        self.carla_addr_udp = liblo.Address('127.0.0.1', carla_port, proto=liblo.UDP)
        self.listen_port = listen_port
        self.on_start()
        atexit.register(self.on_exit)

    def on_start(self):
        print('starting osc')
        self.server_tcp = liblo.ServerThread(self.listen_port, proto=liblo.TCP)
        self.server_tcp.register_methods(self)
        self.server_tcp.start()
        self.server_udp = liblo.ServerThread(self.listen_port, proto=liblo.UDP)
        self.server_udp.register_methods(self)
        self.server_udp.start()
        liblo.send(self.carla_addr_tcp, '/register', 'osc.tcp://127.0.0.1:%d/Carla' % self.listen_port)
        liblo.send(self.carla_addr_udp, '/register', 'osc.udp://127.0.0.1:%d/Carla' % self.listen_port)
        # TODO query all current parameter values to set all buttons to the correct value

    def on_exit(self):
        # Registering with the full URL gives an error about the wrong owner, just the IP-address seems to work.
        # liblo.send(self.carla_addr_tcp, '/unregister', 'osc.tcp://127.0.0.1:%d/Carla' % self.listen_port)
        # liblo.send(self.carla_addr_udp, '/unregister', 'osc.udp://127.0.0.1:%d/Carla' % self.listen_port)
        liblo.send(self.carla_addr_udp, '/unregister', '127.0.0.1')
        self.server_udp.stop()
        del self.server_udp
        liblo.send(self.carla_addr_tcp, '/unregister', '127.0.0.1')
        self.server_tcp.stop()
        del self.server_tcp

    @liblo.make_method('/Carla/info', 'iiiihiisssssss')
    def on_carla_info(self, path, args):
        print('INFO', path, args)

    @liblo.make_method('/Carla/cb', 'iiiiifs')
    def on_carla_cb(self, path, args):
        # https://github.com/falkTX/Carla/blob/de8e0d3bd9cc4ab76cbea9f53352c92d89266ea2/source/frontend/carla_control.py#L337
        action, plugin_id, value1, value2, value3, valuef, value_str = args
        print('CB', path, args)
        if action == ENGINE_CALLBACK_PLUGIN_ADDED:
            self.plugins[plugin_id] = {
                'name': value_str,
                'ranges': ranges[value_str],
            }
            if value_str == 'Noize Mak3r':
                self.note_on(plugin_id)  # immediatly make noize!
        elif action == ENGINE_CALLBACK_PLUGIN_REMOVED:
            del self.plugins[plugin_id]

        print(self.plugins)

    def plugin_by_name(self, name):
        for _id, _dict in self.plugins.items():
            if _dict['name'] == name:
                _dict = _dict.copy()
                _dict['_id'] = _id
                return _dict

    def note_on(self, plugin_id, note=60, velocity=127):
        liblo.send(
            self.carla_addr_tcp,
            f'/Carla/{plugin_id}/note_on',
            plugin_id, note, velocity
        )


carla = OSCInterface(stylus, pad, touch)


if __name__ == '__main__':
    print(carla.plugins)
