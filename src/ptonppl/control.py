
import typing

import ptonppl.abstract
import ptonppl.constants
import ptonppl.ldap
import ptonppl.ldapcmd
import ptonppl.webdir


def search(
        value: str,
) -> typing.Optional[ptonppl.abstract.AbstractPtonPerson]:

    obj: typing.Optional[ptonppl.abstract.AbstractPtonPerson] = None

    attempts = []

    if "@" in value:
        attempts += [lambda val: ptonppl.ldap.search_one(ldap_field="mail", ldap_value=val)]
        attempts += [lambda val: ptonppl.webdir.search_one(field="mail", value=val)]
        attempts += [lambda val: ptonppl.ldapcmd.search_one(ldap_field="mail", ldap_value=val)]

        # remove suffix of email, as it might match an alias or a NetID search
        value = value.split("@")[0]

    # operations for NetID and alias

    attempts += [lambda val: ptonppl.ldap.search_one(ldap_field="uid", ldap_value=val)]
    attempts += [lambda val: ptonppl.ldap.search_one(
        ldap_field="mail", ldap_value=ptonppl.constants.WEBDIR_EMAIL_FROM_NETID.format(val))]
    attempts += [lambda val: ptonppl.webdir.search_one(field="uid", value=val)]
    attempts += [lambda val: ptonppl.webdir.search_one(field="alias", value=val)]
    attempts += [lambda val: ptonppl.ldapcmd.search_one(ldap_field="uid", ldap_value=val)]
    attempts += [lambda val: ptonppl.ldapcmd.search_one(
        ldap_field="mail", ldap_value=ptonppl.constants.WEBDIR_EMAIL_FROM_NETID.format(val))]

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
