
import base64
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
    BEGINS_WITH = "b"
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

PRINCETON_CAMPUS_DIRECTORY_SEARCH_URL = \
    "https://www.princeton.edu/search/people-advanced?{field}={{}}&{field}f={filter_op}"


# URL to build queries to search the campus directory by email address equality
# NOTE: for email, had to switch to "begins with" because of bug in search

PRINCETON_CAMPUS_DIRECTORY_EMAIL_SEARCH_URL = PRINCETON_CAMPUS_DIRECTORY_SEARCH_URL.format(
    field=WebdirFields.EMAIL.value,
    filter_op=WebdirFilterOps.BEGINS_WITH.value,
)
PRINCETON_CAMPUS_DIRECTORY_NETID_SEARCH_URL = PRINCETON_CAMPUS_DIRECTORY_SEARCH_URL.format(
    field=WebdirFields.NETID.value,
    filter_op=WebdirFilterOps.IS.value,
)


# LDAP CMD constants

ID_AUTHORIZED_CHARS = "abcdefghijklmnopqrstuvwxyz.0123456789_"

LDAP_IGNORE_FIELDS = ["search", "result"]

LDAP_CMD_PATTERN = "{{cmd}} -x -h {host} -u -b {base_dn} \"{{query}}\"".format(
    host=LDAP_HOSTNAME,
    base_dn=LDAP_BASE_DN,
)

LDAP_DEFAULT_CMD = "ldapsearch"

LDAP_QUERY_NETID = "uid={}"

LDAP_QUERY_EMAIL = "mail={}"

LDAP_QUERY_PUID = "universityid={}"

LDAP_DEFAULT_PROXY_URL = base64.b64decode(
    b'aHR0cHM6Ly9lZHV0b29scy5jcy5wcmluY2V0b24uZWR1L2ludGVncmF0aW9uL2xkYXAuY2dp'.decode("ascii")
).decode("ascii")

PARSED_LDAP_KEY = "uid"


# Output formats
OUTPUT_CSV_HEADER = ["puid", "netid", "email", "alias", "type", "name"]
