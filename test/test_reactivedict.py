from wacosc.reactivedict import ReactiveDict
from pytest import raises


class Handler:  # is a mock better suited?
    a = None
    b = None
    c = None
    d = None
    cc = None

    def on_p_a(self, value):
        self.a = value

    def on_p_c(self, value):
        self.c = value

    def on_pc_d(self, value):
        self.d = value

    def on_pc_cc(self, value):
        self.cc = value


def test_plain():
    h = Handler()
    rd = ReactiveDict(h, 'p', {'a': ''})
    assert rd.a == ''

    rd.a = 'A'
    assert h.a == 'A'

    rd['a'] = 'AA'
    assert h.a == 'AA'

    rd.b = 'B'
    assert rd['b'] == 'B'  # even if not handled
    assert rd.b == 'B'
    assert getattr(rd, 'b') == 'B'


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
    assert [h, 'p', '', 'A', 'B'] == list(rd.values(strip=()))


def test_deep():
    h = Handler()
    rd = ReactiveDict(h, 'p', {'a': 'A', 'b': 'B'})
    rd.c = {'c': 'C'}
    assert h.c == {'c': 'C'}

    rd.c['c'] = 'CC'
    assert h.c == {'c': 'C'}

    rd['c']['cc'] = 'CCC'
    assert h.cc == 'CCC'

    assert rd.c.cc == 'CCC'

    rd.c['d'] = 'D'
    assert rd.c.d == 'D'
    assert h.d == 'D'


def test_list():
    h = Handler()
    rd = ReactiveDict(h, 'p', {'a': []})
    rd.a.append(1)
    assert h.a == [1]
    rd.a[0:5] = (1, 2, 3, 4, 5)
    assert h.a == [1, 2, 3, 4, 5]
