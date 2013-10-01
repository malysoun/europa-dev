import os
import re
from functools import reduce, total_ordering
from operator import not_


def compose(*functions):
    return reduce(lambda f, g: lambda x: f(g(x)), functions)


@total_ordering
class Configuration(object):
    def __init__(self, root, local, remote):
        self.__root = root
        self.__local = local
        self.__remote = remote

    def __repr__(self):
        t = self.tuple()
        return "Configuration({0},{1},{2})".format(*t)

    def __eq__(self, that):
        return self.tuple() == that.tuple()

    def __lt__(self, that):
        return self.tuple() < that.tuple()

    def tuple(self):
        return self.__root, self.__local, self.__remote

    def exists(self):
        """ Does the local path exists """
        return os.path.exists(self.localpath())

    def root( self):
        """ EUROPA_ROOT """
        return self.__root

    def rootpath( self):
        """ Path relative to EUROPA_ROOT """
        return self.__local

    def localpath( self):
        """ complete local path """
        return os.path.join(self.__root, self.__local)

    def remotepath( self):
        return self.__remote


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

    def reduce(self, func, init):
        return reduce(func, self.values, init)

    @staticmethod
    def root():
        path = os.environ.get("EUROPA_ROOT", None)
        path = path or os.path.join(__file__, '..', '..', '..', '..', '..', '..')
        path = os.path.realpath(path)
        return path

    @staticmethod
    def parse(root, file):
        configs = []
        with open(file, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                path, repo = re.split("\s*,\s*", line)
                path = os.path.join(*path.split('/'))
                c = Configuration(root, path, repo)
                configs.append(c)
        return configs

    @staticmethod
    def get():
        root = Configurations.root()
        conf_file = os.path.join(root, 'repos')

        # load public repos configuration
        configs = Configurations.parse(root, conf_file)

        # load private repos configuration
        private_conf_file = os.path.join(root, 'private', 'repos')
        if os.path.exists(private_conf_file):
            private_configs = Configurations.parse(root, private_conf_file)
            configs.extend(private_configs)

        return Configurations(configs)
