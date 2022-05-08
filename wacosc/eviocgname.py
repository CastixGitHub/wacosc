# before Wayframer discovered ioctl_opt package
# I did write the following C code ot the the number
# #include <linux/input.h>
# #include <stdio.h>
# int main() {
#   printf("EVIOGCNAME(1024): %u\n", EVIOCGNAME(1024));
#   return 0;
# }
import ctypes
import fcntl
from os import listdir


try:
    from ioctl_opt import IOC, IOC_READ
    EVIOCGNAME = lambda length: IOC(IOC_READ, ord('E'), 0x06, length)
except ImportError:
    # we mock out EVIOCGNAME macro, assuming the length is always 1024
    EVIOCGNAME = lambda ignored: 2214610182  # 1024


def get_device_name(fd, length=1024):
    name = (ctypes.c_char * length)()
    actual_length = fcntl.ioctl(fd, EVIOCGNAME(length), name, True)
    if actual_length < 0:
        raise OSError(-actual_length)
    if name[actual_length - 1] == b'\x00':
        actual_length -= 1
    return name[:actual_length]


def find_event_files(grep=b'Wacom'):    
    _dict = {}
    for device in listdir('/dev/input'):
        try:
            with open('/dev/input/' + device, 'rb') as dev:
                name = get_device_name(dev)
            if grep in name:
                _dict['/dev/input/' + device] = name.decode()
        except (OSError, IsADirectoryError):
                continue
    return _dict


if __name__ == '__main__':
    import json
    print(json.dumps(find_event_files(), indent=4))
