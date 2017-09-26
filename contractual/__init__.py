from contextlib import contextmanager
from functools import wraps
try:
    import yaml
except ImportError:
    # Handle this at use
    pass


class ContractException(Exception):
    pass


class ContractMock(object):
    def __init__(self, config):
        self.calls = config
        self.preconditions = None

    def __getitem__(self, item):
        # arguments may not be hashable, so we check the call table
        # for matches the manual way
        args, kwargs = item
        for call in self.calls:
            if args == call.get('args', ()) \
                    and kwargs == call.get('kwargs', {}) \
                    and self.preconditions == call.get('preconditions'):
                return call.get('return')
        raise ContractException('args: %s kwargs: %s precon: %s is not valid for this '
                                'mock' % (args, kwargs, self.preconditions))

    @contextmanager
    def pre(self, *args):
        self.preconditions = args
        try:
            yield
        finally:
            self.preconditions = None

    def __call__(self, *args, **kwargs):
        return self[(args, kwargs)]


class Contractual(object):
    def __init__(self, config):
        self.config = {}
        for key in config.keys():
            self.config[key] = self.buildconfig(config[key])

    @classmethod
    def from_yaml(cls, filename):
        try:
            with open(filename, 'r') as f:
                return cls(yaml.load(f))
        except NameError:
            raise ImportError('PyYAML is required to use YAML')

    @staticmethod
    def buildconfig(contract):
        config = []
        for c in contract:
            args = c.get('args', ())
            if type(args) == str:
                args = (args,)
            if type(args) == list:
                args = tuple(args)
            kwargs = c.get('kwargs', {})
            if type(kwargs) != dict:
                raise ContractException('Kwargs must be a dict')
            precon = c.get('preconditions', None)
            if type(precon) in (str, int, float):
                precon = (args,)
            if type(precon) == list:
                precon = tuple(precon)

            ret = c.get('return', None)
            config.append({
                'args': args,
                'kwargs': kwargs,
                'preconditions': precon,
                'return': ret,
            })
        return config

    def contract_mock(self, key):
        try:
            return ContractMock(self.config[key])
        except KeyError:
            raise ContractException('%s is not a registered contract mock' % key)

    def contract(self, key):
        def decorator(func):
            @wraps(func)
            def wrapper():
                for config in self.config[key]:
                    args = config.get('args', [])
                    kwargs = config.get('kwargs', {})
                    precon = config.get('preconditions', [])
                    ret = config.get('return')
                    try:
                        val = func(args, kwargs, precon)
                        assert val == ret
                    except AssertionError:
                        raise ContractException('function with args: %s, '
                                                'kwargs: %s and preconditions: %s '
                                                'does not return %s' % (args, kwargs, precon, ret))
            return wrapper
        return decorator
