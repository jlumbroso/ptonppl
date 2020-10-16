
import distutils.version
import typing

import ldap


__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"

__all__ = [
    "LDAP_HOSTNAME",
    "LDAP_URI",
    "LDAP_24_API",
    "LDAP_BASE_DN",

    "ATTRIBUTES_TOP_LEVEL",
    "ATTRIBUTES_PUBLIC",
    "ATTRIBUTES_FULL",
    "ATTRIBUTE_MAPPING"
]


# Princeton LDAP server
LDAP_HOSTNAME: str = "ldap.princeton.edu"

# LDAP URI with protocol scheme
LDAP_URI: str = "ldap://{hostname}".format(hostname=LDAP_HOSTNAME)

# Flag on whether using SSL/TLS
LDAP_URI_SECURE: bool = "ldaps://" in LDAP_URI

# Determine which version of the LDAP package
LDAP_24_API: bool = (distutils.version.LooseVersion(ldap.__version__) >=
                     distutils.version.LooseVersion("2.4"))

# Base domain name for Princeton University
LDAP_BASE_DN: str = "o=Princeton University,c=US"


# Cached sets of attributes

ATTRIBUTES_TOP_LEVEL: typing.Set[str] = {"o", "c"}

ATTRIBUTES_PUBLIC: typing.Set[str] = {
    "cn",
    "displayName",
    "givenName",
    "mail",
    "objectClass",
    "pudisplayname",
    "sn"
}

ATTRIBUTES_FULL: typing.Set[str] = {
    "cn",
    "displayName",
    "eduPersonAffiliation",
    "eduPersonEntitlement",
    "eduPersonPrimaryAffiliation",
    "eduPersonPrincipalName",
    "facsimileTelephoneNumber",
    "givenName",
    "loginShell",
    "mail",
    "objectClass"
    "ou",
    "puacademiclevel",
    "puclassyear",
    "pudisplayname",
    "puhomedepartmentnumber",
    "puinterofficeaddress",
    "purescollege",
    "pustatus",
    "sn",
    "street",
    "telephoneNumber",
    "title",
    "uid",
    "universityid",
    "universityidref",
}

# Mappings with Princeton terminology

ATTRIBUTE_MAPPING = {
    "puid": "universityid",
    "netid": "uid",
    "email": "mail",
    "alias": "mail",
}
