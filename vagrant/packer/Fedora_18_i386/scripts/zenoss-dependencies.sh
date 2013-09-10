yum -y install python-devel memcached libmemcached-devel vim-enhanced bzip2 bc subversion swig rrdtool-devel rrdtoo\
l-python libxml2-devel libxslt-devel patch protobuf-compiler python-coverage epydoc libsmi python-imaging python-ip\
addr python-decorator python-ldap python-six python-networkx python-eventlet python-celery python-billiard python-Z\
SI python-suds MySQL-python python-lxml nmap python-memcached python-sphinx python-amqplib python-txamqp python-htt\
plib2 python-urllib3 python-twisted PyXML redis python-redis mysql-server protobuf-python net-snmp-libs libcap supe\
rvisor pcre-devel openssl-devel emacs-nox autoconf bison flex gcc gcc-c++ kernel-devel make m4 java-1.7.0-openjdk j\
ava-1.7.0-openjdk-devel erlang
mkdir -pm 00755 /etc/profile.d
echo "export JAVA_HOME=/usr/lib/jvm/java" >> /etc/profile.d/jdk.sh
update-alternatives --install /usr/bin/java java /usr/lib/jvm/jre-1.7.0-openjdk/bin/java 1061 && update-alte\
rnatives --set java /usr/lib/jvm/jre-1.7.0-openjdk/bin/java


