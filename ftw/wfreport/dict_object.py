from UserDict import IterableUserDict


class DictObject(IterableUserDict, object):

    def __getattr__(self, name):
        try:
            return self.data[name]
        except KeyError, exc:
            raise AttributeError(str(exc))

    def __setattr__(self, name, value):
        if name == 'data' and 'data' not in vars(self):
            # IterableUserDict.__init__ does self.data = {}
            object.__setattr__(self, name, value)
        else:
            self[name] = value

    def __delattr__(self, name):
        del self[name]
