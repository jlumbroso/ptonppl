
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
        ]:
            if val is not None:
                ret[name] = val

        return ret
