from .git import clone
from .repository import Configurations
from .termutils import *


def main():
    root = Configurations.get().root()
    shell("git pull", cwd=root)
    clone().perform(None)
    shell("pip install -e utils/zenoss.europadev", cwd=root)
