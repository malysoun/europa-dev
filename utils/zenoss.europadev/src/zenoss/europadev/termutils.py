import sys
import os
import subprocess
import platform
import textwrap

# Need function to get a single keypress from the user
try:
    # Try Windows
    # noinspection PyUnresolvedReferences
    import msvcrt
    getch = msvcrt.getch
except ImportError:
    # Everything else
    # noinspection PyUnresolvedReferences
    import tty, termios
    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


# Define terminal color-printing functions
def _color_func(colorcode):
    return lambda s: '\033[{0}m{1}\033[0m'.format(colorcode, s)


grey = _color_func(30)
red = _color_func(31)
green = _color_func(32)
yellow = _color_func(33)
blue = _color_func(34)
magenta = _color_func(35)
cyan = _color_func(36)
white = _color_func(37)


# Simple func to get full path relative to PWD
here = lambda *x: os.path.abspath(os.path.join(os.path.curdir, *x))


def say(msg):
    """
    Output a message to the console.
    """
    wrapped = textwrap.wrap(msg)
    print blue("==>"), white(wrapped[0])
    for line in wrapped[1:]:
        print "   ", white(line)


def warn(msg):
    print
    wrapped = textwrap.wrap(msg)
    print red("Warning") + ":", wrapped[0]
    for line in wrapped[1:]:
        print "        ", line


def execute(cmd, cwd=None):
    """
    Execute a command, printing it first.
    """
    say(' '.join(cmd) if isinstance(cmd, (list, tuple)) else cmd)
    return subprocess.call(cmd, shell=False, cwd=cwd)

def shell(cmd, cwd=None):
    """
    Run a shell command, printing it first.
    """
    say(' '.join(cmd) if isinstance(cmd, (list, tuple)) else cmd)
    return subprocess.call(cmd, shell=True, cwd=cwd)


def error(msg):
    print red("Error:"), msg


def abort(msg):
    error(msg)
    sys.exit(0)


def wait():
    print "Press", blue("ENTER"), "to continue or any other key to abort"
    ch = getch()
    if ord(ch) not in (10, 13):
        abort("Installation aborted by user")


def abort_unless(msg=None):
    print (msg or "Are you sure you want to continue"), blue("[") + "y/N" + blue("]"), "? ",
    ch = getch()
    print
    if ch not in "yY":
        abort("Installation aborted by user")


def which(cmd):
    p = subprocess.Popen(["which", cmd], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = p.communicate()
    return stdout


def verify(fname, description=None, use_which=True, die=True, warning=True):
    if use_which:
        result = bool(which(fname))
    else:
        result = os.path.exists(fname)
    if not result and warning:
        msg = "{0} is not present.".format(description or fname)
        (abort if die else warn)(msg)
    return result


def install(pkg):
    if sys.platform == 'darwin':
        if not verify("brew", die=False):
            say("Can't autoinstall {0} without Homebrew. Get it from http://mxcl.github.io/homebrew/")
        shell("brew install {0}".format(pkg))
    else:
        # Assume linux
        distro, version, ident = platform.linux_distribution()
        if distro.lower() in ("ubuntu", "debian"):
            shell("sudo apt-get install {0}".format(pkg))
        elif distro.lower() in ("centos", "rhel", "fedora"):
            shell("sudo yum -y install {0}".format(pkg))


def install_python(pkg, sudo=False):
    cmd = "pip install"
    if not verify("pip", warning=False):
        cmd = "easy_install"
        if not verify("easy_install", warning=False):
            abort("Neither pip nor setuptools is installed.")
    shell("{0} {1} {2}".format("sudo" if sudo else "", cmd, pkg))


