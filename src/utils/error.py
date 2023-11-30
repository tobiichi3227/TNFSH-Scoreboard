"""
    @author: tobiichi3227
    @day: 2023/10/25
"""

from typing import Any


class _Error:
    def __str__(self):
        return "E"


Error = _Error()


class _Success(_Error):
    def __str__(self):
        return "S"


Success = _Success()


class _ExistError(_Error):
    def __str__(self):
        return "Eexist"


ExistError = _ExistError()


class _NotExistError(_Error):
    def __str__(self):
        return "Enoext"


NotExistError = _NotExistError()


class _MemberNotFoundError(_Error):
    def __repr__(self):
        return "Emembernoext"


MemberNotFoundError = _MemberNotFoundError()


class _WrongPasswordError(_Error):
    def __str__(self):
        return "Ewrongpw"


WrongPasswordError = _WrongPasswordError()


class _MemberLockedError(_Error):
    def __str__(self):
        return "Elocked"


MemberLockedError = _MemberLockedError()


class _WrongParamError(_Error):
    def __str__(self):
        return "Eparam"


WrongParamError = _WrongParamError()


class _CanNotAccessError(_Error):
    def __str__(self):
        return "Eacces"


CanNotAccessError = _CanNotAccessError()


class _UnknownError(_Error):
    def __str__(self):
        return "Eunk"


UnknownError = _UnknownError

ReturnType = tuple[_Error, Any]
