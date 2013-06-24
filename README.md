europa-dev
==========

Europa Development Environment

Install
=======
   1. Install git-zen
      cd utils/zenoss.europadev/; python setup.py develop
   2. Checkout the Repos
      git-zen clone
   3. Ensure nfs file sharing is turned on
      - Mac (Mountain Lion) -- http://support.apple.com/kb/HT4695

   4. Start up a vagrant box (Fusion Instructions)
      cd vagrant/dev; vagrant up --provider=vmware_fusion

   5. Start up a vagrant box (VirtualBox Instructions)
      cd vagrant/dev; vagrant up

Notes
=====

Vagrant has a bug regarding fedora networking.  You may need to apply
https://github.com/mitchellh/vagrant/pull/1738 for fedora 18 to
load the networking properly

To alway choose vmware_fusion as your default provider set the env variable
like so.
export VAGRANT_DEFAULT_PROVIDER="vmware_fusion"

