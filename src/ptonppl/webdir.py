
import typing

import bs4

import ptonppl.constants
import ptonppl.ldap
import ptonppl.requests


__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"

__all__ = [
    "search_one"
]


# Hard-coded constants that are required to scrape the web page

CLASS_RESULTS_BLOCK1 = "people-results"
CLASS_RESULTS_BLOCK2 = "bordered"
CLASS_RESULTS_ROW = "row"
CLASS_RESULTS_DETAILS = "expanded-details-value"


# noinspection PyBroadException
def _fetch_raw_results(url: str) -> typing.Optional[typing.List[bs4.element.Tag]]:

    # not a valid URL
    if url is None or type(url) is not str or len(url) == 0 or "http" not in url:
        return

    # make request
    r = ptonppl.requests.get(url)
    if not r.ok:
        return

    # parse using BeautifulSoup
    s = bs4.BeautifulSoup(r.content, features="html.parser")
    if s is None:
        return

    # try to extract the subtree of results
    try:
        # get the subtree of the DOM containing results
        b = s.find("div", attrs={"class": CLASS_RESULTS_BLOCK1}).find("div", attrs={"class": CLASS_RESULTS_BLOCK2})

        # get individual results
        raw_items = b.find_all("div", attrs={"class": CLASS_RESULTS_ROW})

        # ensure there are least one
        if raw_items is None:
            return

    except:
        return

    return raw_items


def _get_inline_content(
        obj: bs4.element.Tag,
        class_name: str
) -> typing.Optional[str]:
    obj = obj.find(attrs={"class": class_name})
    if obj is None:
        return

    str_value = "".join(obj.stripped_strings) or ""
    str_value = str_value.strip()

    return str_value


def _get_header_content(
        obj: bs4.element.Tag,
        header_name: str
) -> typing.Optional[str]:
    tag_label = obj.find("h4", string=header_name)
    if tag_label is None:
        return

    tag_value = tag_label.find_next_sibling("span", attrs={"class": CLASS_RESULTS_DETAILS})
    if tag_value is None:
        return

    str_value = "".join(tag_value.stripped_strings) or ""
    str_value = str_value.strip()

    return str_value


def _parse_result(obj: bs4.element.Tag) -> typing.Dict[str, typing.Any]:

    r = dict()

    # NOTE: should remove all the hardcoded constants from below perhaps?
    # or move to constants module

    for header_name, field_name in [
        ("NetID", "uid"),
        ("University ID", "universityid"),
        ("Office Location", "street"),
        ("Interoffice Address", "puinterofficeaddress"),
    ]:
        val = _get_header_content(obj=obj, header_name=header_name)
        if val is not None:
            r[field_name] = val

    for class_name, field_name in [
        ("title", "title"),
        ("people-search-email", "mail"),
        ("people-search-result-phone", "telephoneNumber"),
        ("people-search-result-name", "pudisplayname"),
        ("people-search-result-department", "ou"),
    ]:
        val = _get_inline_content(obj=obj, class_name=class_name)
        if val is not None:
            r[field_name] = val

    if "pudisplayname" in r:
        pudn = r.get("pudisplayname")
        last, first = pudn.split(", ")
        r["displayName"] = "{} {}".format(first, last)
        r["givenName"] = first
        r["cn"] = r["displayName"]
        r["sn"] = last

    if "mail" in r and "uid" in r:
        r["eduPersonPrincipalName"] = ptonppl.constants.WEBDIR_EMAIL_FROM_NETID.format(r["uid"])

    return r


def search_one(
        field: str,
        value: str,
) -> typing.Optional[ptonppl.ldap.LdapPtonPerson]:

    if field.lower() in ["mail", "email"]:
        url_pattern = ptonppl.constants.PRINCETON_CAMPUS_DIRECTORY_EMAIL_SEARCH_URL

    elif field.lower() in ["alias"]:
        url_pattern = ptonppl.constants.PRINCETON_CAMPUS_DIRECTORY_EMAIL_SEARCH_URL
        value = ptonppl.constants.WEBDIR_EMAIL_FROM_NETID.format(value)

    elif field.lower() in ["netid"]:
        url_pattern = ptonppl.constants.PRINCETON_CAMPUS_DIRECTORY_NETID_SEARCH_URL

    else:
        raise ValueError(
            "unrecognized field: {}  (choices are 'mail', 'uid')".format(field))

    url = url_pattern.format(value)

    raw_results = _fetch_raw_results(url=url)
    if raw_results is None:
        return

    results = list(map(_parse_result, raw_results))

    if results is not None and len(results) > 0:
        return ptonppl.ldap.LdapPtonPerson(ldap_result=results[0])
