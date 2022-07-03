from wacosc.reactive import ReactiveDict, ReactiveList
from pytest import raises
from functools import partial
import logging


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Handler:  # pylint: disable=too-few-public-methods
    def __getattr__(self, name):
        return partial(lambda name, value: log.info('%s called with %s', name, value), name)


def test_plain(caplog):
    h = Handler()
    rd = ReactiveDict(h, 'p', {'a': ''})
    assert len(caplog.records) == 0
    rd.a = 'A'
    assert 'on_p_a called with A' in caplog.records[0].message

    rd['a'] = 'AA'
    assert rd['a'] == 'AA'
    assert 'on_p_a called with AA' in caplog.records[1].message

    rd.b = 'B'
    assert 'on_p_b called with B' in caplog.records[2].message


def test_not_handled(caplog):
    class O: pass
    o = O()
    rd = ReactiveDict(o, 'p', {'a': ''})
    assert o.on_p_prefix is not None
    assert 'on_p_a not configured' in caplog.records[0].message


def test_getattr():
    rd = ReactiveDict(Handler(), 'p', {'a': ''})
    with raises(AttributeError) as ex:
        rd.b


def test_contains():
    rd = ReactiveDict(Handler(), 'p', {'a': ''})
    assert 'a' in rd
    assert 'b' not in rd


def test_dict_views_like():
    h = Handler()
    rd = ReactiveDict(h, 'p', {'a': 'A', 'b': 'B'})

    assert ['a', 'b'] == list(rd.keys())
    assert ['A', 'B'] == list(rd.values())
    assert [('a', 'A'), ('b', 'B')] == list(rd.items())
    assert [False, h, 'p', '', 'A', 'B'] == list(rd.values(strip=()))


def test_deep(caplog):
    h = Handler()
    rd = ReactiveDict(h, 'p', {'a': 'A', 'b': 'B'})
    rd.c = {'c': 'C'}
    rd.c.c = 'CC'
    assert "on_pc_c called with CC" in caplog.records[0].message
    rd.c['d'] = 'D'
    assert "on_pc_d called with D" in caplog.records[1].message


def test_list(caplog):
    h = Handler()
    rd = ReactiveDict(h, 'p', {'a': []})
    assert isinstance(rd.a, ReactiveList)
    rd.a.append(1)
    assert "on_p_a called with [1]" in caplog.records[0].message
    rd.a[1:5] = (1, 2, 3, 4, 5)
    assert "on_p_a called with [1, 1, 2, 3, 4, 5]" in caplog.records[-1].message
    rd.a[0] = 9
    assert "on_p_a called with [9, 1, 2, 3, 4, 5]" in caplog.records[-1].message
    rd.a * 2  # mul
    assert "on_p_a called with [9, 1, 2, 3, 4, 5, 9, 1, 2, 3, 4, 5]" in caplog.records[-1].message
    rd.a.replace([1, 1, 2, 3, 4, 5])
    assert "on_p_a called with [1, 1, 2, 3, 4, 5]" in caplog.records[-1].message
    rd.a *= 2  # imul
    assert "on_p_a called with [1, 1, 2, 3, 4, 5, 1, 1, 2, 3, 4, 5]" in caplog.records[-1].message
    rd.a + [2]
    assert "on_p_a called with [1, 1, 2, 3, 4, 5, 1, 1, 2, 3, 4, 5, 2]" in caplog.records[-1].message
    rd.a.replace([])
    assert "on_p_a called with []" in caplog.records[-1].message
    rd.a.extend([1, 2])
    assert "on_p_a called with [1, 2]" in caplog.records[-1].message
    rd.a.insert(2, 5)
    assert "on_p_a called with [1, 2, 5]" in caplog.records[-1].message
    assert 5 in rd.a
    rd.a.pop()
    assert "on_p_a called with [1, 2]" in caplog.records[-1].message
    rd.a.remove(2)
    assert "on_p_a called with [1]" in caplog.records[-1].message
    rd.a.append([1, 2])
    assert "on_p_a called with [1, <ReactiveList: [1, 2]>]" in caplog.records[-1].message
    assert isinstance(rd.a[-1], ReactiveList)
    rd.a.append({'a': 'A'})
    assert "on_p_a called with [1, <ReactiveList: [1, 2]>, <ReactiveDict: {'a': 'A'}>]" in caplog.records[-1].message
    assert isinstance(rd.a[-1], ReactiveDict)
    rd.a[-1].b = 'B'
    assert "on_p_a_b called with B" in caplog.records[-1].message

    rd.a.enable()  # just to cover line 23 (at the time of writing)

    del rd.a[:]
    assert "on_p_a called with []" in caplog.records[-1].message
    rd.a.append(1)
    del rd.a[0]
    assert "on_p_a called with []" in caplog.records[-1].message

    rd.a = [5] + rd.a
    assert "on_p_a called with [5]" in caplog.records[-1].message
    rd.a += [4]
    assert "on_p_a called with [5, 4]" in caplog.records[-1].message
    rd.a = 3 * rd.a
    assert "on_p_a called with [5, 4, 5, 4, 5, 4]" in caplog.records[-1].message
