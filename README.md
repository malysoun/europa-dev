Zenoss Europa Development Environment
=====================================

Installation
------------
NOTE: If you're on OS X with a case-insensitive filesystem, you should create a case-sensitive partition for your source, or Python imports will get confused.

   1. Set up git credentials to avoid being asked for passwords constantly. On
      OS X, run:

        $ git config --global credential.helper osxkeychain

      On other platforms, run: 

        $ git config --global credential.helper 'cache --timeout=86400'

      See <https://help.github.com/articles/set-up-git> for more information.

   2. __Don't clone this repository directly__. Run this command, which will 
      set up the entire environment in the directory `./europa`:

        $ python -c "$(curl -fsSL https://raw.github.com/zenoss/europa-dev/go)"

    If you're planning to have a full Resource Manager development environment, run:

        $ EUROPAPRIVATE= python -c "$(curl -fsSL https://raw.github.com/zenoss/europa-dev/go)"

    This will verify that several things are installed and try to install them
    (asking for confirmation first) if not, including [Virtualbox][], 
    [Vagrant][] and [git-flow][].

   3. Execute `workon europa` to enter the sandboxed development environment
      (issue the command `deactivate` to leave the sandbox). You can install
      Python packages using the `pip` in your `PATH` without affecting the rest of
      the system. You may need to open a new shell to get `workon` defined.

   4. See the state of your cloned repositories: 

        $ git zen xstatus
    
   5. Ensure nfs file sharing is turned on
      - Mac (Mountain Lion) -- http://support.apple.com/kb/HT4695
      - Ubuntu: `sudo apt-get install nfs-kernel-server`

   6. Optional: Set up authorized_keys. Find the line in Vagrantfile:

        chef.json = {
            :zenoss => {
                ...
                :authorized_keys => ""
            }
            ...
        }

     Paste the contents of ~/.ssh/id_rsa.pub or ~/.ssh/id_dsa.pub as the value
     assigned to authorized_keys.

   7. Start up your dev box.
    - VirtualBox:
      
            $ cd vagrant/dev
            $ vagrant up
            $ vagrant ssh
    - Fusion:

            $ cd vagrant/dev
            $ vagrant up --provider=vmware_fusion
            $ vagrant ssh

   8. You'll be in the box as the `vagrant` user, but Zenoss development should happen as the `zendev` user. Both are sudoers with `NOPASSWD:ALL`; the default password for `zendev` is `zendev`. `sudo su - zendev` to enter the Zenoss environment.

   9. Optional: Install SSH keys (if you skipped step 6). Run on the host box:

        cat ~/.ssh/id_rsa.pub | ssh zendev@192.168.33.10 "cat >> ~/.ssh/authorized_keys"

      Of course, change `id_rsa.pub` to `id_dsa.pub` if that's the file containing your
      public key.

   10. Set up SSH config. Run on the host box: 

        cat <<EOF>> ~/.ssh/config
        Host zendev
            User zendev
            HostName 192.168.33.10
        EOF

      You will them be able to run "ssh zendev" without specifying user or
      modifying your hosts file.

   11. The source checkouts on your host box are mounted via NFS on the dev box. You can use `git zen` (or just `git`) locally to modify them, or edit them locally.


[Virtualbox]: https://www.virtualbox.org/
[Vagrant]: http://www.vagrantup.com/
[git-flow]: https://github.com/nvie/gitflow 


Working with your environment
-----------------------------
Run `workon europa` to enter your dev environment. Once in the environment,
several commands are available to make things simpler.

### cdproject/cdvirtualenv
These commands will switch to your dev environment root and the virtualenv
environment directory (with lib/python2.7), respectively. These are included
with virtualenvwrapper, which is installed automatically.

### upeuropa
The process of updating your Europa dev environment is encapsulated in the
`upeuropa` command. It will pull the latest environment code, clone any missing
repositories, and reinstall the utilities package to make sure you get the
latest scripts or environment dependencies. Do this instead of "git pull".

### git zen
`git zen` is a utility that will run various commands across your Zenoss git
repositories. Those repositories are defined in `repos` and `private/repos`. If
you want a new repository to be part of your development environment, add
a line to `repos` of the format `{path}, {repo URL}` and run `git zen clone`.

To see a simple status of changes in your repos, run `git zen status`.

To see an extended status of your repos, run `git zen xstatus`.

To pull changes for all of your repos, run `git zen pull`.

### git zen feature
`git zen feature` encapsulates the workflow (based on [git-flow][]) for
developing against Zenoss code. You should use it to make sure you don't miss
something. Here's how it works:

   1. `git zen feature start my-new-feature`.
      This will create a local feature branch, based off `develop`, called
      `feature/my-new-feature` tracking a remote branch of the same name. It
      is the equivalent of running these commands:

         $ git flow feature start my-new-feature
         $ git stash
         $ git flow feature publish my-new-feature
         $ git stash apply

   2. __Change code, `git commit`, etc.__ Use git normally while on this 
      branch. `git push` to publish the code to GitHub.
  
   3. `git zen feature request [my-new-feature]`. If you're on the branch,
      you don't have to specify its name. This command will make sure that 
      you've pushed up any outstanding changes and create a [pull request][] to 
      get your code merged into the `develop` branch. It is the equivalent of
      performing these actions:

         $ # Verify you have no uncommitted changes
         $ git push origin feature/my-new-feature
         $ # Create a pull request in GitHub from feature/my-new-feature to develop

   4. __Get code reviewed. Make updates simply by committing/pushing.__ When
      satisfied, the reviewer will merge the changes in the pull request
      interface on GitHub.

   5. `git zen feature cleanup [my-new-feature]`. If you're on the branch,
      you don't have to specify its name. This will make sure the code was
      all merged, get your local repo up to date with the remote `develop` 
      branch, delete the now-unnecessary local branch, and delete the remote
      branch it's tracking. This is the equivalent of performing these
      actions:

         $ # Verify the pull request has been closed
         $ git fetch origin
         $ git branch --merged origin/develop # Verify feature/my-new-feature
         $ git flow feature finish feature/my-new-feature
         $ git push origin :feature/my-new-feature
         $ git pull  # Fast-forward develop

[pull request]: https://help.github.com/articles/using-pull-requests


Modifying europa-dev
--------------------
Feel free to keep your own copy of europa-dev with your own custom modifications.
Once you've created your environment, simply [create a fork][] of europa-dev in
GitHub, then execute:

    $ git remote set-url origin https://github.com/{MYUSERNAME}/europa-dev
    $ git remote add upstream https://github.com/zenoss/europa-dev

If you have changes that would be useful for everyone, please make a pull
request to get it into the upstream repository.

If changes are made to the upstream repo that you want to pull in, run:

    $ git pull upstream master

[create a fork]: https://help.github.com/articles/fork-a-repo

Notes
-----

Vagrant has a bug regarding fedora networking.  You may need to apply
https://github.com/mitchellh/vagrant/pull/1738 for fedora 18 to
load the networking properly.

To alway choose vmware_fusion as your default provider set the env variable
like so.

    export VAGRANT_DEFAULT_PROVIDER="vmware_fusion"

### Useful bash aliases
    alias vp="vagrant provision"
    alias vs="vagrant ssh"
    alias vu="vagrant up"
    alias vd="vagrant destroy"
