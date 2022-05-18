from wacosc.eviocgname import find_event_files
from wacosc.carla import carla
from wacosc.reactivedict import ReactiveDict
from select import poll, POLLIN
from struct import unpack
import logging


log = logging.getLogger(__name__)


stylus = ReactiveDict(carla, 'stylus', {
    'x': 0,
    'y': 0,
    'tilt_x': 0,
    'tilt_y': 0,
    'erasing': 'NO',
    'near': 'NO',
    'pressing': 'OFF',
    'pressure': 0,
    'distance': 0,
    'stylus_button_1': 'OFF',
    'stylus_button_2': 'OFF',
    'unknown': '',
})


def handle_stylus(timestamp, usecond, type_, code, value):
    match type_:
        case 0:
            return
        case 4:
            return
        case 1:
            match code:
                case 320:
                    stylus['near'] = 'YES'
                case 321:
                    stylus['erasing'] = 'YES'
                case 330:
                    stylus['pressing'] = 'ON' if value else 'OFF'
                case 331:
                    stylus['stylus_button_1'] = 'ON' if value else 'OFF'
                case 332:
                    stylus['stylus_button_2'] = 'ON' if value else 'OFF'
                case _:
                    stylus['unknown'] = f'BUTTONS {code} {value}'
        case 3:
            match code:
                case 0:
                    if value == 0:
                        stylus['near'] = 'NO'
                    else:
                        stylus['x'] = value
                case 1:
                    stylus['y'] = value
                case 26:
                    stylus['tilt_x'] = value
                case 27:
                    stylus['tilt_y'] = value
                case 24:
                    stylus['pressure'] = value
                case 25:
                    stylus['distance'] = value
                case 40:
                    stylus['erasing'] = 'NO'
                case _:
                    stylus['unknown'] = f'ABS {code} {value}'


pad = ReactiveDict(carla, 'pad', {
    'unknown': '',
})
def handle_pad(timestamp, usecond, type_, code, value):
    match type_:
        case 0:
            return
        case 4:
            return
        case 1:
            match code:
                case 256:
                    # how can we know the led value?
                    pad['main_button'] = 'ON' if value else 'OFF'
                case c if 257 <= c < 362:
                    pad[f'button_{code}'] = 'ON' if value else 'OFF'
                case _:
                    pad['unknown'] = f'BUTTONS {code} {value}'
        case 3:
            match code:
                case 8:
                    pad['touchring'] = value
                case 40:
                    return  # pad['WTF'] = value  # 0 or 15
                case _:
                    pad['unknown'] = f'ABS {code} {value}'


touch = ReactiveDict(carla, 'touch', {
    'unknown': '',
    'x': 0,
    'y': 0,
    # 'touching': 'NO',
    'fingers': 0,
    '0': {}
})
last_slot = '0'
def handle_touch(timestamp, usecond, type_, code, value):
    global last_slot
    match type_:
        case 0 | 4:
            return
        case 1:
            match code:
                case 325:
                    if not value:
                        log.debug('setting fingers to 0')
                        touch['fingers'] = 0
                case 325 | 330:
                    if value:
                        log.debug(1, 'fingers', code)
                        touch['fingers'] = 1
                case 333:
                    if value:
                        log.debug(2, 'fingers')
                        touch['fingers'] = 2
                case 334:
                    if value:
                        log.debug(3, 'fingers')
                        touch['fingers'] = 3
                case 335:
                    if value:
                        touch['fingers'] = 4
                case 328:
                    if value:
                        touch['fingers'] = 5
                case _:
                    touch['unknown'] = f'BUTTONS {code} {value}'
        case 3:
            match code:
                case 0:
                    touch['x'] = value
                case 1:
                    touch['y'] = value
                case 48:
                    touch[last_slot]['major'] = value
                case 49:
                    touch[last_slot]['minor'] = value
                case 57:
                    print('decrementing fingers to', touch['fingers'] - 1)
                    if touch['fingers'] > 0:
                        touch['fingers'] -= 1

                case 47:
                    last_slot = str(value)
                    if last_slot not in touch:
                        touch[last_slot] = {}
                case 53:
                    touch[last_slot]['x'] = value
                case 54:
                    touch[last_slot]['y'] = value
                case _:
                    touch['unknown'] = f'ABS {code} {value}'


from threading import Thread
def handle_wacom():
    fpaths = find_event_files()
    files = {}
    _poll = poll()

    for path in fpaths.keys():
        f = open(path, 'rb')
        files[f.fileno()] = f
        _poll.register(f, POLLIN)

    while not killing:
        for fno, _ in _poll.poll():
            if 'Pen' in fpaths[files[fno].name]:
                handle_stylus(*unpack('LLHHi', files[fno].read(24)))
            if 'Pad' in fpaths[files[fno].name]:
                handle_pad(*unpack('LLHHi', files[fno].read(24)))
            if 'Finger' in fpaths[files[fno].name]:
                handle_touch(*unpack('LLHHi', files[fno].read(24)))

    for f in files.values():
        f.close()

killing = False
t = Thread(target=handle_wacom)
t.start()
