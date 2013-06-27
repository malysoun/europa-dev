import json
import os
import sys
import inspect
import argparse
import subprocess
from getpass import getpass
from functools import partial

import requests

from zenoss.europadev import repository
from .termutils import *
from .repository import Configuration


def get_oauth_token():
    """
    Get or create an OAuth token for making pull requests.
    """
    cache = os.path.join(os.path.expanduser("~"), ".europa.gitauth")
    try:
        result = open(cache, 'r').read().strip()
    except IOError:
        username = raw_input("GitHub username: ")
        password = getpass("GitHub password: ")
        response = requests.post(
            "https://api.github.com/authorizations",
            data=json.dumps({
                "scopes": ["repo"],
                "note": "Europa Development Environment"
            }),
            auth=(username, password))
        result = response.json().get('token')
        with open(cache, 'w') as f:
            f.write(result)
    return result


def github_api(method, url, data=None):
    token = get_oauth_token()
    return requests.request(
        method, "https://api.github.com" + url, data=data,
        headers={"Authorization": "token %s" % token}
    ).json()


def repo_info():
    remotes = (s.strip() for s in git_out("remote", "-v")[1])
    branch = git_out("symbolic-ref", "--short", "HEAD")[1][0].strip()
    for line in remotes:
        if line.startswith('origin'):
            line = line.rsplit(":", 1)[-1]
            owner, name = line.split('/')[-2:]
            name = name.split()[0]
            if name.endswith('.git'):
                name = name[:-4]
            return owner, name, branch


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
    # use the class name
    cmd = None
    help = None
    repositories = repository.Configurations.get()

    def name(self):
        return self.cmd if self.cmd else self.__class__.__name__

    def configure(self, parser):
        cmd_parser = parser.add_parser(self.name(), help=self.help)
        self.add_help(cmd_parser)

    def get_branch(self, path):
        return git_out("rev-parse", "--abbrev-ref", "HEAD", cwd=path)[1][0].strip()

    def get_untracked_changes(self, path):
        return git_out("ls-files", "--other", "--exclude-standard", cwd=path)[1]

    def has_staged_changes(self, path):
        """ args for testing if a local git repository has changes """
        return git("diff-index", "--cached", "--quiet", "HEAD", "--", cwd=path)

    def has_unstaged_changes(self, path):
        return git("diff-files", "--quiet", "--", cwd=path)

    def has_untracked_changes(self, path):
        untracked_changes = self.get_untracked_changes(path)
        return 1 if len(untracked_changes) > 0 else 0

    def has_changes(self, path):
        """ test if a local git repository has changes """
        git("update-index", "-q", "--refresh", cwd=path)
        if self.has_unstaged_changes(path):
            return True

        if self.has_staged_changes(path):
            return True

        if self.has_untracked_changes(path):
            return True

        return False

    def add_help(self, parser):
        pass

    def perform(self, args):
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
        say("git fetch {0}".format(config.rootpath()))
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
        say("git pull {0}".format(config.rootpath()))
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
        say("git checkout {0} in {1}".format(branch, config.rootpath()))
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
        say("git clone {0} -> {1}".format(config.remotepath(), config.rootpath()))
        result = git("clone", config.remotepath(), config.localpath())
        if result == 0:
            shell("git flow init -d 2>&1 >/dev/null", cwd=config.localpath())
        return value if result == 0 else 1

    def perform(self, args):
        configs = self.repositories.not_exist()
        return configs.reduce(self.execute, 0)


class status(command):
    help = "print status for cloned repo(s) with changes"

    def add_help(self, parser):
        parser.add_argument(
            "-a", "--all", dest="all", action="store_true", default=False,
            help="show status for all repos including unchanged repos")

    def execute(self, value, config):
        path = config.localpath()
        say("git status {0} -s".format(config.rootpath()))
        result = git("status", "-s", cwd=path)
        print
        return value if result == 0 else 1

    def perform(self, args):
        configs = self.repositories.exist()
        if not args.all:
            configs = configs.filter(self.has_changes, Configuration.localpath)
        return configs.reduce(self.execute, 0)


class diff(command):
    help = "print diff for repo(s)"

    def execute(self, value, config):
        path = config.localpath()
        say("git diff {0}".format(config.rootpath()))
        result = git("diff", cwd=path)
        print
        return value if result == 0 else 1

    def perform(self, args):
        configs = self.repositories.exist()
        return configs.reduce(self.execute, 0)


