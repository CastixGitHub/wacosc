import wacosc.eviocgname as eviocgname
from importlib import reload
import pytest
import sys


def mock_ioctl(fd, request, arg, mutate):
    _str = 'Wacom intuos mock'
    for i, c in enumerate(_str):
        arg[i] = c.encode()
    return len(_str)


def test_get_device_name(monkeypatch):
    monkeypatch.setattr(eviocgname, 'ioctl', mock_ioctl)
    assert b'Wacom intuos mock' == eviocgname.get_device_name(None)


def test_get_device_name_bad(monkeypatch):
    monkeypatch.setattr(eviocgname, 'ioctl', lambda *a: -1)
    with pytest.raises(OSError):
        eviocgname.get_device_name(None)


def test_get_device_name_bad_trim(monkeypatch):
    monkeypatch.setattr(eviocgname, 'ioctl', lambda *a: 10)
    assert b'\x00' * (10 - 1) == eviocgname.get_device_name(None)


def mock_listdir(path):
    return ['README.md']


def test_find_event_files(monkeypatch):
    monkeypatch.setattr(eviocgname, 'ioctl', mock_ioctl)
    monkeypatch.setattr(eviocgname, 'listdir', mock_listdir)
    assert eviocgname.find_event_files(base='./') == {
        './README.md': 'Wacom intuos mock',
    }


def test_find_event_files_permision_error(monkeypatch):
    monkeypatch.setattr(eviocgname, 'ioctl', mock_ioctl)
    assert eviocgname.find_event_files() == {}


def test_fixed_value(monkeypatch):
    got_by_opt = eviocgname.EVIOCGNAME(1024)
    monkeypatch.setitem(sys.modules, 'ioctl_opt', None)
    reload(eviocgname)
    assert eviocgname.EVIOCGNAME(1024) == got_by_opt
