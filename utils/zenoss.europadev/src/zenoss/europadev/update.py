from .git import clone, say, warn, debug
from .repository import Configurations
from .termutils import *


def main():
    debug.wrap = False
    say.wrap = False
    warn.wrap = False
    root = Configurations.get().root()
    shell("git pull", cwd=root)
    clone().perform(None)
    shell("pip install -e utils/zenoss.europadev", cwd=root)
