from unittest.mock import MagicMock
from wacosc.magic import MagicHandler

cfg_flat = {
    'plugin_name': '',
    'parameter_name': '',
    'fn': lambda _: None,
}

cfg_nested = {
    'key': cfg_flat
}


def test_magichandler():
    mh = MagicHandler(MagicMock(), 'kind', 'key', cfg_flat)
    mh(128)


def test_magichandler_nested():
    mh = MagicHandler(MagicMock(), 'kind', 'key', cfg_nested)
    mh(128)


def test_magichandler_empty_cfg(caplog):
    mh = MagicHandler(MagicMock(), 'kind', 'key', {'plugin_name': ''})
    mh(128)
    assert False, caplog.records
