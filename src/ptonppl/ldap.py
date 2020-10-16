
import typing

import ldap

import ptonppl.constants


__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"

__all__ = [
]


# If using LDAPS, ignore server side certificate errors (this assumes
# a self-signed certificate).

if ptonppl.constants.LDAP_URI_SECURE:
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_ALLOW)

# Don't follow referrals

ldap.set_option(ldap.OPT_REFERRALS, 0)

# Connect to server

_server: typing.Optional[ldap.ldapobject.LDAPObject] = None


def connect(
        reconnect: typing.Optional[bool] = None,
) -> ldap.ldapobject.LDAPObject:
    global _server

    if _server is None or (reconnect is not None and reconnect):
        _server = ldap.initialize(ptonppl.constants.LDAP_URI)
        _server.protocol_version = 3

    return _server


connect(reconnect=True)


# Determine attributes that are available

def get_attributes() -> typing.Set[str]:
    msg_id = _server.search_ext(
        ptonppl.constants.LDAP_BASE_DN,
        ldap.SCOPE_SUBTREE,
        sizelimit=100,
    )

    fields = set()

    while True:
        try:
            _, new_results = _server.result(msgid=msg_id, all=0)
        except ldap.LDAPError as error:
            break

        if new_results is None or type(new_results) is not list:
            break

        try:
            new_result = new_results[0]
            _, new_record = new_result
        except ValueError as error:
            break

        fields = fields.union(set(new_record.keys()))

    return fields


_ldap_attributes: typing.Set[str] = get_attributes()


# If we only have a small number of attributes in common with ATTRIBUTES_FULL
# we are probably in restricted LDAP

_ldap_restricted: bool = (
        len(_ldap_attributes.intersection(ptonppl.constants.ATTRIBUTES_FULL)) <=
        len(ptonppl.constants.ATTRIBUTES_PUBLIC)
)
