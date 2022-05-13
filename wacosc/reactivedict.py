class ReactiveDict:
    def __init__(self, handler, prefix, initial_data):
        self.handler = handler
        self.prefix = prefix
        for k, v in initial_data.items():
            self[k] = v

    def __setitem__(self, key, value):
        self.__dict__[key] = value
        if key not in ('__dict__', 'handler'):
            try:
                getattr(self.handler, f'on_{self.prefix}_{key}')(value)
            except AttributeError:
                print(f'on_{self.prefix}_{key} not configured')

    def __getitem__(self, key):
        return self.__dict__.get(key, None)

    def __getattr__(self, key):
        if key != '__dict__':
            return getattr(self.__dict__, key)
        return getattr(self, '__dict__')

    def __setattr__(self, key, value):
        self[key] = value

    def items(self):
        return [(k, v) for k, v in self.__dict__.items() if k not in ('handler', '__dict__')]

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()
