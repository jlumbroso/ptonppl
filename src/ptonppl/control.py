
import typing

import ptonppl.abstract
import ptonppl.constants
import ptonppl.ldap
import ptonppl.ldapcmd
import ptonppl.webdir


__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"

__all__ = [
    "search",
]


def search(
        value: str,
) -> typing.Optional[ptonppl.abstract.AbstractPtonPerson]:

    obj: typing.Optional[ptonppl.abstract.AbstractPtonPerson] = None

    attempts = []

    if "@" in value:

        # using `old_value` instead of `val` is intentional here
        old_value = value
        attempts += [lambda _: ptonppl.ldap.search_one(ldap_field="mail", ldap_value=old_value)]
        attempts += [lambda _: ptonppl.webdir.search_one(field="mail", value=old_value)]
        attempts += [lambda _: ptonppl.ldapcmd.search_one(ldap_field="mail", ldap_value=old_value)]

        # remove suffix of email, as it might match an alias or a NetID search
        value = value.split("@")[0]

    else:
        possible_email = ptonppl.constants.WEBDIR_EMAIL_FROM_NETID.format(value)

        attempts += [lambda _: ptonppl.ldap.search_one(ldap_field="mail", ldap_value=possible_email)]
        attempts += [lambda _: ptonppl.webdir.search_one(field="mail", value=possible_email)]
        attempts += [lambda _: ptonppl.ldapcmd.search_one(ldap_field="mail", ldap_value=possible_email)]

    # operations for NetID and alias

    attempts += [lambda val: ptonppl.ldap.search_one(ldap_field="uid", ldap_value=val)]
    attempts += [lambda val: ptonppl.ldap.search_one(
        ldap_field="mail", ldap_value=ptonppl.constants.WEBDIR_EMAIL_FROM_NETID.format(val))]
    attempts += [lambda val: ptonppl.webdir.search_one(field="uid", value=val)]
    attempts += [lambda val: ptonppl.webdir.search_one(field="alias", value=val)]
    attempts += [lambda val: ptonppl.ldapcmd.search_one(ldap_field="uid", ldap_value=val)]
    attempts += [lambda val: ptonppl.ldapcmd.search_one(
        ldap_field="mail", ldap_value=ptonppl.constants.WEBDIR_EMAIL_FROM_NETID.format(val))]

    # heuristic for PUIDs
    if value.isdigit() and len(value) > 6:
        attempts += [lambda val: ptonppl.ldap.search_one(ldap_field="universityid", ldap_value=val)]
        attempts += [lambda val: ptonppl.ldapcmd.search_one(ldap_field="universityid", ldap_value=val)]

    # reestablish connection
    ptonppl.ldap.connect(reconnect=True)

    for f in attempts:
        try:
            new_obj = f(value)
        except ValueError:
            continue

        if new_obj is None:
            continue

        elif obj is None:
            obj = new_obj

        else:
            obj = obj.merge(obj=new_obj)

        if obj.complete:
            break

    return obj
