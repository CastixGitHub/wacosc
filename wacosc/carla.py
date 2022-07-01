"""WacOsc carla.py - where handlers are defined."""
from typing import Iterable
from wacosc.osc import OSCInterface
from wacosc.plugins import ranges
import logging
import liblo


log = logging.getLogger(__name__)

# Carla callback opcodes
# https://github.com/falkTX/Carla/blob/2a6a7de04f75daf242ae9d8c99b349ea7dc6ff7f/source/backend/CarlaBackend.h
ENGINE_CALLBACK_PLUGIN_ADDED = 1
ENGINE_CALLBACK_PLUGIN_REMOVED = 2
ENGINE_CALLBACK_PARAMETER_VALUE_CHANGED = 5


class CarlaInterface(OSCInterface):

    def __init__(
        self,
        *args: Iterable[dict],
        listen_port: int = 22755,
        carla_host: str = '127.0.0.1',
        carla_port: int = 22752,
    ):
        self.addresses['carla_tcp'] = liblo.Address(carla_host, carla_port, proto=liblo.TCP)
        self.addresses['carla_udp'] = liblo.Address(carla_host, carla_port, proto=liblo.UDP)
        super().__init__(*args, listen_port=listen_port)

    def on_start(self):
        super().on_start()
        liblo.send(self.addresses['carla_tcp'], '/register', 'osc.tcp://127.0.0.1:%d/Carla' % self.listen_port)
        liblo.send(self.addresses['carla_udp'], '/register', 'osc.udp://127.0.0.1:%d/Carla' % self.listen_port)
        # TODO query all current parameter values to set all buttons to the correct value

    def on_exit(self):
        liblo.send(self.addresses['carla_udp'], '/unregister', '127.0.0.1')
        liblo.send(self.addresses['carla_tcp'], '/unregister', '127.0.0.1')
        super().on_exit()

    @staticmethod
    @liblo.make_method('/Carla/info', 'iiiihiisssssss')
    def on_carla_info(path, args):
        log.info('Carla INFO %s %s', path, args)

    @liblo.make_method('/Carla/cb', 'iiiiifs')
    def on_carla_cb(self, path, args):
        # https://github.com/falkTX/Carla/blob/de8e0d3bd9cc4ab76cbea9f53352c92d89266ea2/source/frontend/carla_control.py#L337
        action, plugin_id, value1, value2, value3, valuef, value_str = args
        log.info('Carla CB %s %s', path, args)
        if action == ENGINE_CALLBACK_PLUGIN_ADDED:
            self.plugins[plugin_id] = {
                'name': value_str,
                'ranges': ranges[value_str],
            }
            if value_str == 'Noize Mak3r':
                self.note(plugin_id)  # immediatly make noize!
        elif action == ENGINE_CALLBACK_PLUGIN_REMOVED:
            del self.plugins[plugin_id]

        print(self.plugins)

    def note(self, plugin_id, note=60, velocity=127, active=True):
        liblo.send(
            self.addresses['carla_tcp'],
            f'/Carla/{plugin_id}/note_{"on" if active else "off"}',
            plugin_id, note, velocity
        )

    def send(self, plugin_id, parameter_id, value, udp=True):
        liblo.send(
            self.addresses['carla_udp'] if udp else self.addresses['carla_tcp'],
            f'/Carla/{plugin_id}/set_parameter_value',
            parameter_id,
            value,
        )
