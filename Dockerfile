FROM debian:jessie
MAINTAINER Alexis Ducastel <alexis@ducastel.net>

RUN apt-get update && apt-get install -y \
    easy-rsa \
    dnsutils \
    iptables \
    netmask \
    mawk \
    rsync \
    openssl \
    openvpn \
    python-kerberos \
    python-ldap \
    python-paramiko \
    wget \
    && apt-get clean

COPY bin/* /usr/local/bin/
RUN chmod 744 /usr/local/bin/entry.sh && \
    chown root:root /usr/local/bin/entry.sh && \
    chmod 744 /usr/local/bin/openvpn-* && \
    chown root:root /usr/local/bin/openvpn-*

CMD ["/usr/local/bin/entry.sh"]
