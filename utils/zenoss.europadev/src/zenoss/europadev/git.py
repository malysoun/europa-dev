import os
import sys
import inspect
import argparse
import repository
from .termutils import execute


class command(object):
    help = None
    repositories = repository.Configurations.get()

    def git(self, command_name, *args):
        git = os.environ.get("GIT") or "git"
        command = [git, command_name]
        command.extend(args)
        return execute(command)

    def configure( self, parser):
        name = self.__class__.__name__
        cmd_parser = parser.add_parser(name, help=self.help)
        self.add_help(cmd_parser)

    def add_help( self, parser):
        pass

    def perform( self, args):
        pass


class purge(command):
    help = "remove everything"


class reset(command):
    help = "reset a repository to master/head"


class fetch(command):
    help = "fetch upstream changes from repo(s)"


class merge(command):
    help = "merge changeset in repo"


class pull(command):
    help = "pull changesets from repo(s)"


class commit(command):
    help = "commit changes to repo(s)"


class checkout(command):
    help = "checkout repo(s)"


class clone(command):
    help = "clone repo(s)"

    def perform( self, args):
        for config in self.repositories:
            self.git("remote", "-v")
            self.git("clone", config.remote, config.local)


def is_command_class( x): return inspect.isclass(x) and issubclass(x, command)


__module__ = sys.modules[__name__]
__classes__ = inspect.getmembers(__module__, is_command_class)
__commands__ = dict([(n, cls()) for (n, cls) in __classes__])


def options():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest='command', help="Sub-command help")
    for command in __commands__.values():
        command.configure(subparser)
    return parser.parse_args()


def main():
    args = options()
    command = __commands__[args.command]
    command.perform(args)
