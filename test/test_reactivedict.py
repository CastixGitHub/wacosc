from wacosc.reactivedict import ReactiveDict
from pytest import raises


class Handler:
    a = None

    def on_p_a(self, value):
        self.a = value


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
    assert [h, 'p', 'A', 'B'] == list(rd.values())
    assert [('a', 'A'), ('b', 'B')] == list(rd.items())
    assert ['A', 'B'] == list(rd.values(strip=(h, 'p')))
