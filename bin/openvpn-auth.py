#!/usr/bin/python

"""
Authentication handler for OpenVPN by Alexis Ducastel
"""

import os
import sys
import ldap
import kerberos

def auth_success():
    """ Authentication success, simply exiting with no error """
    exit(0)
    

def auth_failure(reason):
    """ Authentication failure, rejecting login with a stderr reason """
    print >> sys.stderr, "[INFO] OpenVPN Authentication failure : " + reason
    exit(1)

def auth_ldap(address,pattern,password):
    """ Ldap authentication handler """
    try:
        conn = ldap.initialize(address)
        conn.protocol_version = 3
        conn.set_option(ldap.OPT_REFERRALS, 0)
        result = conn.simple_bind_s(pattern, password)
    except ldap.INVALID_CREDENTIALS:
         auth_failure("Invalid credentials for "+ username)
    except ldap.SERVER_DOWN:
        auth_failure("Server unreachable")
    except ldap.LDAPError, e:
        if type(e.message) == dict and e.message.has_key('desc'):
            auth_failure("LDAP error: " + e.message['desc'])
        else: 
            auth_failure("LDAP error: " + e)
    finally:
        conn.unbind_s()
    
    auth_success()



if all (k in os.environ for k in ("username","password","AUTH_METHOD")):
    username = os.environ.get('username') 
    password = os.environ.get('password') 
    auth_method = os.environ.get('AUTH_METHOD') 

    #=====[ LDAP ]==============================================================
    # How to test:
    #   https://github.com/osixia/docker-openldap
    #   docker run -d --name=ldap --env LDAP_ORGANISATION="ACME" --env LDAP_DOMAIN="acme.tld" --env LDAP_ADMIN_PASSWORD="mypwd" osixia/openldap:1.1.1
    #   docker exec ldap ldapsearch -x -h localhost -b dc=acme,dc=tld -D "cn=admin,dc=acme,dc=tld" -w admin
    # Example :
    #   AUTH_METHOD='ldap'
    #   LDAP_URL='ldap(s)://ldap.acme.tld[:port]'
    #   LDAP_PATTERN='cn=$username,dc=acme,dc=tld'
    if auth_method=='ldap':
        if all (k in os.environ for k in ("AUTH_LDAP_URL","AUTH_LDAP_PATTERN")):
            address=os.environ.get('AUTH_LDAP_URL') 
            pattern=os.environ.get('AUTH_LDAP_PATTERN').replace('$username',username) 
            auth_ldap(address,pattern,password)

        else:
            auth_failure('Missing one of mandatory environement variables for authentication method "ldap" : AUTH_LDAP_URL or AUTH_LDAP_PATTERN')
            
    #=====[ Kerberos ]==============================================================
    # How to test:
    #   @todo
    # Example :
    #   AUTH_METHOD='kerberos'
    elif auth_method=='kerberos':
        auth_failure('Not implemented')

        #if all (k in os.environ for k in ("KERBEROS_REALM")):
        #    realm=os.environ.get('KERBEROS_REALM') 
        #    if not kerberos.checkPassword(username,password,realm):
        #        auth_failure("Invalid credentials for " + username)
        #    else:
        #        auth_success()
        #else:
        #    auth_failure("Missing mandatory environement variable KERBEROS_REALM")

    # No method handler found
    else:
        auth_failure('No handler found for authentication method "'+ auth_method +'"')

else:
    auth_failure("Missing one of following environment variables : username, password, or AUTH_METHOD")

