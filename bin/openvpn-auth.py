#!/usr/bin/python

"""
Authentication handler for OpenVPN by Alexis Ducastel
"""

import os
import sys
import ldap
import kerberos
import requests
from requests.auth import HTTPBasicAuth
from requests.auth import HTTPDigestAuth

def auth_success(username):
    """ Authentication success, simply exiting with no error """
    print "[INFO] OpenVPN Authentication success for " + username
    exit(0)


def auth_failure(reason, severity="INFO"):
    """ Authentication failure, rejecting login with a stderr reason """
    print >> sys.stderr, "["+severity+"] OpenVPN Authentication failure : " + reason
    exit(1)

def auth_http_basic(url, username, password):
    if (requests.get(url, auth=HTTPBasicAuth(username, password))):
        auth_success(username)
    else:
        auth_failure("Invalid credentials for username "+ username)

def auth_http_digest(url, username, password):
    if (requests.get(url, auth=HTTPDigestAuth(username, password))):
        auth_success(username)
    else:
        auth_failure("Invalid credentials for username "+ username)

def auth_rancher_local(url, username, password):
    if (requests.post(url, data = { "authProvider": "localauthconfig", "code": username + ":" + password})):
        auth_success(username)
    else:
        auth_failure("Invalid credentials for username "+ username)

if all (k in os.environ for k in ("username","password","AUTH_METHOD")):
    username = os.environ.get('username')
    password = os.environ.get('password')
    auth_method = os.environ.get('AUTH_METHOD')

    #=====[ HTTP Basic ]==============================================================
    # How to test:
    #   Just test against github api url : https://api.github.com/user
    # Example :
    #   AUTH_METHOD='httpbasic'
    #   AUTH_URL='http[s]://hostname[:port][/uri]'
    #
    elif auth_method=='httpbasic':
        if "AUTH_URL" in os.environ:
            url=os.environ.get('AUTH_URL')
            auth_http_basic(url, username, password)
        else:
            auth_failure('Missing mandatory environment variable for authentication method "httpbasic" : AUTH_HTTPBASIC_URL')

    #=====[ HTTP Digest ]==============================================================
    # How to test:
    #   Just test against httpbin sandbox url : https://httpbin.org/digest-auth/auth/user/pass
    # Example :
    #   AUTH_METHOD='httpdigest'
    #   AUTH_URL='http[s]://hostname[:port][/uri]'
    #
    elif auth_method=='httpdigest':
        if "AUTH_URL" in os.environ:
            url=os.environ.get('AUTH_URL')
            auth_http_digest(url, username, password)
        else:
            auth_failure('Missing mandatory environment variable for authentication method "httpdigest" : AUTH_HTTPDIGEST_URL')

    #=====[ Rancher local ]==============================================================
    # How to test:
    #   @todo
    # Example :
    #   AUTH_METHOD='rancherlocal'
    elif auth_method=='rancherlocal':
        if "AUTH_URL" in os.environ:
            url=os.environ.get('AUTH_URL')
            auth_rancher_local(url, username, password)
        else:
            auth_failure('Missing mandatory environment variable for authentication method "rancherlocal" : AUTH_RANCHERLOCAL_URL')

    # No method handler found
    else:
        auth_failure('No handler found for authentication method "'+ auth_method +'"')

else:
    auth_failure("Missing one of following environment variables : username, password, or AUTH_METHOD")
