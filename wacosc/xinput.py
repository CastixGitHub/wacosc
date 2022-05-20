# TODO: support wayland through libinput
from subprocess import check_output, CalledProcessError
from sys import stderr, argv
import argparse
import re


def grep_xinput(name):
    try:
        return check_output(f'xinput list | grep {name}', shell=True).decode()
    except CalledProcessError as e:
        print(str(e), file=stderr)
        return ''


def clean_name(name):
    return ' '.join([c for c in name.split(' ') if c and c not in (' ', '⎡', '↳', '\u23a3', '\u239c')])


def find_ids(grep='Wacom'):
    _dict = {}
    for name, _id in re.compile(r'(.*)\tid=(?P<line>\d+)').findall(grep_xinput(grep)):
        _dict[_id] = clean_name(name)
    return _dict


def action(_action, _ids):
    for key in _ids.keys():
        check_output(['xinput', _action, key], shell=False)


if __name__ == '__main__':  # pragma: no cover
    import json
    parser = argparse.ArgumentParser()
    parser.add_argument('--grep', '-g', default='Wacom', help='string that must be in the device name')
    parser.add_argument('--action', '-a', default='show', help='show, enable or disable')
    args = parser.parse_args(argv[1:])
    ids = find_ids(grep=args.grep)

    if args.action != 'show':
        action(args.action, ids)

    print(json.dumps(ids, indent=4))