class xstatus(command):
    help = "print a status summary for repo(s)"
    __formatter = "{:<45} {:<10} {:^11} {:^8} {:^9} {}"

    def add_help(self, parser):
        pass

    #path, repo, branch, untracked, tracked, unstaged,
    def execute(self, summaries, config):
        path = config.localpath()
        rpath = config.remotepath()
        branch = self.get_branch(path)
        changes = "X" if self.has_staged_changes(path) else "-"
        unstaged = "X" if self.has_unstaged_changes(path) else "-"
        untracked = "X" if self.has_untracked_changes(path) else "-"

        summary = (config.rootpath(), branch, changes, unstaged, untracked, rpath)
        summaries.append(summary)
        return summaries

    def perform(self, args):
        header = ("Path", "Branch", "Staged", "Unstaged", "Untracked", "Repo")
        header = self.__formatter.format(*header)
        print white(header)
        print "=" * (len(header) + 40)
        configs = self.repositories.exist()
        summaries = configs.reduce(self.execute, [])
        # bring the repos with changes to the top
        summaries = sorted(summaries, lambda x, y: cmp(x[2:5], y[2:5]),
                           reverse=True)
        for summary in summaries:
            s = self.__formatter.format(*summary)
            if 'X' == summary[2]:
                print green(s)
            elif 'X' == summary[3]:
                print blue(s)
            else:
                print s


class lsfiles(command):
    cmd = "ls-files"
    help = "print ls-files for repo(s)"

    def execute(self, value, config):
        results = git_out("ls-files", cwd=config.localpath())
        if results[0] != 0 or value != 0:
            return 1

        files = results[1]
        files = [os.path.join(config.rootpath(), file) for file in files]
        for file in files:
            print file.strip()
            pass
        return 0

    def perform(self, args):
        configs = self.repositories.exist()
        return configs.reduce(self.execute, 0)


class feature(command):
    cmd = None
    help = "Manage feature workflow"

    def perform(self, args):
        start = getattr(args, 'start-name', None)
        if start is not None:
            self.start(start)
        request = getattr(args, 'request-name', None)
        if request is not None:
            self.request(request, getattr(args, 'message', None))
        cleanup = getattr(args, 'cleanup-name', None)
        if cleanup is not None:
            self.cleanup(cleanup)

    def start(self, name):
        git_out("flow", "feature", "start", name)
        git_out("stash")
        git_out("flow", "feature", "publish", name)
        git_out("stash", "apply")

    def request(self, name=None, body=''):
        owner, repo, branch = repo_info()
        rebase_args = ["flow", "feature", "rebase"]
        if name:
            branch = "feature/" + name
            rebase_args.append(name)
        retcode, stdout, _ = git_out(*rebase_args)
        if retcode:
            print "Unable to make a pull request."
            return
        git_out("push", "origin", branch)
        response = github_api(
            "POST",
            "/repos/{0}/{1}/pulls".format(owner, repo),
            data=json.dumps({
                "title": "Please review branch %s" % branch,
                "body": body,
                "head": branch,
                "base": "develop"
            }))
        if 'url' in response:
            print "Pull Request: ", response['url']
        elif response['message'] == 'Validation Failed':
            for error in response['errors']:
                if error['message'].startswith("No commits between"):
                    print "You have to commit some code first!"
                    return
                else:
                    print error.get('message')


    def cleanup(self, name=None):
        owner, repo, branch = repo_info()
        finish_args = ["flow", "feature", "finish"]
        if name:
            branch = "feature/" + name
            finish_args.append(name)
        else:
            finish_args.append(branch.replace("feature/", ""))
        # Test to see if open pull request
        response = github_api(
            "GET",
            "/repos/{0}/{1}/pulls".format(owner, repo),
            data=json.dumps({
                "state": "open",
                "head": branch,
                "base": "develop"
            }))
        if not response:
            git_out("fetch", "origin")
            git_out(*finish_args)
            git_out("push", "origin", ":" + branch)
            git_out("pull")  # Fast-forward develop
        else:
            print "Pull request is still open."


    def add_help(self, parser):
        subparser = parser.add_subparsers()

        start = subparser.add_parser("start", help="Begin a reviewable change")
        start.add_argument("start-name", help="Feature name")

        request = subparser.add_parser("request", help="Ask for a pull request from the current branch")
        request.add_argument("request-name", help="Feature name (will autocomplete if possible)")
        request.add_argument("-m", help="Message", required=False)

        cleanup = subparser.add_parser("cleanup", help="Clean up the current feature branch")
        cleanup.add_argument("cleanup-name", help="Feature name to clean up")


def is_command_class(x):
    return inspect.isclass(x) and issubclass(x, command)


__module__ = sys.modules[__name__]
__classes__ = inspect.getmembers(__module__, is_command_class)
__classes__ = [cls() for (cls_name, cls) in __classes__ if cls_name != "command"]
__commands__ = dict([(cls.name(), cls) for cls in __classes__])


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
