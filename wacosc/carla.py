import liblo as _liblo
import atexit


# Carla callback opcodes - https://github.com/falkTX/Carla/blob/2a6a7de04f75daf242ae9d8c99b349ea7dc6ff7f/source/backend/CarlaBackend.h
ENGINE_CALLBACK_PLUGIN_ADDED = 1
ENGINE_CALLBACK_PLUGIN_REMOVED = 2
ENGINE_CALLBACK_PARAMETER_VALUE_CHANGED = 5

# based on https://github.com/wvengen/lpx-controller/blob/561b5db81d0a9136d529e4262016345a255d95e8/sequencer.py that was
# based on https://github.com/dsacre/mididings/blob/master/mididings/extra/osc.py
class OSCInterface(object):
    plugins = {}
    
    def __init__(self, carla_port=22752, listen_port=22755): # TODO find free listen port
        self.carla_addr_tcp = _liblo.Address('127.0.0.1', carla_port, proto=_liblo.TCP)
        self.carla_addr_udp = _liblo.Address('127.0.0.1', carla_port, proto=_liblo.UDP)
        self.listen_port = listen_port
        self.on_start()
        atexit.register(self.on_exit)

    def on_start(self):
        print('starting osc')
        self.server_tcp = _liblo.ServerThread(self.listen_port, proto=_liblo.TCP)
        self.server_tcp.register_methods(self)
        self.server_tcp.start()
        self.server_udp = _liblo.ServerThread(self.listen_port, proto=_liblo.UDP)
        self.server_udp.register_methods(self)
        self.server_udp.start()
        _liblo.send(self.carla_addr_tcp, '/register', 'osc.tcp://127.0.0.1:%d/Carla' % self.listen_port)
        _liblo.send(self.carla_addr_udp, '/register', 'osc.udp://127.0.0.1:%d/Carla' % self.listen_port)
        # TODO query all current parameter values to set all buttons to the correct value


    def on_exit(self):
        # Registering with the full URL gives an error about the wrong owner, just the IP-address seems to work.
        #_liblo.send(self.carla_addr_tcp, '/unregister', 'osc.tcp://127.0.0.1:%d/Carla' % self.listen_port)
        #_liblo.send(self.carla_addr_udp, '/unregister', 'osc.udp://127.0.0.1:%d/Carla' % self.listen_port)
        _liblo.send(self.carla_addr_udp, '/unregister', '127.0.0.1')
        self.server_udp.stop()
        del self.server_udp
        _liblo.send(self.carla_addr_tcp, '/unregister', '127.0.0.1')
        self.server_tcp.stop()
        del self.server_tcp

    @_liblo.make_method('/Carla/info', 'iiiihiisssssss')
    def on_carla_info(self, path, args):
        print('INFO', path, args)

    @_liblo.make_method('/Carla/cb', 'iiiiifs')
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

    def note_on(self, plugin_id, note=60, velocity=127):
        _liblo.send(
            self.carla_addr_tcp,
            f'/Carla/{plugin_id}/note_on',
            plugin_id, note, velocity
        )

    def on_x(self, value):
        # print(float(value) / 31500)
        self.selected_plugin_id = 0
        self.parameter_index = 20
        
        _liblo.send(
            self.carla_addr_udp,
            f'/Carla/{self.selected_plugin_id}/set_parameter_value',
            self.parameter_index,
            float(value) / 31500
        )

    def on_y(self, value):
        # print(value)
        _liblo.send(
            self.carla_addr_udp,
            f'/Carla/{self.selected_plugin_id}/set_parameter_value',
            self.parameter_index,
            float(value) / 31500
        )
        
        

carla = OSCInterface()
