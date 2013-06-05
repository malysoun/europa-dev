import os
import argparse
from .termutils import shell


def update(args):
    pass


def options():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="Sub-command help")

    update = subparsers.add_parser("update", help="Update repos")
    update.add_argument("--all", action="store_true", default="False", 
                        help="Act on all repositories")
    update.add_argument("repository")
    return parser.parse_args()


def main():
    args = options()
    if args.update:
        update(args)


def git(cmd):
    shell((os.environ.get("GIT") or "git") + " " + cmd)
