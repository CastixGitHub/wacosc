from typing import Iterable
from wacosc.magic import MagicHandler
from wacosc.reactivedict import ReactiveDict
import liblo
import atexit


# based on https://github.com/wvengen/lpx-controller/blob/561b5db81d0a9136d529e4262016345a255d95e8/sequencer.py that was
# based on https://github.com/dsacre/mididings/blob/master/mididings/extra/osc.py
# TODO find free listen port
class OSCInterface:
    plugins = {}
    addresses = {}

    def __new__(cls, *args: Iterable[dict], **_):
        """here the object is created, and callables are created for each event"""
        obj = object.__new__(cls)
        for arg in args:
            for key, value in arg.items():
                setattr(
                    obj,
                    f"on_{arg['prefix']}{arg.get('previous_key', '')}_{key}",
                    MagicHandler(obj, arg['prefix'], key, value)
                )
        return obj

    def __init__(
        self,  # pylint: disable=unused-argument  # this should be in the following line
        *args: Iterable[dict],
        listen_port: int = 22755,
        **kwargs,
    ):
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

    def on_exit(self):
        self.server_udp.stop()
        del self.server_udp
        self.server_tcp.stop()
        del self.server_tcp

    def plugin_by_name(self, name):
        for _id, _dict in self.plugins.items():
            if _dict['name'] == name:
                _dict = _dict.copy()
                _dict['_id'] = _id
                return _dict
