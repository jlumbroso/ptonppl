
import typing


__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"

__all__ = [
    "AbstractPtonPerson",
]


class AbstractPtonPerson:

    _puid: typing.Optional[int] = None
    _netid: typing.Optional[str] = None
    _alias: typing.Optional[str] = None
    _email: typing.Optional[str] = None
    _pustatus: typing.Optional[str] = None

    _original: typing.Optional[typing.Any] = None

    @property
    def puid(self) -> typing.Optional[int]:
        return self._puid

    @property
    def netid(self) -> typing.Optional[str]:
        return self._netid

    @property
    def alias(self) -> typing.Optional[str]:
        return self._alias

    @property
    def email(self) -> typing.Optional[str]:
        return self._email

    @property
    def status(self) -> typing.Optional[str]:
        return self._pustatus

    @property
    def has_alias(self) -> bool:
        return self._alias is not None and self._alias != self._netid

    @property
    def as_dict(self) -> typing.Dict[str, typing.Any]:
        ret = dict()

        for (name, val) in [
            ("puid", self._puid),
            ("netid", self._netid),
            ("alias", self._alias),
            ("email", self._email),
            ("status", self._pustatus),
        ]:
            if val is not None:
                ret[name] = val

        if "alias" in ret and "netid" in ret and ret["alias"] == ret["netid"]:
            del ret["alias"]

        return ret
