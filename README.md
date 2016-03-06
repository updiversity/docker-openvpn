# OpenVPN for Rancher with PAM authentication

OpenVPN server image made to give access to Rancher network.

This Server doesn't relies on clients certificates, but on credential based authentication

First version is shipped with ldap authentication only, but several authentication methods will be implemented like :
- mysql
- kerberos
- ssh
- etc.

## How to configure the image

**The only mandatory variables are AUTH_METHOD, and method dependant variables.**

Each non mandatory environment variable is optionnal and has default value.

Following variables are the answers to common questions during certificate 
creation process 
- CERT_COUNTRY="US"
- CERT_PROVINCE="AL"
- CERT_CITY="Birmingham"
- CERT_ORG="ACME"
- CERT_EMAIL="nobody@example.com"
- CERT_OU="IT"

These variables define the network address and CIDR netmask for the ip pool which 
will be the VPN subnet for OpenVPN to draw client addresses from
- VPNPOOL_NETWORK="10.43.0.0"
- VPNPOOL_CIDR="16"

Next two variables are used in client configuration generation process, 
to indicate OpenVPN clients where to connect to establish the link
- REMOTE_IP="ipOrHostname"
- REMOTE_PORT="1194"

There is also an optionnal variable to let you customize OpenVPN server config, 
for example to push your own custom route
- OPENVPN_EXTRACONF=""

## How to run this image

**You must have to run this image with privileged mode.**

Here is the minimal docker run example with ldap authentication :
```sh
docker run -d --privileged=true -p 1194:1194 \
    -e AUTH_METHOD=ldap \
    -e AUTH_LDAP_URL=ldap://ldap.acme.tld \
    -e AUTH_LDAP_PATTERN='cn=$username,dc=acme,dc=tld' \
    mdns/rancher-openvpn
```

And here is an exhaustive docker run example with ldap authentication :
```sh
docker run -d \
    --privileged=true \
    -e REMOTE_IP=1.2.3.4 \
    -e REMOTE_PORT=1194 \
    -e CERT_COUNTRY=FR \
    -e CERT_PROVINCE=PACA \
    -e CERT_CITY=Marseille \
    -e CERT_ORG=MDNS \
    -e CERT_EMAIL=none@example.com \
    -e CERT_OU=IT \
    -e VPNPOOL_NETWORK=10.8.0.0 \
    -e VPNPOOL_CIDR=24 \
    -e OPENVPN_EXTRACONF='push "10.10.0.0 255.255.0.0"'
    -e AUTH_METHOD=ldap \
    -e AUTH_LDAP_URL=ldap://ldap.acme.tld \
    -e AUTH_LDAP_PATTERN='cn=$username,dc=acme,dc=tld' \
    -v /etc/openvpn \
    --name=vpn \
    -p 1194:1194 \
    mdns/rancher-openvpn
```

Note bene : First launch takes more time because of certificates and private keys generation
process

## Authentication methods

### LDAP

Authentication is made by trying to connect a ldap server with client credentials

These are mandatory variable to setup ldap authentication :

- AUTH_METHOD=ldap
- AUTH_LDAP_URL is the server address in URL format : AUTH_LDAP_URL=ldap(s)://hostnameOrIp[:port]
- AUTH_LDAP_PATTERN is the DN syntax to use in ldap login process, with a parameter $username, ex : AUTH_LDAP_PATTERN='uid=$username,ou=People,dc=acme,dc=tld'

You can test ldap authentication with osixia/openldap ldap docker image, with login "admin" :
```
docker run -d --name=ldap -e LDAP_ORGANISATION="ACME" -e LDAP_DOMAIN="acme.tld" -e LDAP_ADMIN_PASSWORD="mypwd" osixia/openldap:1.1.1
docker run -d --privileged=true -p 1194:1194 --link ldap:ldapsrv \
    -e AUTH_METHOD=ldap \
    -e AUTH_LDAP_URL=ldap://ldapsrv \
    -e AUTH_LDAP_PATTERN='cn=$username,dc=acme,dc=tld' \
    mdns/rancher-openvpn
```

## Client configuration

The client configuration is printed at dock start on stdout, but you can also 
retrieve it through the "vpn_get_client_config.sh" script.

```sh
docker exec -it vpn bash
root@35972bb51cc9:/# vpn_get_client_config.sh
remote $REMOTE_IP $REMOTE_PORT
client
dev tun
proto tcp
remote-random
resolv-retry infinite
cipher AES-128-CBC
auth SHA1
nobind
link-mtu 1500
persist-key
persist-tun
comp-lzo
verb 3
auth-user-pass
auth-retry interact
ns-cert-type server
<ca>
-----BEGIN CERTIFICATE-----
MIIEkjCCA3qgAwIBAgIJALhlg01BvAIvMA0GCSqGSIb3DQEBCwUAMIGMMQswCQYD
...
[Your generated OpenVPN CA certificate]
...
X0yOqF6doV0+DPt5T+vEeu9oiczscg==
-----END CERTIFICATE-----
</ca>
```

Save this configuration in your ".ovpn" file, don't forget to replace IPADDRESS 
and PORT with your server ip and the exposed port to reach OpenVPN server

Here is an example of a final client.ovpn :

```
remote 5.6.7.8 1194
client
dev tun
proto tcp
remote-random
resolv-retry infinite
cipher AES-128-CBC
auth SHA1
nobind
link-mtu 1500
persist-key
persist-tun
comp-lzo
verb 3
auth-user-pass
auth-retry interact
ns-cert-type server
<ca>
-----BEGIN CERTIFICATE-----
MIIEkjCCA3qgAwIBAgIJALhlg01BvAIvMA0GCSqGSIb3DQEBCwUAMIGMMQswCQYD
...
[Your generated OpenVPN CA certificate]
...
X0yOqF6doV0+DPt5T+vEeu9oiczscg==
-----END CERTIFICATE-----
</ca>
```

## Volumes and data conservation

Everything is stored in /etc/openvpn.
