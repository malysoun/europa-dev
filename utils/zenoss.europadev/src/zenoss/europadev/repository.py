import os
import re
from functools import reduce, total_ordering
from operator import not_


def compose(*functions):
    return reduce(lambda f, g: lambda x: f(g(x)), functions)


@total_ordering
class Configuration(object):
    def __init__(self, base, local, remote):
        self.base = base
        self.local = local
        self.remote = remote

    def __repr__(self):
        t = self.tuple()
        return "Configuration({0},{1},{2})".format(*t)

    def __eq__(self, that):
        return self.tuple() == that.tuple()

    def __lt__(self, that):
        return self.tuple() < that.tuple()

    def tuple(self):
        return self.base, self.local, self.remote

    def exists(self):
        """ Does the local path exists """
        return os.path.exists(self.localpath())

    def rootpath( self):
        """ Path relative to EUROPA_ROOT """
        return self.local

    def localpath( self):
        return os.path.join(self.base, self.local)

    def remotepath( self):
        return self.remote


@total_ordering
class Configurations(object):
    def __init__(self, values=None):
        if values:
            self.values = values
        else:
            self.values = []
        self.values = set(values)

    def __eq__(self, that):
        return self.values == that.values

    def __lt__(self, that):
        return self.values < that.values

    def __repr__(self):
        return "Configurations( {0})".format(self.values)

    def __iter__(self):
        return iter(self.values)

    def exist(self):
        """ find all configurations that exist locally """
        return self.filter(Configuration.exists)

    def not_exist(self):
        """ find all configurations that don't exist locally """
        return self.filter(not_, Configuration.exists)

    def filter(self, *funcs):
        results = filter(compose(*funcs), self.values)
        return Configurations(results)

    @staticmethod
    def get():
        base_path = os.path.join(__file__, '..', '..', '..', '..', '..', '..')
        base_path = os.path.realpath(base_path)
        conf_path = os.path.join(base_path, 'repos')

        configs = []
        with open(conf_path, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                c = re.split("\s*,\s*", line)
                c = Configuration(base_path, *c)
                configs.append(c)
        return Configurations(configs)
