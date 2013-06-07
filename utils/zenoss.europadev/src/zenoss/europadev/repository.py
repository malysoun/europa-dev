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
        return "Configuration({0},{1},{2})".format( *t)

    def __eq__(self, that):
        return self.tuple() == that.tuple()

    def __lt__(self, that):
        return self.tuple() < that.tuple()

    def tuple(self):
        return (self.base, self.local, self.remote)

    def exists(self):
        """ Does the local path exists """
        return os.path.exists( self.localpath())

    def localpath( self):
        return os.path.join( self.base, self.local)

@total_ordering
class Configurations(object):
    def __init__(self, values=None):
        if values:
            self.values = values
        else:
            self.values = []
        self.values = set( values)

    def __eq__(self, that):
        return self.values == that.values

    def __lt__(self, that):
        return self.values < that.values

    def __repr__(self):
        return "Configurations( {0})".format( self.values)

    def __iter__(self):
        return iter(self.values)

    def exist(self):
        """ find all configurations that exist locally """
        exists = filter( Configuration.exists, self.values)
        return Configurations(exists)

    def not_exist(self):
        """ find all configurations that exist locally """
        not_exists = filter( compose( not_, Configuration.exists), self.values)
        return Configurations( not_exists)

    @staticmethod
    def get():
        base_path = os.path.join( __file__, '..', '..', '..', '..', '..', '..')
        base_path = os.path.realpath( base_path)
        conf_path = os.path.join( base_path, 'repos')

        configs = []
        with open( conf_path, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                c = re.split( "\s*,\s*", line) 
                c = Configuration(base_path, *c)
                configs.append( c)
        return Configurations( configs)
