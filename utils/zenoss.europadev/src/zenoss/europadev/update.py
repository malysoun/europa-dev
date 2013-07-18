from .git import clone, say, warn, debug
from .repository import Configurations
from .termutils import *


def main():
    debug.wrap = False
    say.wrap = False
    warn.wrap = False
    say("Updating europa-dev")
    root = Configurations.get().root()
    shell("git pull", cwd=root)
    say("Cloning any new repos")
    clone().perform(None)
    say("Installing utils package to register any new bin scripts")
    shell("pip install -e utils/zenoss.europadev > /dev/null 2>&1", cwd=root)
    say("Ensuring all develop branches track origin/develop")
    shell("git zen retrack > /dev/null 2>&1")
