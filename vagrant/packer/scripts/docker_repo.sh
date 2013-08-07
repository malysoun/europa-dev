# install europa interna deps
rpm -i http://cmyum.zenoss.loc/yum/zenossdeps-private-5.0.x-1.fc18.x86_64.rpm 

rpm -i --force http://cmyum.zenoss.loc/yum/5.0.x/fc/18/os/x86_64/kernel-3.9.11-200.aufs.fc18.x86_64.rpm http://cmyum.zenoss.loc/yum/5.0.x/fc/18/os/x86_64/kernel-headers-3.9.11-200.aufs.fc18.x86_64.rpm

yum -y install 	aufs-util lxc

cd /tmp
rm docker* -Rf
wget http://get.docker.io/builds/Linux/x86_64/docker-latest.tgz
tar xfz docker-latest.tgz
cp docker-latest/docker /usr/bin/

cat > /etc/init.d/docker <<EOF
#!/bin/sh
#
# docker        init file for starting up the docker daemon
#
# chkconfig:   - 20 80
# description: Starts and stops the docker daemon.

# Source function library.
. /etc/rc.d/init.d/functions

name="docker"
exec="/usr/bin/\$name"
pidfile="/var/run/docker.pid"

[ -e /etc/sysconfig/docker ] && . /etc/sysconfig/docker

lockfile=/var/lock/subsys/docker

start() {
    [ -x \$exec ] || exit 5
    echo -n $"Starting $name: "
    daemon "\$exec -d"
    retval=\$?
    echo
    [ \$retval -eq 0 ] && touch \$lockfile
    return \$retval
}

stop() {
    echo -n $"Stopping \$name: "
    killproc -p \$pidfile \$name
    retval=\$?
    echo
    [ \$retval -eq 0 ] && rm -f \$lockfile
    return \$retval
}

restart() {
    stop
    start
}

reload() {
    false
}

rh_status() {
    status -p \$pidfile \$name
}

rh_status_q() {
    rh_status >/dev/null 2>&1
}

case "\$1" in
    start)
        rh_status_q && exit 0
        \$1
        ;;
    stop)
        rh_status_q || exit 0
        \$1
        ;;
    restart)
        \$1
        ;;
    reload)
        rh_status_q || exit 7
        \$1
        ;;
    force-reload)
        force_reload
        ;;
    status)
        rh_status
        ;;
    condrestart|try-restart)
        rh_status_q || exit 0
        restart
        ;;
    *)
        echo $"Usage: \$0 {start|stop|status|restart|condrestart|try-restart}"
        exit 2
esac
exit \$?
EOF

chmod +x /etc/init.d/docker
chkconfig docker on

cat > /etc/cron.d/docker_rprivate  <<EOF
SHELL=/bin/bash
PATH=/sbin:/bin:/usr/sbin:/usr/bin
@reboot root mount --make-rprivate /
EOF

