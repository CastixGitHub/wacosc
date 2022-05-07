from wacosc.xinput import find_event_files
from wacosc.carla import carla
from select import select
from struct import unpack


class ReactiveDict:
    def __init__(self, handler, initial_data):
        self.handler = handler
        self.__dict__ = initial_data

    def __setitem__(self, key, value):
        self.__dict__[key] = value
        getattr(self.handler, f'on_key')(value)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __getattr__(self, key):
        if key != '__dict__':
            return getattr(self.__dict__, key)
        return getattr(self, '__dict__')

    def __setattr__(self, key, value):
        setattr(self.__dict__, key, value)


stylus = ReactiveDict(carla, {
    'x': 0,
    'y': 0,
    'tilt x': 0,
    'tilt y': 0,
    'erasing': 'NO',
    'near': 'NO',
    'pressing': 'OFF',
    'pressure': 0,
    'distance': 0,
    'stylus button 1': 'OFF',
    'stylus button 2': 'OFF',
    '?': '',
})

def handle_stylus(timestamp, usecond, type_, code, value):
    if type_ in (0, 4):
        return  # SYN or MISC (serial 1954545779)
    elif type_ == 1:  # BUTTONS
        if code == 320:
            stylus['near'] = 'YES'
        elif code == 321:
            stylus['erasing'] = 'YES'
        elif code == 330:
            stylus['pressing'] = 'ON' if value else 'OFF'
        # it is really hard to press button1 and button2 together
        elif code == 331:
            stylus['stylus button 1'] = 'ON' if value else 'OFF'
        elif code == 332:
            stylus['stylus button 2'] = 'ON' if value else 'OFF'
        else:
            stylus['?'] = f'BUTTONS {code} {value}'

    elif type_ == 3:
        if code == 0:
            if value == 0:
                stylus['near'] = 'NO'
            else:
                stylus['x'] = value
                osc.on_x(value)
        elif code == 1:
            stylus['y'] = value
        elif code == 26:
            stylus['tilt x'] = value
        elif code == 27:
            stylus['tilt y'] = value
        elif code == 24:
            stylus['pressure'] = value
        elif code == 25:
            stylus['distance'] = value
        elif code == 40:
            stylus['erasing'] = 'NO'
        else:
            stylus['?'] = f'ABS {code} {value}'
    else:
        stylus['?'] = f'{type_} {code} {value}'


pad = {
    '?': '',
}
def handle_pad(timestamp, usecond, type_, code, value):
    if type_ in (0, 4):
        return  # SYN or MISC (serial 1954545779)
    elif type_ == 1:  # BUTTONS
        if code == 256:
            # how can we know the led value?
            pad['main button'] = 'ON' if value else 'OFF'
        elif code in range(257, 362):
            pad[f'button {code}'] = 'ON' if value else 'OFF'
        pad['?'] = f'BUTTONS {code} {value}'

    elif type_ == 3:
        if code == 8:
            pad['touchring'] = value
        elif code == 40:
            return # pad['WTF'] = value  # 0 or 15
        else:
            pad['?'] = f'ABS {code} {value}'
    else:
        pad['?'] = f'{type_} {code} {value}'

touch = {
    '?': '',
    'x': '',
    'y': '',
    # 'touching': 'NO',
    'fingers': 0,
    '0': {}
}
last_slot = '0'
def handle_touch(timestamp, usecond, type_, code, value):
    global last_slot
    if type_ in (0, 4):
        return  # SYN or MISC (serial 1954545779)
    elif type_ == 1:  # BUTTONS
        if code == 325:
            pass  # this is just wrong...
            # touch['touching'] = 'YES' if value else 'NO'
        elif code == 330:
            if value:
                touch['fingers'] = 1
        elif code == 333:
            if value:
                touch['fingers'] = 2
        elif code == 334:
            if value:
                touch['fingers'] = 3
        elif code == 335:
            if value:
                touch['fingers'] = 4
        elif code == 328:
            if value:
                touch['fingers'] = 5
        else:
            touch['?'] = f'BUTTONS {code} {value}'

    elif type_ == 3:
        if code in (48, 49):
            pass  # skip major and minor for the moment...
        elif code == 57:
            touch['fingers'] -= 1
        elif code == 0:
            touch['x'] = value
        elif code == 1:
            touch['y'] = value
        elif code == 47:
            last_slot = str(value)
            if last_slot not in touch:
                touch[last_slot] = {}
        elif code == 53:
            touch[last_slot]['x'] = value
        elif code == 54:
            touch[last_slot]['y'] = value
        else:
            touch['?'] = f'ABS {code} {value}'
    else:
        touch['?'] = f'{type_} {code} {value}'



from threading import Thread
def handle_wacom():
    fpaths = find_event_files()
    files = {}

    for path in fpaths.keys():
        f = open(path, 'rb')
        files[f.fileno()] = f

    while True:
        if killing:
            break
        reading = select(files.keys(), [], [])[0]
        for fno in reading:
            if 'Pen' in fphats[files[fno].name]:
                handle_stylus(*unpack('LLHHi', files[fno].read(24)))
            if 'Pad' in fphats[files[fno].name]:
                handle_pad(*unpack('LLHHi', files[fno].read(24)))
            if 'Finger' in fphats[files[fno].name]:
                handle_touch(*unpack('LLHHi', files[fno].read(24)))

    for f in files.values():
        f.close()

killing = False
t = Thread(target=handle_wacom)
t.start()
