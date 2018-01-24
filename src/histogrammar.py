import numpy as np

from math import floor

class SparseMap(object):
    def __init__(self, default_probability=0.01, resolution=0.2):
        self.def_prob = default_probability
        self.resolution = resolution
        self.data = {}
        self.rows = {}
        self.cols = {}

    def __collapse_key(self, x, y):
        new_x = int(floor(x / self.resolution))
        new_y = int(floor(y / self.resolution))
        return (new_x, new_y,)

    def __expand_key(self, tuple):
        x = tuple[0] * self.resolution
        y = tuple[1] * self.resolution
        return (x, y,)

    def __getitem__(self, tuple_or_x, y=None):
        if y is None:
            x = tuple_or_x[0]
            y = tuple_or_x[1]
        else:
            x = tuple_or_x

        if self.__collapse_key(x, y) not in self.data:
            return self.def_prob
        return self.data[self.__collapse_key(x, y)]

    def __setitem__(self, tuple_or_x, value, y=None):
        if y is None:
            x = tuple_or_x[0]
            y = tuple_or_x[1]
        else:
            x = tuple_or_x

        self.data[self.__collapse_key(x, y)] = value

    def __delitem__(self, tuple_or_x, y=None):
        if y is None:
            x = tuple_or_x[0]
            y = tuple_or_x[1]
        else:
            x = tuple_or_x

        del self.data[self.__collapse_key(x, y)]

    def __len__(self):
        return len(self.data)


    def keys(self, axis=None, selector=None):
        if axis == 0 or axis == 'row':
            if selector is not None:
                return [self.__expand_key(k) for k in self.rows[selector]]
        if axis == 1 or axis == 'col':
            if selector is not None:
                return [self.__expand_key(k) for k in self.cols[selector]]
        return [self.__expand_key(k) for k in self.data.keys()]

    def values(self, axis=None, selector=None):
        if axis == 0 or axis == 'row':
            if selector is not None:
                return [self.data[k] for k in self.rows[selector]]
        if axis == 1 or axis == 'col':
            if selector is not None:
                return [self.data[k] for k in self.cols[selector]]
        return self.data.values()

    def items(self, axis=None, selector=None):
        return list(self.iteritems(axis, selector))

    def iteritems(self, axis=None, selector=None):
        if axis == 0 or axis == 'row':
            if selector is not None:
                for key in self.rows[selector]:
                    yield (self.__expand_key(key), self.data[key],)
        if axis == 1 or axis == 'col':
            if selector is not None:
                for key in self.cols[selector]:
                    yield (self.__expand_key(key), self.data[key],)
        
        for pair in self.data.iteritems():
            yield (self.__expand_key(pair[0]), pair[1])


class HistogramFilter(object):
    pass