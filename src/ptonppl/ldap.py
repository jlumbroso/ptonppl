
import typing

import backoff
import ldap

import ptonppl.abstract
import ptonppl.constants


__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"

__all__ = [
    "connect",
    "LdapPtonPerson",
    "search_one",
]


# If using LDAPS, ignore server side certificate errors (this assumes
# a self-signed certificate).

if ptonppl.constants.LDAP_URI_SECURE:
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_ALLOW)

# Don't follow referrals

ldap.set_option(ldap.OPT_REFERRALS, 0)

# Short time out (both for initial connection and follow-up operations)

ldap.set_option(ldap.OPT_NETWORK_TIMEOUT, 2)
ldap.set_option(ldap.OPT_TIMEOUT, 1)

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


# Determine attributes that are available (on a sample of 100 results)

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


def _ldap_do_we_give_up(
        err: typing.Union[ldap.SERVER_DOWN, ldap.TIMEOUT, Exception]
) -> bool:

    if isinstance(err, ldap.SERVER_DOWN) or isinstance(err, ldap.TIMEOUT):
        # reconnect ...
        connect(reconnect=True)

        # ... and retry
        return False

    # neither one of those exceptions, therefore we should fail
    return True


ldap_retry = backoff.on_exception(
    wait_gen=backoff.constant,
    exception=ldap.LDAPError,
    giveup=_ldap_do_we_give_up
)


@ldap_retry
def search_aux(
        ldap_filter: typing.Optional[str] = None,
        size_limit: int = 1,
):
    msg_id = _server.search_ext(
        base=ptonppl.constants.LDAP_BASE_DN,
        scope=ldap.SCOPE_SUBTREE,
        filterstr=ldap_filter,
        sizelimit=size_limit,
    )

    results = []

    while True:
        try:
            _, new_results = _server.result(msgid=msg_id, all=0)
            if new_results is None or len(new_results) == 0:
                break

            new_result = new_results[0]
            res_type, res_data = new_result

            aux_attrs = {
                field: value
                for (field, value) in map(lambda s: s.split("="), map(str.strip, res_type.split(",")))
                if field.lower() not in ptonppl.constants.ATTRIBUTES_TOP_LEVEL
            }
            res_data.update(aux_attrs)

            results.append(res_data)

        except ldap.SIZELIMIT_EXCEEDED:
            break

        except ValueError:
            continue

    return results


def search_many(
        ldap_field: str,
        ldap_value: str,
        size_limit: int = 1,
):
    if _ldap_restricted and ldap_field not in ptonppl.constants.ATTRIBUTES_PUBLIC:
        return None

    return search_aux(
        ldap_filter="{}={}".format(ldap_field, ldap_value),
        size_limit=size_limit,
    )


def _grab_attr(
        ldap_obj: typing.Dict[str, typing.Any],
        ldap_field: str
) -> typing.Optional[typing.Any]:

    if ldap_obj is None:
        return

    val = ldap_obj.get(ldap_field)
    if val is None:
        return

    if type(val) is list:
        try:
            val = val[0]
        except ValueError:
            pass

    if type(val) is bytes:
        val = val.decode("ascii")

    return val


class LdapPtonPerson(ptonppl.abstract.AbstractPtonPerson):

    def __init__(self, ldap_result: typing.Dict[str, typing.Any]):
        self._original = ldap_result

        self._puid = _grab_attr(self._original, ptonppl.constants.LDAP_ATTRIBUTE_MAPPING["puid"])
        self._netid = _grab_attr(self._original, ptonppl.constants.LDAP_ATTRIBUTE_MAPPING["netid"])
        self._email = _grab_attr(self._original, ptonppl.constants.LDAP_ATTRIBUTE_MAPPING["email"])
        self._alias = _grab_attr(self._original, ptonppl.constants.LDAP_ATTRIBUTE_MAPPING["alias"])
        self._pustatus = _grab_attr(self._original, "pustatus")
        self._cn = _grab_attr(self._original, ptonppl.constants.LDAP_ATTRIBUTE_MAPPING["name"])

        if self._email is None:
            val = _grab_attr(self._original, "eduPersonPrincipalName")
            if "@" in val:
                self._email = val

        if self._alias is not None:
            self._alias = self._alias.split("@")[0]


def search_one(
        ldap_field: str,
        ldap_value: str,
) -> typing.Optional[LdapPtonPerson]:

    ret = search_many(
        ldap_field=ldap_field,
        ldap_value=ldap_value,
        size_limit=1,
    )

    if ret is not None and len(ret) > 0:
        return LdapPtonPerson(ldap_result=ret[0])
