
import typing
import subprocess

import requests

import ptonppl.abstract
import ptonppl.constants
import ptonppl.ldap


__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"

__all__ = [
]


def _check_uid(s:str) -> typing.Optional[str]:
    if not (s or type(s) is str):
        return None

    s_l = s.lower()
    for c in s_l:
        if not c in ptonppl.constants.ID_AUTHORIZED_CHARS:
            return None

    return s_l


def _parse_ldapsearch_output(out:str) -> typing.Dict[str, typing.Dict[str, str]]:

    if out is None:
        return dict()

    lines = out.split("\n")

    # sentinel to flush
    lines.append("dn: ")

    current_dn = None
    current_record = {}

    identities = {}

    for line in lines:
        if line == "" or line[0] == "#":
            continue

        if ":" in line:
            (field, value) = line.split(":", 1)
            field = field.strip().lower()
            value = value.strip().lower()

            if field == "dn":

                # the last occurrence of "dn" is a sentinel meant to flush
                # the final result

                if current_dn is not None and current_record is not None:
                    key = current_record[ptonppl.constants.PARSED_LDAP_KEY]
                    identities[key] = current_record

                if value:
                    current_dn = value
                    current_record = {}

            elif field:

                if not field in ptonppl.constants.LDAP_IGNORE_FIELDS:

                    if field in current_record:
                        curr = current_record[field]

                        if type(curr) is list:
                            curr.append(value)
                        else:
                            current_record[field] = [curr, value]

                    else:
                        current_record[field] = value

    return identities


def _get_ldapsearch_output_from_proxy_url(
        ldap_field: str,
        ldap_value: str,
        proxy_url: typing.Optional[str] = None,
) -> typing.Optional[str]:

    if proxy_url is None:
        proxy_url = ptonppl.constants.LDAP_DEFAULT_PROXY_URL

    r = requests.get(proxy_url, params={ldap_field: ldap_value})

    if r.ok:
        return r.content.decode("ascii")


def _get_ldapsearch_output_from_local_cmd(
        ldap_field: str,
        ldap_value: str,
        local_cmd: typing.Optional[str] = None,
) -> typing.Optional[str]:

    if local_cmd is None:
        local_cmd = ptonppl.constants.LDAP_DEFAULT_CMD

    cmd = ptonppl.constants.LDAP_CMD_PATTERN.format(
        cmd=local_cmd,
        query="{}={}".format(ldap_field, ldap_value),
    )

    (status, out) = subprocess.getstatusoutput(cmd)

    # If unsuspected problem, check here
    # FIXME: add error correction
    ## TO DEBUG:
    ## print "Content-type: text/plain\n\n", (status, output)
    ## if error 256 may be that the local copy of ldapsearch is outdated

    if status == 0:
        return out


def _get_ldapsearch_output(
        ldap_field: str,
        ldap_value: str,
) -> typing.Optional[typing.Dict[str, str]]:

    local_ret = _parse_ldapsearch_output(
        out=_get_ldapsearch_output_from_local_cmd(
            ldap_field=ldap_field,
            ldap_value=ldap_value,
        )
    )

    url_ret = _parse_ldapsearch_output(
        out=_get_ldapsearch_output_from_proxy_url(
            ldap_field=ldap_field,
            ldap_value=ldap_value,
        )
    )

    obj1 = list(local_ret.values())[0] if len(local_ret) > 0 else None
    obj2 = list(url_ret.values())[0] if len(url_ret) > 0 else None


    if obj1 is None:
        return obj2

    if obj1 is not None and obj2 is not None:
        obj1.update(obj2)

    return obj1


def search_one(
        ldap_field: str,
        ldap_value: str,
) -> typing.Optional[ptonppl.abstract.AbstractPtonPerson]:

    ret = _get_ldapsearch_output(
        ldap_field=ldap_field,
        ldap_value=ldap_value,
    )

    if ret is not None:
        return ptonppl.ldap.LdapPtonPerson(ldap_result=ret)


# #!/usr/bin/python
# import os
# import cgi, cgitb
# cgitb.enable()
#
# ##########################################################################
# # OPERATIONAL PART
#
#
# LDAP_KEY = "uid"
# LDAP_CMD_NETID = ("""./ldapsearch -x -h ldap.princeton.edu -u """ + \
#                   """-b o='Princeton University,c=US' "uid={uid}" """ + \
#                   """universityid cn uid eduPersonAffiliation pustatus ou""")
# LDAP_CMD_PUID = ("""./ldapsearch -x -h ldap.princeton.edu -u """ + \
#                  """-b o='Princeton University,c=US' "universityid={puid}" """ + \
#                  """universityid cn uid eduPersonAffiliation pustatus ou""")
#
# LDAP_IGNORE_FIELDS = ["search", "result"]
#
#
#
# def run_cmd(cmd):
#     (status, output) = commands.getstatusoutput(cmd)
#     # If unsuspected problem, check here
#     # FIXME: add error correction
#     ## TO DEBUG:
#     ## print "Content-type: text/plain\n\n", (status, output)
#     ## if error 256 may be that the local copy of ldapsearch is outdated
#     return output
#
#
#
# def ldap_uid(s):
#     uid = check_uid(s)
#
#     if uid:
#         cmd = LDAP_CMD_NETID.format(uid=uid)
#         output = run_cmd(cmd)
#         ldap_info = parse_ldap(output)
#
#         if uid in ldap_info:
#             return ldap_info[uid]
#
# def ldap_puid(s):
#     puid = check_uid(s)
#
#     if puid:
#         cmd = LDAP_CMD_PUID.format(puid=puid)
#         output = run_cmd(cmd)
#         ldap_info = parse_ldap(output)
#
#         if len(ldap_info.values()) > 0:
#             return ldap_info.values()[0]
#
#
#
# ##########################################################################
# # WEB SERVICE PART
#
# if __name__ == "__main__":
#
#     if 'REQUEST_METHOD' in os.environ:
#
#         import cgi, cgitb
#         cgitb.enable()
#
#         form = cgi.FieldStorage()
#         output = """{}"""
#
#         if form.has_key("netid"):
#             netid = form["netid"].value
#             ldap_info = ldap_uid(netid)
#
#             if ldap_info and "universityid" in ldap_info:
#                 puid = ldap_info["universityid"]
#                 output = """{ "netid" : "%s", "puid" : "%s", "cn": "%s", "type": "%s", "affiliation": "%s" }""" % (
#                     ldap_info["uid"], ldap_info["universityid"], ldap_info["cn"],
#                     ldap_info.get("pustatus", ""),
#                     ldap_info.get("ou", "")
#                     # ", ".join(ldap_info.get("edupersonaffiliation", []))
#                 )
#
#         if form.has_key("puid"):
#             puid = form["puid"].value
#             ldap_info = ldap_puid(puid)
#
#             if ldap_info and "universityid" in ldap_info:
#                 puid = ldap_info["universityid"]
#                 output = """{ "netid" : "%s", "puid" : "%s", "cn": "%s", "type": "%s", "affiliation": "%s" }""" % (
#                     ldap_info["uid"], ldap_info["universityid"], ldap_info["cn"],
#                     ldap_info.get("pustatus", ""),
#                     ldap_info.get("ou", "")
#                     # ", ".join(ldap_info.get("edupersonaffiliation", []))
#                 )
#
#         print "Content-type: text/plain"
#         print ""
#         print output
#
