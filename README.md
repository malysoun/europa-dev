Zenoss Europa Development Environment
=====================================

__Important: Do not clone this repository (yet). Read on for instructions.__

Requirements
------------
   1. [VirtualBox][] (at least version 4.2.18)
   2. [Vagrant][] (version 1.3.x, __required. Older versions will not work.__)
   3. Early adopters may also need to install the Vagrant [Berkshelf][] plugin:

          vagrant plugin install vagrant-berkshelf

      If, however, you're about to run this from scratch, it will be installed
      for you.
   4. Understand the [git-flow][] workflow; our `git zen feature` workflow is
      a superset thereof. Check out DataSift's [git-flow for GitHub][]
      documentation for a description of a very similar workflow.

Installation
------------
### Linux

   1. If you've previously built Zenoss and are running it on the host box on
      which you plan to set up europa-dev, you need to ensure you aren't using
      Zenoss's custom Python environment.  Run ``which python``; if it's under
      $ZENHOME (e.g., /opt/zenoss/bin/python), either remove the modifications
      that add $ZENHOME/bin to your $PATH or specify system python (e.g.,
      /usr/bin/python) in step 3. Consider using a function like [zenv][]
      to switch between Zenoss and system Python environments.

   2. Set up git credentials to avoid being asked for passwords constantly. On
      OS X, run:

        $ git config --global credential.helper osxkeychain

      On other platforms, run: 

        $ git config --global credential.helper 'cache --timeout=86400'

      See <https://help.github.com/articles/set-up-git> for more information.

   3. __Don't clone this repository directly__. Run this command, which will 
      set up the entire environment in the directory `./europa`:

        $ python -c "$(curl -fsSL https://raw.github.com/malysoun/europa-dev/go/install)"

    If you're planning to have a full Resource Manager development environment, run:

        $ EUROPAPRIVATE= python -c "$(curl -fsSL https://raw.github.com/malysoun/europa-dev/go/install)"

    This will verify that several things are installed and try to install them
    (asking for confirmation first) if not, including [VirtualBox][], 
    [Vagrant][], [Berkshelf][] and [git-flow][].

   4. Execute `workon europa` to enter the sandboxed development environment
      (issue the command `deactivate` to leave the sandbox). You can install
      Python packages using the `pip` in your `PATH` without affecting the rest of
      the system. You may need to open a new shell to get `workon` defined.

   5. See the state of your cloned repositories: 

        $ git zen xstatus
    
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

   7. Optional: Add the custom script `~/.europarc`

      If you have certain things you want to run every time you provision
      a vagrant box (SSH keys, dotfiles, custom packages), you can put them in
      a script at `~/.europarc`. This script will be executed by Vagrant on the
      dev box as root at the end of provisioning. A 
      [sample script](https://github.com/zenoss/europa-dev/blob/develop/europarc.sample) 
      is included with europa-dev.

   8. Optional: Use NFS instead of VirtualBox shared folders. NFS is much
      faster and will provide a significant reduction in build time where
      filesystem operations are numerous (e.g., assembling fat JARs). You will
      need NFS installed on your host box. Edit `europa/vagrant/dev/Vagrantfile`.  
      Comment out the existing synced_folder configuration:

          config.vm.synced_folder "../../src", "/zensrc", owner:"zendev",
              group:"zendev", :mount_options => ['dmode=775','fmode=775']

      And uncomment the NFS version:

          #config.vm.synced_folder "../../src", "/zensrc", :nfs => true

   9. Start up your dev box.
    - VirtualBox:
      
            $ cd vagrant/dev
            $ vagrant up
            $ vagrant ssh
    - Fusion:

            $ cd vagrant/dev
            $ vagrant up --provider=vmware_fusion
            $ vagrant ssh

   10. This box no longer uses a `vagrant` user; the default username is
      `zendev`, and all development should happen as the `zendev` user, who
      has sudo privileges with `NOPASSWD:ALL`; the default password for 
      `zendev` is `zendev`.

   11. Optional: Install SSH keys (if you skipped step 6 and 7). Run on the host box:

        cat ~/.ssh/id_rsa.pub | ssh zendev@192.168.33.10 "cat >> ~/.ssh/authorized_keys"

      Of course, change `id_rsa.pub` to `id_dsa.pub` if that's the file containing your
      public key.

   12. Set up SSH config. Run on the host box: 

        cat <<EOF>> ~/.ssh/config
        Host zendev
            User zendev
            HostName 192.168.33.10
        EOF

      You will them be able to run "ssh zendev" without specifying user or
      modifying your hosts file.

   13. The source checkouts on your host box are mounted as shared folders on
       the dev box. You can use `git zen` (or just `git`) locally to modify
       them, or edit them locally.

### OS X
If you have a case-insensitive filesystem, create a separate source partition
with a case-sensitive filesystem in Disk Utility, and run the Linux
instructions relative to that root. Otherwise, Python imports that differ only
in case (of which a couple exist in the product) will get confused.

### Windows
This is a wild ride. Prepare yourself.

   1. Install [Python][] 2.7.x using the Windows installer. Install it for all
      users to the default location, C:\Python27. Customize nothing.

   2. In Explorer, right-click on "Computer". Select "Properties", then
      "Advanced System Settings". Click "Environment Variables". Edit the
      system variable "Path" (semicolon-delimited) to include C:\Python27 and
      C:\Python27\Scripts at the end.

   3. Install [GitHub for Windows][]. This will also install .NET if you don't
      have it already. Log in using your normal GitHub account. Clone any repo
      to anywhere, which will force SSH keys to be set up properly (you can
      delete this repo later). Select Tools > Options... and select "Git Bash"
      as your default shell. Click "Update". Close.

   4. Double-click on "Git Shell" on your desktop. This will open up a window
      running bash.

   5. cd to the directory in which you want a europa environment installed and 
      execute:

          curl -fsSL https://github.com/zenoss/europa-dev/raw/windows/install.sh | bash

      This script, comparable to the *NIX "go" script, will set up git-flow,
      virtualenv, vagrant-berkshelf, create a Europa environment, install the
      development tools package, and clone all the repositories.

   6. Skip to step 4 of the Linux installation instructions. Bear in mind
      Windows will not allow sharing of folders via NFS, so ignore that part.



[zenv]: https://intranet.zenoss.com/docs/DOC-2401
[Virtualbox]: https://www.virtualbox.org/
[GitHub for Windows]: http://windows.github.com
[Python]: http://python.org/download
[Vagrant]: http://www.vagrantup.com/
[Berkshelf]: http://berkshelf.com/
[git-flow]: https://github.com/nvie/gitflow 
[git-flow for GitHub]: http://datasift.github.io/gitflow/GitFlowForGitHub.html


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

To force the develop branch of all repos to track origin/develop, run `git zen
retrack`.

### git zen feature
`git zen feature` encapsulates the workflow (based on [git-flow][]) for
developing against Zenoss code, in a GitHub-aware way. See the image in
DataSift's [git-flow for GitHub][] docs for a diagram of the branching model.
You should use `git zen feature` to make sure you don't miss something. Here's
how it works:

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

* VirtualBox 4.2.14 has a [Vagrant bug][] you may encounter. When running
  `vagrant up`, you may get this error:
  
        Progress object failure: NS_ERROR_CALL_FAILED
  
  If so, you need to create a manifest file. Run this, where ``BOX_NAME`` is
  "europa-dev" or "fedora18":
  
        cd ~/.vagrant.d/boxes/[BOX_NAME]/virtualbox
        openssl sha1 *.vmdk *.ovf > box.mf
  
  Then try again.

[Vagrant bug]: https://www.virtualbox.org/ticket/11895

* Vagrant has a bug regarding Fedora networking when you attempt to start two boxes 
  with the same private IP, in that the message is confusing (refers to interface p7p1). 
  If you encounter this, simply change the Vagrantfile to have a different IP.

  On Vagrant >= 1.2.5, this may occur without a second box being up (see [open
  issue][]). Applying the [patch][] to Vagrant itself should fix the problem.

  Update: The fix for this issue is included in Vagrant 1.3.0 and above. If
  you're using the supported version you should not see this.

[open issue]: https://github.com/mitchellh/vagrant/pull/1738
[patch]: https://github.com/mitchellh/vagrant/commit/ea89b43a06bf65d3ae0fa90924caeb67d62b82d8 

* To alway choose vmware_fusion as your default provider set the env variable
  like so.

    export VAGRANT_DEFAULT_PROVIDER="vmware_fusion"

### Useful bash aliases
    alias vp="vagrant provision"
    alias vs="vagrant ssh"
    alias vu="vagrant up"
    alias vd="vagrant destroy"
