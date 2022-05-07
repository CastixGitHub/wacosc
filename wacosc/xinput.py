from subprocess import check_output, CalledProcessError
from sys import stderr
import re


def grep_xinput(name):
    try:
        return check_output(f'xinput list | grep {name}', shell=True).decode()
    except CalledProcessError as e:
        print(str(e), file=stderr)
        return ''

def clean_name(name):
    return ' '.join([c for c in name.split(' ') if c and c not in (' ', '⎡', '↳', '\u23a3', '\u239c')])

def find_event_files(grep='Wacom'):
    _dict = {}
    for name, _id in re.compile('(.*)\tid=(?P<line>\d+)').findall(grep_xinput(grep)):
        _dict[f'/dev/input/event{_id}'] = clean_name(name)
    return _dict


if __name__ == '__main__':
    import json
    print(json.dumps(find_event_files(), indent=4))
