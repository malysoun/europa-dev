yum -y install \
    python-devel \
    memcached \
    libmemcached-devel \
    vim-enhanced \
    bzip2 \
    bc \
    subversion \
    swig \
    rrdtool-devel \
    rrdtool-python \
    libxml2-devel \
    libxslt-devel \
    patch \
    protobuf-compiler \
    python-coverage \
    epydoc \
    libsmi \
    python-imaging \
    python-ipaddr \
    python-decorator \
    python-ldap \
    python-six \
    python-networkx \
    python-eventlet \
    python-celery \
    python-billiard \
    python-ZSI \
    python-suds \
    MySQL-python \
    python-lxml \
    nmap \
    python-memcached \
    python-sphinx \
    python-amqplib \
    python-txamqp \
    python-httplib2 \
    python-urllib3 \
    python-twisted \
    PyXML \
    redis \
    python-redis \
    mysql-server \
    protobuf-python \
    net-snmp-libs \
    libcap \
    supervisor \
    pcre-devel \
    openssl-devel \
    emacs-nox \
    autoconf \
    bison \
    flex \
    gcc \
    gcc-c++ \
    kernel-devel \
    make \
    m4 \
    java-1.7.0-openjdk \
    java-1.7.0-openjdk-devel \
    erlang

mkdir -pm 00755 /etc/profile.d
echo "export JAVA_HOME=/usr/lib/jvm/java" >> /etc/profile.d/jdk.sh
update-alternatives --install /usr/bin/java java /usr/lib/jvm/jre-1.7.0-openjdk/bin/java 1061 && update-alternatives --set java /usr/lib/jvm/jre-1.7.0-openjdk/bin/java
