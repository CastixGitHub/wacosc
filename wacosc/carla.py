"""WacOsc carla.py - where handlers are defined."""
from wacosc.plugins import ranges
from wacosc.magic import MagicHandler
from wacosc.config import stylus, pad, touch
import liblo
import trio
import atexit


# Carla callback opcodes
# https://github.com/falkTX/Carla/blob/2a6a7de04f75daf242ae9d8c99b349ea7dc6ff7f/source/backend/CarlaBackend.h
ENGINE_CALLBACK_PLUGIN_ADDED = 1
ENGINE_CALLBACK_PLUGIN_REMOVED = 2
ENGINE_CALLBACK_PARAMETER_VALUE_CHANGED = 5


# based on https://github.com/wvengen/lpx-controller/blob/561b5db81d0a9136d529e4262016345a255d95e8/sequencer.py that was
# based on https://github.com/dsacre/mididings/blob/master/mididings/extra/osc.py
class OSCInterface:
    plugins = {}

    def __new__(cls, stylus, pad, touch, carla_port=22752, listen_port=22755):
        obj = object.__new__(cls)
        for key, value in stylus.items():
            setattr(obj, f'on_stylus_{key}', MagicHandler(obj, 'stylus', key, value))
        for key, value in pad.items():
            setattr(obj, f'on_pad_{key}', MagicHandler(obj, 'pad', key, value))
        for key, value in touch.items():
            setattr(obj, f'on_touch_{key}', MagicHandler(obj, 'touch', key, value))
        return obj

    def __init__(self, stylus, pad, touch, carla_port=22752, listen_port=22755):  # TODO find free listen port
        self.carla_addr_tcp = liblo.Address('127.0.0.1', carla_port, proto=liblo.TCP)
        self.carla_addr_udp = liblo.Address('127.0.0.1', carla_port, proto=liblo.UDP)
        self.listen_port = listen_port
        self.server_tcp = liblo.Server(self.listen_port, proto=liblo.TCP)
        self.server_tcp.register_methods(self)
        self.server_udp = liblo.Server(self.listen_port, proto=liblo.UDP)
        self.server_udp.register_methods(self)
        self.stopped = False
        atexit.register(self.on_exit)

    async def start_udp(self):
        liblo.send(self.carla_addr_udp, '/register', 'osc.udp://127.0.0.1:%d/Carla' % self.listen_port)
        while not self.stopped:
            self.server_udp.recv(0)
            await trio.sleep(0)

    async def start_tcp(self):
        liblo.send(self.carla_addr_tcp, '/register', 'osc.tcp://127.0.0.1:%d/Carla' % self.listen_port)
        while not self.stopped:
            self.server_tcp.recv(0)
            await trio.sleep(0)

    # TODO on_start query all current parameter values to set all buttons to the correct value

    def on_exit(self):
        self.stopped = True
        liblo.send(self.carla_addr_udp, '/unregister', '127.0.0.1')
        del self.server_udp
        liblo.send(self.carla_addr_tcp, '/unregister', '127.0.0.1')
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
