import os
import re

class Configuration(object):
    def __init__(self, local, remote):
        self.local = local
        self.remote = remote

    def __repr__(self):
        return "configuration({0},{1})".format( self.local, self.remote)

class Configurations(object):
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
                c = Configuration( *c)
                configs.append( c)
        return configs
