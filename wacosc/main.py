import signal
import trio
from wacosc.wacom import handle_wacom
from wacosc.carla import carla


async def main():
    print(__import__('os').getpid())
    async with trio.open_nursery() as nursery:
        print('starting wacom handler')
        nursery.start_soon(handle_wacom)
        print('starting osc servers to communicate with carla')
        nursery.start_soon(carla.start_udp)
        print('starting tcp too')
        nursery.start_soon(carla.start_tcp)


def handler(signum, frame):
    print(frame)
    print('Signal', signum, 'frame is above.')
    carla.on_exit()


signal.signal(signal.SIGTERM, handler)


trio.run(main)
