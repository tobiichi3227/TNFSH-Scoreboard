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


class _WrongPasswordOrAccountError(_Error):
    def __str__(self):
        return "Ewrongpwacct"


WrongPasswordOrAccountError = _WrongPasswordOrAccountError()


class _WrongValidateCodeError(_Error):
    def __str__(self):
        return "Ewrongvalidatecode"


WrongValidateCodeError = _WrongValidateCodeError()


class _WrongTooManyTimesError(_Error):
    def __str__(self):
        return "Ewrongtoomany"


WrongTooManyTimesError = _WrongTooManyTimesError()


class _NeedResetPasswordError(_Error):
    def __str__(self):
        return "Eneedresetpw"


NeedResetPasswordError = _NeedResetPasswordError()


class _WrongParamError(_Error):
    def __str__(self):
        return "Eparam"


class _RemoteServerError(_Error):
    def __str__(self):
        return "Eremote"


RemoteServerError = _RemoteServerError()

WrongParamError = _WrongParamError()


class _UnknownError(_Error):
    def __str__(self):
        return "Eunk"


UnknownError = _UnknownError

ReturnType = tuple[_Error, Any]
