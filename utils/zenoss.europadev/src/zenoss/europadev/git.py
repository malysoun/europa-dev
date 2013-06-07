import os
import sys
import inspect
import argparse
import repository
from .termutils import execute, shell, say, warn

class command(object):
    """ base git-command object """
    help = None
    repositories = repository.Configurations.get()

    def git(self, command_name, *args, **kwargs):
        git = os.environ.get("GIT") or "git"
        command = [git, command_name]
        command.extend(args)
        return execute(command, **kwargs)

    def name(self):
        return self.__class__.__name__

    def configure( self, parser):
        cmd_parser = parser.add_parser( self.name(), help=self.help)
        self.add_help( cmd_parser)

    def has_unstaged_changes(self, path):
        return self.git( "diff-files", "--quiet", cwd=path)
    
    def has_uncommitted_changes( self, path):
        """ args for testing if a local git repository has changes """
        return self.git("diff-index", "--quiet", "HEAD", "--", cwd=path)

    def has_changes( self, path):
        """ test if a local git repository has changes """
        self.git( "update-index", "-q", "--refresh", cwd=path)
        if self.has_unstaged_changes(path):
            return True 

        if self.has_uncommitted_changes(path):
            return True

        return False

    def add_help( self, parser):
        pass

    def perform( self, args):
        return 0


class purge(command):
    help = "remove local cloned repositories"
    def add_help(self, parser):
        parser.add_argument(
            "-f", "--force", dest="force", action="store_true", default=False,
            help="force local repository deletion, even when changes exist")

    def perform(self, args):
        retcode = 0
        configs = self.repositories.exist()
        for config in configs:
            path = config.localpath()
            if args.force or not self.has_changes( path):
                shell( " ".join(["rm", "-rf", path]))
            else:
                warn( "local clone has changes: {0}".format(path))

        return retcode

class reset(command):
    help = "reset repositories"

class fetch(command):
    help = "fetch upstream changes from repo(s)"

class merge(command):
    help = "merge changeset in repo"

class pull(command):
    help = "pull changesets into local repo(s)"
    def perform(self, args):
        retcode = 0
        configs = self.repositories.exist()
        for config in configs:
            result = self.git( "pull", cwd=config.localpath())
            retcode = retcode if result == 0 else result
        return retcode

class checkout(command):
    help = "checkout repo(s)"

class commit(command):
    help = "commit changes to repo(s)"

class status(command):
    help = "print status summary for repo(s)"
    def perform(self, args):
        retcode = 0
        configs = self.repositories.exist()
        for config in configs:
            path = config.localpath()
            say( "Status for {0} in {1}".format(config.remote, path))
            result = self.git( "status", cwd=path)
            retcode = retcode if result == 0 else result
        return retcode

class clone(command):
    help = "clone repo(s)"

    def perform( self, args):
        retcode = 0
        configs = self.repositories.not_exist()
        for config in configs:
            result = self.git( "clone", config.remote, config.localpath())
            retcode = retcode if result == 0 else result
        return retcode

def is_command_class( x):
    return inspect.isclass( x) and issubclass( x, command)

__module__   = sys.modules[__name__]
__classes__  = inspect.getmembers(__module__, is_command_class)
__commands__ = dict( [(n, cls()) for (n, cls) in __classes__])
del __commands__['command']

def options():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest='command', help="Sub-command help")
    for command in __commands__.values():
        command.configure(subparser)
    return parser.parse_args()


def main():
    args = options()
    command = __commands__[args.command]
    retcode = command.perform( args)
    sys.exit( retcode)
