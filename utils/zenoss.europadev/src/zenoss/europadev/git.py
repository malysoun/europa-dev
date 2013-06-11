import os
import sys
import inspect
import argparse
import repository
import subprocess
from functools import partial
from .termutils import *


def git(command_name, *args, **kwargs):
    git = os.environ.get("GIT") or "git"
    command = [git, command_name]
    command.extend(args)
    return execute(command, **kwargs)[0]


def git_out(command_name, *args, **kwargs):
    """  run git and return process stdout """
    git = os.environ.get("GIT") or "git"
    command = [git, command_name]
    command.extend(args)
    kwargs["stdout"] = subprocess.PIPE
    return execute(command, **kwargs)


class command(object):
    """ base git-command object """
    help = None
    repositories = repository.Configurations.get()

    def name(self):
        return self.__class__.__name__

    def configure( self, parser):
        cmd_parser = parser.add_parser(self.name(), help=self.help)
        self.add_help(cmd_parser)

    def get_branch(self, path):
        return git_out("rev-parse", "--abbrev-ref", "HEAD", cwd=path)[1][0].strip()

    def get_untracked_changes(self, path):
        return git_out("ls-files", "--other", "--exclude-standard", cwd=path)[1]

    def has_untracked_changes(self, path):
        untracked_changes = self.get_untracked_changes(path)
        return 1 if len(untracked_changes) > 0 else 0

    def has_unstaged_changes(self, path):
        return git("diff-files", "--quiet", cwd=path)

    def has_uncommitted_changes( self, path):
        """ args for testing if a local git repository has changes """
        return git("diff-index", "--quiet", "HEAD", "--", cwd=path)

    def has_changes( self, path):
        """ test if a local git repository has changes """
        git("update-index", "-q", "--refresh", cwd=path)
        if self.has_unstaged_changes(path):
            return True

        if self.has_uncommitted_changes(path):
            return True

        if self.has_untracked_changes(path):
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

    def execute(self, force, value, config):
        result = 0
        path = config.localpath()
        if force or not self.has_changes(path):
            say("Removing: {0}".format(config.rootpath()))
            result = shell(" ".join(["rm", "-rf", path]))
        else:
            warn("Not removing: clone has changes: {0}".format(path))
        return value if result == 0 else 1

    def perform(self, args):
        execute = partial(self.execute, args.force)
        configs = self.repositories.exist()
        return configs.reduce(execute, 0)


class fetch(command):
    help = "fetch upstream changes from repo(s)"

    def add_help(self, parser):
        parser.add_argument(
            "--all", dest="all", action="store_true", default=False,
            help="fetch all remotes")

    def execute(self, flags, value, config):
        say("Git Fetch {0}".format(config.rootpath()))
        result = git("fetch", *flags, cwd=config.localpath())
        print
        return value if result == 0 else 1

    def perform(self, args):
        configs = self.repositories.exist()
        flags = []
        if args.all:
            flags.append("--all")
        func = partial(self.execute, flags)
        return configs.reduce(func, 0)


class pull(command):
    help = "pull changesets into local repo(s)"

    def execute(self, value, config):
        say("Git Pull {0}".format(config.rootpath()))
        result = git("pull", cwd=config.localpath())
        print
        return value if result == 0 else 1

    def perform(self, args):
        configs = self.repositories.exist()
        return configs.reduce(self.execute, 0)


class checkout(command):
    help = "checkout repo(s)"

    def add_help(self, parser):
        parser.add_argument("branch", help="branch name to checkout")

    def execute(self, branch, value, config):
        say("Git Checkout {0} in {1}".format(branch, config.rootpath()))
        result = git("checkout", branch, cwd=config.localpath())
        print
        return value if result == 0 else 1

    def perform(self, args):
        configs = self.repositories.exist()
        func = partial(self.execute, args.branch)
        return configs.reduce(func, 0)


class clone(command):
    help = "clone repo(s)"

    def execute(self, value, config):
        say("Git Clone {0} -> {1}".format(config.remotepath(), config.rootpath()))
        result = git("clone", config.remote, config.localpath())
        return value if result == 0 else 1

    def perform(self, args):
        configs = self.repositories.not_exist()
        return configs.reduce(self.execute, 0)


class status(command):
    help = "print status for repo(s)"

    def execute(self, value, config):
        path = config.localpath()
        say("Git Status {0}".format(config.rootpath()))
        result = git("status", cwd=path)
        print
        return value if result == 0 else 1

    def perform(self, args):
        configs = self.repositories.exist()
        return configs.reduce(self.execute, 0)


class diff(command):
    help = "print diff for repo(s)"

    def execute(self, value, config):
        path = config.localpath()
        say("Git Diff {0}".format(config.rootpath()))
        result = git("diff", cwd=path)
        print
        return value if result == 0 else 1

    def perform(self, args):
        configs = self.repositories.exist()
        return configs.reduce(self.execute, 0)

class xstatus(command):
    help = "print a status summary for repo(s)"
    formatter = "{:<45} {:<10} {:<11} {:<8} {:<9} {}"

    #path, repo, branch, untracked, tracked, unstaged,
    def execute(self, value, config):
        path = config.localpath()
        rpath = config.remotepath()
        branch = self.get_branch(path)
        changes = self.has_uncommitted_changes(path)
        unstaged = self.has_unstaged_changes(path)
        untracked = self.has_untracked_changes(path)

        print self.formatter.format(config.rootpath(), branch, changes, unstaged, untracked, rpath)
        return value

    def perform(self, args):
        header = ("Path", "Branch", "Uncommitted", "Unstaged", "Untracked", "Repo")
        print self.formatter.format(*header)
        configs = self.repositories.exist()
        return configs.reduce(self.execute, 0)


def is_command_class( x):
    return inspect.isclass(x) and issubclass(x, command)


__module__ = sys.modules[__name__]
__classes__ = inspect.getmembers(__module__, is_command_class)
__commands__ = dict([(n, cls()) for (n, cls) in __classes__])
del __commands__['command']


def options():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", dest="debug", default=False, action="store_true",
                        help="enable detailed debug logging")
    subparser = parser.add_subparsers(dest='command', help="Sub-command help")
    for command in sorted(__commands__.values()):
        command.configure(subparser)
    args = parser.parse_args()
    debug.enable = args.debug
    debug.wrap = False
    say.wrap = False
    warn.wrap = False
    return args


def main():
    args = options()
    command = __commands__[args.command]
    retcode = command.perform(args)
    sys.exit(retcode)
