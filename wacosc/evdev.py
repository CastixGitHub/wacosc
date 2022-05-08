import evdev


def find_event_files(grep='Wacom'):
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    _dict = {}
    for device in devices:
        if grep in device.name:
            _dict[device.path] = device.name
    return _dict


if __name__ == '__main__':
    import json
    print(json.dumps(find_event_files(), indent=4))
