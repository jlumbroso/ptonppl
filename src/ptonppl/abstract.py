
import copy
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
    _cn: typing.Optional[str] = None

    _original: typing.Optional[typing.Any] = None

    def merge(self, obj: 'AbstractPtonPerson') -> 'AbstractPtonPerson':
        # defensive copy
        self_copy = copy.deepcopy(self)

        # pick best version of attribute
        self_copy._puid = self_copy._puid or obj._puid
        self_copy._netid = self_copy._netid or obj._netid
        self_copy._alias = self_copy._alias or obj._alias
        self_copy._email = self_copy._email or obj._email
        self_copy._pustatus = self_copy._pustatus or obj._pustatus
        self_copy._cn = self_copy._cn or obj._cn

        # update original dict
        if obj._original is not None:
            orig = copy.deepcopy(obj._original)
            if self_copy._original is not None:
                orig.update(self_copy._original)
            self_copy._original = orig

        return self_copy

    @property
    def complete(self):
        return (
                self._puid is not None and
                self._netid is not None and
                self._email is not None
        )

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
    def common_name(self) -> typing.Optional[str]:
        return self._cn

    @property
    def status(self) -> typing.Optional[str]:
        return self._pustatus

    @property
    def has_alias(self) -> bool:
        return self._alias is not None and self._alias != self._netid

    @property
    def original(self) -> typing.Any:
        # defensive copy
        if self._original is not None:
            return copy.deepcopy(self._original)

    @property
    def as_dict(self) -> typing.Dict[str, typing.Any]:
        ret = dict()

        for (name, val) in [
            ("puid", self._puid),
            ("netid", self._netid),
            ("alias", self._alias),
            ("email", self._email),
            ("type", self._pustatus),
            ("name", self._cn),
        ]:
            if val is not None:
                ret[name] = val

        if "alias" in ret and "netid" in ret and ret["alias"] == ret["netid"]:
            del ret["alias"]

        return ret
