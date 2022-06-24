# a different approach was before authored by Rick Copeland for Ming
# https://github.com/TurboGears/Ming/blob/master/ming/odm/icollection.py
# this is much different because doesn't use a tracker, this just reacts
import logging


log = logging.getLogger(__name__)


class ReactiveDict:
    def __init__(self, handler, prefix, initial_data, init_skips_handler=False, previous_key=''):
        object.__setattr__(self, 'inhibit', True)
        self.handler = handler
        if not getattr(handler, f'on_{prefix}_prefix', False):
            setattr(self.handler, f'on_{prefix}_prefix', lambda _: None)
        self.prefix = prefix
        self.previous_key = previous_key
        for k, v in initial_data.items():
            if not init_skips_handler:
                self[k] = v
            else:
                object.__setattr__(self, k, v)
        object.__setattr__(self, 'inhibit', False)

    def __setitem__(self, key, value):
        if not isinstance(value, dict):
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
        else:
            self.__dict__[key] = ReactiveDict(
                self.handler,
                self.prefix,
                value,
                init_skips_handler=True,
                previous_key=key
            )

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
            strip = (self['handler'], self['prefix'], self['previous_key'])
        return [v for v in self.__dict__.values() if v not in strip]

    def __str__(self):
        return f'ReactiveDict: {dict(self.items())}'
