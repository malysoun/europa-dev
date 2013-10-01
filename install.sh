#!/bin/bash

HERE=${PWD}
MSYS_HOME=$(find ~/AppData/Local/GitHub -name PortableGit_* -type d)
DOWNLOAD_ROOT="https://github.com/zenoss/europa-dev/raw/windows"
DOWNLOAD_ROOT="https://dl.dropboxusercontent.com/u/784231/windowslibs"

msys2win () {
    echo $(sh -c "cd $1; pwd -W")
}

# Install setuptools, pip and virtualenvwrapper
curl -fsSL https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py | python
curl -fsSL https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python
pip install virtualenvwrapper

# Install missing libraries
curl -o ${MSYS_HOME}/bin/getopt.exe ${DOWNLOAD_ROOT}/getopt.exe
curl -o ${MSYS_HOME}/bin/libintl3.dll ${DOWNLOAD_ROOT}/libintl3.dll
curl -o /usr/bin/mktemp.exe ${DOWNLOAD_ROOT}/mktemp.exe

# Install vagrant-berkshelf
vagrant plugin install vagrant-berkshelf

# Install git-flow
GITFLOWTMP=/tmp/gitflow
git clone --recursive git://github.com/nvie/gitflow.git ${GITFLOWTMP}
cmd.exe /c "$(msys2win ${GITFLOWTMP})\contrib\msysgit-install.cmd $(msys2win ${MSYS_HOME})"

# Modify .bashrc to include necessary vars
cat >> ${HOME}/.bashrc << EOF
export MSYS_HOME=${MSYS_HOME}
export PATH=\${PATH}:\${MSYS_HOME}/bin
export EUROPA_ROOT=${HERE}/europa
source /c/python27/scripts/virtualenvwrapper.sh
EOF

source ${HOME}/.bashrc

git clone git@github.com:zenoss/europa-dev.git ${EUROPA_ROOT}
mkvirtualenv europa -a ${EUROPA_ROOT}
cd ${EUROPA_ROOT} && git flow init -d
pip install -e ${EUROPA_ROOT}/utils/zenoss.europadev
git zen clone
