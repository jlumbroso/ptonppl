
import distutils.version
import enum
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
    "LDAP_ATTRIBUTE_MAPPING"
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

LDAP_ATTRIBUTE_MAPPING = {
    "puid": "universityid",
    "netid": "uid",
    "email": "mail",
    "alias": "mail",
    "name": "cn",
}


# Web filter operations

class WebdirFilterOps(enum.Enum):
    CONTAINS = "c"
    IS = "eq"
    IS_NOT = "neq"
    BEGINS = "b"
    ENDS_WITH = "e"


class WebdirFields(enum.Enum):
    FIRST_NAME = "f"
    LAST_NAME = "l"
    TITLE = "t"
    DEPARTMENT = "d"
    ADDRESS = "a"
    PHONE = "p"
    FAX = "fa"
    NETID = "i"
    EMAIL = "e"


WEBDIR_FIELD_MAPPING = {
    "netid": WebdirFields.NETID,
    "email": WebdirFields.EMAIL,
    "alias": WebdirFields.EMAIL,
}


WEBDIR_EMAIL_FROM_NETID = "{}@princeton.edu"


# LDAP CMD constants

ID_AUTHORIZED_CHARS = "abcdefghijklmnopqrstuvwxyz.0123456789_"

LDAP_IGNORE_FIELDS = ["search", "result"]

LDAP_CMD_PATTERN = "{{}} -x -h {host} -u -b "


LDAP_CMD_PUID = ("""./ldapsearch -x -h ldap.princeton.edu -u """ + \
                                    """-b o='Princeton University,c=US' "universityid={puid}" """ + \
                                    """universityid cn uid eduPersonAffiliation pustatus ou""")

LDAP_IGNORE_FIELDS = ["search", "result"]



def run_cmd(cmd):
    (status, output) = commands.getstatusoutput(cmd)
    # If unsuspected problem, check here
    # FIXME: add error correction
    ## TO DEBUG:
    ## print "Content-type: text/plain\n\n", (status, output)
    ## if error 256 may be that the local copy of ldapsearch is outdated
    return output