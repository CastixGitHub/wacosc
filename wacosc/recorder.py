from typing import Iterable
from wacosc.osc import OSCInterface
from wacosc.reactive import ReactiveDict
import logging
import liblo


log = logging.getLogger(__name__)


class RecorderInterface(OSCInterface):

    def __init__(
        self,
        *args: Iterable[dict],
        this_host: str = '127.0.0.1',
        listen_port: int = 22755,
        oscdump_host: str = '127.0.0.1',
        oscdump_port: int = 9000,
    ):
        self.this_host = this_host
        self.addresses['oscdump_tcp'] = liblo.Address(oscdump_host, oscdump_port, proto=liblo.TCP)
        self.addresses['oscdump_udp'] = liblo.Address(oscdump_host, oscdump_port, proto=liblo.UDP)
        super().__init__(*args, listen_port=listen_port)

    def on_start(self):
        super().on_start()
        liblo.send(self.addresses['oscdump_tcp'], '/start', f'osc.tcp://{self.this_host}:{self.listen_port}')
        liblo.send(self.addresses['oscdump_udp'], '/start', f'osc.udp://{self.this_host}:{self.listen_port}')

    def on_exit(self):
        liblo.send(self.addresses['oscdump_udp'], '/exit', f'osc.tcp://{self.this_host}:{self.listen_port}')
        liblo.send(self.addresses['oscdump_tcp'], '/exit', f'osc.udp://{self.this_host}:{self.listen_port}')
        super().on_exit()

    def send(self, kind, parameter, value, udp=True, tcp=True):
        try:
            if udp:
                liblo.send(self.addresses['oscdump_udp'], f'/{kind}/{parameter}', value)
            if tcp:
                liblo.send(self.addresses['oscdump_tcp'], f'/{kind}/{parameter}', value)
        except:
            import pdb; pdb.set_trace()


