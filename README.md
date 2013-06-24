europa-dev
==========

Europa Development Environment

Install
=======
NOTE: If you're on OS X with a case-insensitive filesystem, you should create a case-sensitive partition for your source, or Python imports will get confused.

   1. __Don't clone this repository directly__. Run this command, which will 
      set up the entire environment in the directory `./europa`:

        $ python -c "$(curl -fsSL https://raw.github.com/zenoss/europa-dev/go)"

    If you're planning to have a full Resource Manager development environment, run:

        $ EUROPAPRIVATE= python -c "$(curl -fsSL https://raw.github.com/zenoss/europa-dev/go)"

   2. Execute `workon europa` to enter the sandboxed development environment
      (issue the command `deactivate` to leave the sandbox). You can install
      Python packages using the `pip` in your `PATH` without affecting the rest of
      the system. You may need to open a new shell to get `workon` defined.

   3. See the state of your cloned repositories: 

        $ git zen xstatus
    
   4. Ensure nfs file sharing is turned on
      - Mac (Mountain Lion) -- http://support.apple.com/kb/HT4695
      - Ubuntu: `sudo apt-get install nfs-kernel-server`
   5. Start up your dev box.
    - VirtualBox:
      
            $ cd vagrant/dev
            $ vagrant up
            $ vagrant ssh

    - Fusion:

            $ cd vagrant/dev
            $ vagrant up --provider=vmware_fusion
            $ vagrant ssh

   6. You'll be in the box as the `vagrant` user, but Zenoss development should happen as the `zendev` user. Both are sudoers with `NOPASSWD:ALL`; the default password for `zendev` is `zendev`. `sudo su - zendev` to enter the Zenoss environment.
   7. The source checkouts on your host box are mounted via NFS on the dev box. You can use `git zen` (or just `git`) locally to modify them, or edit them locally.

Notes
=====

Vagrant has a bug regarding fedora networking.  You may need to apply
https://github.com/mitchellh/vagrant/pull/1738 for fedora 18 to
load the networking properly

To alway choose vmware_fusion as your default provider set the env variable
like so.

    export VAGRANT_DEFAULT_PROVIDER="vmware_fusion"


