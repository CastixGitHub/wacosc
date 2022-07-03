# a different approach was before authored by Rick Copeland for Ming
# https://github.com/TurboGears/Ming/blob/master/ming/odm/icollection.py
# this is much different because doesn't use a tracker, this just reacts
from typing import Iterable
import logging


log = logging.getLogger(__name__)


class ReactiveList(list):
    def __init__(self, handler, key, initial_list, init_skips_handler=True):
        self._list = initial_list
        self.handler = handler
        self.magic_key = f'{key}'
        self.inhibit = init_skips_handler
        self.enable()

    def enable(self):
        object.__setattr__(self, 'inhibit', False)
        for sub in self._list:
            if isinstance(sub, (ReactiveDict, ReactiveList)):
                sub.enable()

    def do(self):
        if not self.inhibit:
            mh = getattr(self.handler, self.magic_key)
            mh(self._list)

    def __repr__(self):
        return f'<ReactiveList: {self._list}>'

    def __getitem__(self, key):
        return self._list[key]

    def inherit(self, value):
        if isinstance(value, list):
            return ReactiveList(
                self.handler,
                self.magic_key,
                value,
                init_skips_handler=True
            )
        if isinstance(value, dict):
            return ReactiveDict(
                self.handler,
                self.magic_key[3:],
                value,
                init_skips_handler=True,
            )
        return value

    def __setitem__(self, key, value):
        if isinstance(key, slice):
            if isinstance(value, list):
                self._list[key.start:key.stop:key.step] = [self.inherit(sv) for sv in value]
            elif isinstance(value, Iterable):
                self._list[key.start:key.stop:key.step] = [self.inherit(sv) for sv in value]
        else:
            self._list[key] = self.inherit(value)
        self.do()

    def __delitem__(self, key):
        if isinstance(key, slice):
            del self[key.start:key.stop:key.step]
        else:
            del self[key]
        self.do()

    def __add__(self, other):
        self._list += other
        self.do()
        return self

    def __radd__(self, other):
        self._list = other + self._list
        self.do()
        return self

    def __iadd__(self, other):
        self._list.append(self.inherit(other))
        self.do()
        return self

    def __mul__(self, other):
        self._list *= other
        self.do()
        return self

    def __rmul__(self, other):
        self._list = other * self._list
        self.do()
        return self

    def __imul__(self, other):
        self._list *= other
        self.do()
        return self

    def __contains__(self, key):
        return key in self._list

    def append(self, value):
        self._list.append(self.inherit(value))
        self.do()
        return self

    def extend(self, iterable):
        self._list.extend((self.inherit(v) for v in iterable))
        self.do()
        return self

    def insert(self, index, value):
        self._list.insert(index, self.inherit(value))
        self.do()
        return self

    def pop(self, index=-1):
        self._list.pop(index)
        self.do()
        return self

    def remove(self, value):
        self._list.remove(value)
        self.do()
        return self

    def replace(self, iterable):
        self._list[:] = iterable
        self.do()
        return self


class ReactiveDict:
    def __init__(self, handler, prefix, initial_data, init_skips_handler=True, previous_key=''):
        object.__setattr__(self, 'inhibit', init_skips_handler)
        self.handler = handler
        if not getattr(handler, f'on_{prefix}_prefix', False):
            setattr(self.handler, f'on_{prefix}_prefix', lambda _: None)
        self.prefix = prefix
        self.previous_key = previous_key
        for k, v in initial_data.items():
            self[k] = v
        self.enable()

    def enable(self):
        object.__setattr__(self, 'inhibit', False)
        for sub in self.values():
            if isinstance(sub, (ReactiveDict, ReactiveList)):
                sub.enable()

    def __setitem__(self, key, value):
        if isinstance(value, dict):
            self.__dict__[key] = ReactiveDict(
                self.handler,
                self.prefix,
                value,
                init_skips_handler=True,
                previous_key=key
            )
        elif isinstance(value, list):
            if isinstance(value, ReactiveList):
                self.__dict__[key]._list = value._list
            else:
                self.__dict__[key] = ReactiveList(
                    self.handler,
                    f'on_{self.prefix}{self.previous_key}_{key}',
                    value,
                    init_skips_handler=True,
                )
        else:
            self.__dict__[key] = value
            if key not in ('__dict__', 'handler', 'prefix', 'previous_key', 'inhibit'):
                magic_key = f'on_{self.prefix}{self.previous_key}_{key}'
                try:
                    mh = getattr(self.handler, magic_key)
                except AttributeError:
                    log.warning(f'{magic_key} not configured')
                    mh = lambda v: None
                if not self.inhibit:
                    mh(value)

    def __contains__(self, key):
        return key in self.__dict__.keys()

    def __getitem__(self, key):
        return self.__dict__.get(key, None)

    def __getattr__(self, key):
        return getattr(self.__dict__, key)

    def __setattr__(self, key, value):
        self[key] = value

    def items(self):
        return [(k, v) for k, v in self.__dict__.items() if k not in ('inhibit', 'handler', 'prefix', 'previous_key', '__dict__')]

    def keys(self):
        return [k for k in self.__dict__.keys() if k not in ('inhibit', 'handler', 'prefix', 'previous_key')]

    def values(self, strip=None):
        if strip is None:
            strip = ('inhibit', 'handler', 'prefix', 'previous_key')
        return [v for k, v in self.__dict__.items() if k not in strip]

    def __str__(self):
        return f'<ReactiveDict: {dict(self.items())}>'

    def __repr__(self):
        return str(self)

